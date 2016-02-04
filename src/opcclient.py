#!/usr/bin/env python3

"""Python Client library for Open Pixel Control
http://github.com/zestyping/openpixelcontrol

Sends pixel values to an Open Pixel Control server to be displayed.
http://openpixelcontrol.org/

https://github.com/ak15199/rop/blob/master/opc/

Recommended use:

	import opc

	# Create a client object
	client = OPCclient('localhost:7890')

	# Test if it can connect (optional)
	if client.can_connect():
		print('connected to %s' % ADDRESS)
	else:
		# We could exit here, but instead let's just print a warning
		# and then keep trying to send pixels in case the server
		# appears later
		print('WARNING: could not connect to %s' % ADDRESS)

	# Send pixels forever at 30 frames per second
	while True:
		my_pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
		if client.put_pixels(my_pixels, channel=0):
			print('...')
		else:
			print('not connected')
		time.sleep(1/30.0)

"""

import socket, time
import struct
import sys
try:
	import json
except ImportError:
	import simplejson as json


class OPCclient(object):

	# ----------------------------
	def __init__(self, server_ip_port='localhost:7890', long_connection=True, verbose=False):
		"""Create an OPC client object which sends pixels to an OPC server.

		server_ip_port should be an ip:port or hostname:port as a single string.
		For example: '127.0.0.1:7890' or 'localhost:7890'

		There are two connection modes:
		* In long connection mode, we try to maintain a single long-lived
		  connection to the server.  If that connection is lost we will try to
		  create a new one whenever put_pixels is called.  This mode is best
		  when there's high latency or very high framerates.
		* In short connection mode, we open a connection when it's needed and
		  close it immediately after.  This means creating a connection for each
		  call to put_pixels. Keeping the connection usually closed makes it
		  possible for others to also connect to the server.

		A connection is not established during __init__.  To check if a
		connection will succeed, use can_connect().

		If verbose is True, the client will print debugging info to the console.

		"""
		self.verbose = verbose

		self._long_connection = long_connection

		self._ip, self._port = server_ip_port.split(':')
		self._port = int(self._port)

		self._socket = None  # will be None when we're not connected

		self.noDither = False
		self.noInterp = False
		self.manualLED = False
		self.ledOnOff = False

	# ----------------------------
	def _debug(self, m):
		if self.verbose:
			print('	%s' % str(m))

	# ----------------------------
	def _ensure_connected(self):
		"""Set up a connection if one doesn't already exist.

		Return True on success or False on failure.

		"""
		if self._socket:
			self._debug('_ensure_connected: already connected, doing nothing')
			return True

		try:
			self._debug('_ensure_connected: trying to connect...')
			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._socket.connect((self._ip, self._port))
			self._debug('_ensure_connected:	...success')
			return True
		except socket.error:
			self._debug('_ensure_connected:	...failure')
			self._socket = None
			return False

	# ----------------------------
	def disconnect(self):
		"""Drop the connection to the server, if there is one."""
		self._debug('disconnecting')
		if self._socket:
			self._socket.close()
		self._socket = None

	# ----------------------------
	def can_connect(self):
		"""Try to connect to the server.

		Return True on success or False on failure.

		If in long connection mode, this connection will be kept and re-used for
		subsequent put_pixels calls.

		"""
		success = self._ensure_connected()
		if not self._long_connection:
			self.disconnect()
		return success

	# ----------------------------
	def send(self, packet):
		self._debug('put_pixels: sending pixels to server')
		try:
			self._socket.send(packet)
		except socket.error:
			self._debug('put_pixels: connection lost.  could not send pixels.')
			self._socket = None
			return False
	
		if not self._long_connection:
			self._debug('put_pixels: disconnecting')
			self.disconnect()

	# ----------------------------
	def put_pixels(self, pixels, channel=0):
		"""Send the list of pixel colors to the OPC server on the given channel.

		channel: Which strand of lights to send the pixel colors to.
			Must be an int in the range 0-255 inclusive.
			0 is a special value which means "all channels".

		pixels: A list of 3-tuples representing rgb colors.
			Each value in the tuple should be in the range 0-255 inclusive. 
			For example: [(255, 255, 255), (0, 0, 0), (127, 0, 0)]
			Floats will be rounded down to integers.
			Values outside the legal range will be clamped.

		Will establish a connection to the server as needed.

		On successful transmission of pixels, return True.
		On failure (bad connection), return False.

		The list of pixel colors will be applied to the LED string starting
		with the first LED.  It's not possible to send a color just to one
		LED at a time (unless it's the first one).

		"""
		self._debug('put_pixels: connecting')
		is_connected = self._ensure_connected()
		if not is_connected:
			self._debug('put_pixels: not connected.  ignoring these pixels.')
			return False

		# build OPC message
		len_hi_byte = int(len(pixels)*3 / 256)
		len_lo_byte = (len(pixels)*3) % 256
		command = 0  # set pixel colors from openpixelcontrol.org

		header = struct.pack("BBBB", channel, command, len_hi_byte, len_lo_byte)
		pieces = [ struct.pack( "BBB",
					 min(255, max(0, int(r))),
					 min(255, max(0, int(g))),
					 min(255, max(0, int(b)))) for r, g, b in pixels ]

		self.send( header + b''.join(pieces) )

		return True


	# ----------------------------
	def sysEx(self, systemId, commandId, msg):
		is_connected = self._ensure_connected()
		if not is_connected:
			return False

		header = struct.pack(">BBHHH", 0, 0xFF, len(msg) + 4, systemId, commandId)
		self.send(header + msg)

	# ----------------------------
	def setGlobalColorCorrection(self, gamma, r, g, b):
		data = json.dumps({'gamma': gamma, 'whitepoint': [r, g, b]})
		self.sysEx(1, 1, data.encode('utf-8'))

	# ----------------------------
	def setFirmwareConfig(self,noDither=None,noInterp=None,manualLED=None,ledOnOff=None):
		if noDither  is not None: self.noDither  = noDither
		if noInterp  is not None: self.noInterp  = noInterp
		if manualLED is not None: self.manualLED = manualLED
		if ledOnOff  is not None: self.ledOnOff  = ledOnOff
		
		data = chr(self.noDither | (self.noInterp << 1) | (self.manualLED << 2) | (self.ledOnOff << 3) )
		self.sysEx(1, 2, struct.pack("s",data.encode('utf-8')))

	# ----------------------------
	def terminate(self):
		pass


if __name__ == "__main__":
	import colorsys
	opc = OPCclient()
	
	opc.setFirmwareConfig(noDither=False,noInterp=True,manualLED=True,ledOnOff=False)
		
	ledCount = 64
	ledData = ledCount * [(0,0,0)]
	saturation = 1.0
	brightness = 1.0
	rotationTime = 3
	
	increment = 3
	sleepTime = rotationTime / ledCount
	while sleepTime < 0.05:
		increment *= 2
		sleepTime *= 2
	increment %= ledCount
	increment = -increment
	
	for i in range(ledCount):
		hue = float(i)/ledCount
		rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
		ledData[i] =(int(255*rgb[0]), int(255*rgb[1]), int(255*rgb[2]))

	opc.put_pixels(ledData)
	opc.setGlobalColorCorrection(2.5, 10, 10, 10)


	try:
		while True:
			opc.put_pixels(ledData)
			ledData = ledData[-increment:] + ledData[:-increment]
			time.sleep(sleepTime)
	except:
		print()
	
	