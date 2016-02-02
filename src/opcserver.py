import socketserver
from threading import Thread

class OPCserver(Thread):
	update_func = None
	running = False

	class OPCHandler(socketserver.BaseRequestHandler):
		def handle(self):
			while OPCserver.running:
				data = self.request.recv(4).strip()
				if not data or not OPCserver.running: break
				channel, cmd, hi, lo = data[:4]
				length = hi*256 + lo
				data = self.request.recv(length)
				if not data or not OPCserver.running: break
				self.led_data = []
				for n in range(0,len(data),3):
					self.led_data.append( (data[n], data[n+1], data[n+2]) )
				if OPCserver.update_func is not None:
					OPCserver.update_func(self.led_data)


	def __init__(self, func=None, HOST='0.0.0.0', PORT=7890):
		Thread.__init__(self)
		OPCserver.update_func = func
		self.server = socketserver.TCPServer((HOST, PORT), OPCserver.OPCHandler)
		self.server.allow_reuse_address = True

	def __del__(self):
		self.stop()

	def run(self):
		OPCserver.running = True
		self.server.serve_forever()

	def stop(self):
		OPCserver.running = False
		self.server.shutdown()
		self.server.server_close()
