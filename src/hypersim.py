#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal, os
import tkinter as tk
from opcserver import *
from mainwindow import *

def signal_handler(signum, frame):
	exit(0)


signal.signal(signal.SIGINT, signal_handler)
root = tk.Tk()
app = MainWindow(parent=root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
app.mainloop()
