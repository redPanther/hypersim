# -*- coding: utf-8 -*-

import socketserver, socket, json
from threading import Thread, Lock

class OPCserver(Thread):
	update_func = None
	running = False
	_standby = False
	_lock = Lock()

	# ======================================================
	class OPCHandler(socketserver.BaseRequestHandler):

		# ------------------------------------------------------
		def setup(self):
			self.request.settimeout(10)

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
					if not data or not OPCserver.running: break
				except socket.timeout:
					break

				# process data
				with OPCserver._lock:
					if cmd == 0:
						if OPCserver.update_func is not None and len(data) >= 3:
							led_data = []
							for n in range(0,len(data),3):
								led_data.append( (data[n], data[n+1], data[n+2]) )
							OPCserver.update_func(led_data)
						
					elif cmd == 0xff:
						sysex_cmd = 0
						sysex_id = 0
						if len(data) > 3:
							sysex_id  = data[0]*256+data[1]
							sysex_cmd = data[2]*256+data[3]
							data = data[4:]
					
						if sysex_id == 1: # color correction commands
							data = data.decode('utf-8')
							print("sysEx [device: fadecandy command: %s] %s" % (sysex_cmd, data) )
							if sysex_cmd == 1 and OPCserver.color_func is not None:
								try:
									json_data = json.loads(data)
									if not OPCserver._standby:
										OPCserver.color_func(json_data['gamma'],json_data['whitepoint'])
								except:
									print("  error reading json string")
						
							elif sysex_cmd == 2: # firmware commands
								if len(data) > 0:
									#data[0]
									pass
							
							elif sysex_cmd > 2:
								print("unknown fadecandy sysEx command")
							
						else:
							print("sysEx [device: %s command: %s] %s", (sysex_id, sysex_cmd, data) )
					else:
						print("unknown command", cmd, data)

	# ======================================================

	# ------------------------------------------------------
	def __init__(self, upd_func=None, col_func=None, HOST='0.0.0.0', PORT=7890):
		Thread.__init__(self)
		OPCserver.update_func = upd_func
		OPCserver.color_func = col_func
		self.server = socketserver.TCPServer((HOST, int(PORT)), OPCserver.OPCHandler, False)
		self.server.allow_reuse_address = True
		self.server.socket.settimeout(3)
		self.server.server_bind()
		print("opc server bind on %s %i" %(HOST,PORT) )

	# ------------------------------------------------------
	def __del__(self):
		self.stop()

	def standby(self,enable):
		try:
			if enable: OPCserver._lock.acquire(True,3)
			else     : OPCserver._lock.release()
		except:
			print("locking error")
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
