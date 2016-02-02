import socket
from threading import Thread

class OPCserver(Thread):

	def __init__(self, func=None):
		Thread.__init__(self)
		self.running = False
		self.update_func = func

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.s.bind(('0.0.0.0', 7890))
		self.s.listen(1)
		self.led_data = []

	def __del__(self):
		self.stop()

	def run(self):
		self.running = True
		print("start")
		while self.running:
				conn, addr = self.s.accept()
				idx = 0
				channel = 0
				cmd     = 0
				length  = 0
				led_idx = 0
				print("reset")
				while self.running:
					data = conn.recv(4)
					if not data: break
					channel, cmd, hi, lo = data[:4]
					length = hi*256 + lo

					data = conn.recv(length)
					if not data: break
					self.led_data = []
					for n in range(0,len(data),3):
						self.led_data.append( (data[n], data[n+1], data[n+2]) )
					if self.update_func is not None:
						self.update_func(self.led_data)
				conn.close()

	def stop(self):
		print("stop")
		self.running = False
		self.s.close()
		exit(0)
		
