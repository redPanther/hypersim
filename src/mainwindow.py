# -*- coding: utf-8 -*-

import json, re, time, argparse, signal, os
import tkinter as tk

import tkinter.messagebox as tkMessageBox
import tkinter.simpledialog as tkSimpleDialog
import tkinter.filedialog as tkFileDialog
import tkinter.simpledialog as tkSimpleDialog

from opcserver import *

class MainWindow(tk.Frame):

	# ------------------------------------------------------
	def __init__(self, parent=None):
		self.parent = parent
		self.layout_file = None
		self.parseCmdArgs()
		if self.layout_file is None:
			self.resetVars()
			self.initUI()
		else:
			self.loadConfig()

		self.opcServer = OPCserver(self.updateLeds)
		self.opcServer.start()

		for idx in range(len(self.led_widgets)):
			self.setLedColor(idx,100,200,100)

	def resetVars(self):
		self.win_width = 800
		self.win_height = 600
		self.led_rects = []
		self.canvas = None
		self.led_widgets = []
		self.led_rects = []

	def loadConfig(self):
		self.resetVars()
		self.readConfig(self.layout_file ,self.layout_type)
		if self.canvas is not None:
			self.canvas.destroy()
		self.initUI()

	def menu_open_hyperion(self):
		filename = tkFileDialog.askopenfilename()
		if filename:
			self.layout_file = filename
			self.layout_type = "hyperion"
			self.loadConfig()

	def menu_open_opc(self,layout_type):
		filename = tkFileDialog.askopenfilename()
		if filename:
			self.layout_file = filename
			self.layout_type = layout_type
			self.loadConfig()

	def menu_open_opc_xy(self):
		self.menu_open_opc("opc_xy")

	def menu_open_opc_xz(self):
		self.menu_open_opc("opc_xz")

	def menu_open_opc_yz(self):
		self.menu_open_opc("opc_yz")

	# ------------------------------------------------------
	def initUI(self):
		self.parent.title("HyperSim");
		tk.Frame.__init__(self, self.parent)
		self.pack()

		menubar = tk.Menu(self)

		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Open Hyperion", command=self.menu_open_hyperion)
		filemenu.add_command(label="Open OPC xy",      command=self.menu_open_opc_xy)
		filemenu.add_command(label="Open OPC xz",      command=self.menu_open_opc_xz)
		filemenu.add_command(label="Open OPC yz",      command=self.menu_open_opc_yz)
		filemenu.add_separator()
		filemenu.add_command(label="Quit",          command=self.on_close)
		menubar.add_cascade(label="File", menu=filemenu)
		self.parent.config(menu=menubar)

		frameC = tk.Frame(master=self)
		frameC.pack()
		self.canvas = tk.Canvas(frameC, width=self.win_width, height=self.win_height)
		self.canvas.pack()
		self.canvas.create_rectangle(0, 0, self.win_width, self.win_height, fill="darkgray", outline="darkgray")

		for idx, r in enumerate(self.led_rects):
			self.led_widgets.append(self.canvas.create_rectangle(r[0], r[1], r[2], r[3], fill="black", outline="darkgray"))
			if self.show_numbers:
				self.canvas.create_text( int((r[0]+r[2])/2), int((r[1]+r[3])/2), anchor=tk.W, text=str(idx))

	# ------------------------------------------------------
	def parseCmdArgs(self):
		parser = argparse.ArgumentParser(description='Simulator for hyperion.', prog='hypersim')
		group = parser.add_mutually_exclusive_group()
		parser.add_argument('-n','--num', dest='show_numbers', action='store_true', help='show led IDs')
		group.add_argument('--hyperion', dest='hyperion', metavar="<file>", default=None, help='hyperion config')
		group.add_argument('--opc_xy', default=None, metavar="<file>", help='opc config xy components')
		group.add_argument('--opc_yz', default=None, metavar="<file>", help='opc config yz components')
		group.add_argument('--opc_xz', default=None, metavar="<file>", help='opc config xz components')

		args = parser.parse_args()
		self.show_numbers = args.show_numbers

		if args.hyperion is not None:
			self.layout_file = os.path.realpath( args.hyperion )
			self.layout_type = "hyperion"
			if not os.path.exists(self.layout_file):
				print("could not read ", self.layout_file)
				exit(1)

		for k in args.__dict__:
			if k in ['opc_xy','opc_yz','opc_xz'] and args.__dict__[k] is not None:
				self.layout_file = os.path.realpath( args.__dict__[k] )
				self.layout_type = k
				if not os.path.exists(self.layout_file):
					print("could not read ", self.layout_file)
					exit(1)
				break

	# ------------------------------------------------------
	def on_close(self):
		self.opcServer.stop()
		self.opcServer.join()
		self.parent.destroy()

	# ------------------------------------------------------
	def readConfig_hyperion(self,layout_file):
		with open(layout_file) as data_file:
			data = ""
			cfg_data = data_file.read()
			for line in cfg_data.splitlines():
				data += line.split('//')[0]
			hyperion_cfg = json.loads(data)

			for led in hyperion_cfg['leds']:
				self.led_rects.append([
					int(led['hscan']['minimum'] * self.win_width),
					int(led['vscan']['minimum'] * self.win_height),
					int(led['hscan']['maximum'] * self.win_width),
					int(led['vscan']['maximum'] * self.win_height)
				])

	# ------------------------------------------------------
	def readConfig_opc(self,layout_file,a_val_idx,b_val_idx):
		a_values = []
		b_values = []
		with open(layout_file) as data_file:
			opc_cfg = json.load(data_file)
			#print(opc_cfg)
			for d in opc_cfg:
				a_values.append(d['point'][a_val_idx])
				b_values.append(d['point'][b_val_idx])

			a_values_max = max(a_values)
			a_values_min = min(a_values)
			b_values_max = max(b_values)
			b_values_min = min(b_values)

			# calc ratio
			#print( abs(b_values_max - b_values_min) / abs(a_values_max - a_values_min),  a_values_max - a_values_min )

			self.win_height = 800
			while True:
				self.win_height = self.win_width * (abs(b_values_max - b_values_min) / abs(a_values_max - a_values_min))
				if self.win_height < 800:
					break
				else:
					self.win_width -= 10

			norm_a = lambda x: (x - a_values_min) / (a_values_max - a_values_min);
			norm_b = lambda x: (x - b_values_min) / (b_values_max - b_values_min);

			for idx in range(len(a_values)):
				self.led_rects.append([
					int(norm_a(a_values[idx]) * (self.win_width-30)+5),
					int(norm_a(b_values[idx]) * (self.win_height-30)+5),
					int(norm_a(a_values[idx]) * (self.win_width-30)+20),
					int(norm_a(b_values[idx]) * (self.win_height-30)+20)
				])

	# ------------------------------------------------------
	def readConfig(self,layout_file, layout_type="hyperion"):
			opc_map = {'opc_xy' : (0,1),'opc_xz' : (0,2),'opc_yz' : (1,2) }
			
			if layout_type == "hyperion":
				self.readConfig_hyperion(layout_file)
			elif layout_type in opc_map:
				self.readConfig_opc(layout_file, opc_map[layout_type][0], opc_map[layout_type][0])
			else:
				print("unknown type of config file")
				exit(1)

	# ------------------------------------------------------
	def updateLeds(self, led_data):
		for idx in range(len(led_data)):
			self.setLedColor(idx,led_data[idx][0],led_data[idx][1],led_data[idx][2])

	# ------------------------------------------------------
	def setLedColor(self,led_idx,r,g,b):
		if led_idx < len(self.led_widgets):
			self.canvas.itemconfigure(self.led_widgets[led_idx], fill="#%02x%02x%02x" % (r, g, b) )
