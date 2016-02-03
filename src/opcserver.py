# -*- coding: utf-8 -*-

import socketserver, socket
from threading import Thread

class OPCserver(Thread):
	update_func = None
	running = False

	# ======================================================
	class OPCHandler(socketserver.BaseRequestHandler):

		# ------------------------------------------------------
		def setup(self):
			self.request.settimeout(3)

		# ------------------------------------------------------
		def handle(self):
			while OPCserver.running:
				try:
					# recv header
					data = self.request.recv(4).strip()
					if not data or not OPCserver.running: break
					channel, cmd, hi, lo = data[:4]
					length = hi*256 + lo

					# recv data
					data = self.request.recv(length)
					if not data or not OPCserver.running or cmd != 0: break
				except socket.timeout:
					break

				# process data
				if OPCserver.update_func is not None and len(data) >= 3:
					led_data = []
					for n in range(0,len(data),3):
						led_data.append( (data[n], data[n+1], data[n+2]) )
					OPCserver.update_func(led_data)

	# ======================================================

	# ------------------------------------------------------
	def __init__(self, func=None, HOST='0.0.0.0', PORT=7890):
		Thread.__init__(self)
		OPCserver.update_func = func
		self.server = socketserver.TCPServer((HOST, PORT), OPCserver.OPCHandler, False)
		self.server.allow_reuse_address = True
		self.server.socket.settimeout(3)
		self.server.server_bind()

	# ------------------------------------------------------
	def __del__(self):
		self.stop()

	# ------------------------------------------------------
	def run(self):
		OPCserver.running = True
		self.server.server_activate()
		self.server.serve_forever()

	# ------------------------------------------------------
	def stop(self):
		OPCserver.running = False
		self.server.shutdown()
		self.server.server_close()
