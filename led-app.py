import time
import numpy as np
import sounddevice as sd
import pyaudiowpatch as pyaudio
from functools import partial, Placeholder
import os
import socket
import colorsys
import ledface
import unisystray
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class LEDApp():
	def __init__(self):
		self.stream = None
		self.event = None

		self.server_ip = ("192.168.0.3", 5000)

		self.passtime = -1

		modes = self.getModesInfo()
		devices = self.getDevicesInfo()

		try:
			text = open("play.txt", "r").read()
			text = text.split(",")
			self.play = text[0]
			self.device = int(text[1])
			self.colour = text[2]
			self.brightness = int(text[3])
		except:
			self.play = "On"
			self.device = self.default_device
			self.colour = "228 112 37"
			self.brightness = 50

			self.saveToFile()

		self.getAudio()

		self.tray = unisystray.Tray("images/icon.png", self.on_quit_callback)
		menu = self.tray.createMenu("Tray", False)

		modesMenu = self.tray.createMenu("Modes", True)
		for mode in modes:
			modesMenu.createAction(mode[0], mode[1], mode[0] == self.play)
		menu.addMenu(modesMenu)

		devicesMenu = self.tray.createMenu("Devices", True)
		for device in devices:
			devicesMenu.createAction(device[0], device[1], device[2] == self.device)
		menu.addMenu(devicesMenu)

		menu.createAction("Light Colour", self.lightColour)
		menu.createAction("Brightness", self.brightnessLevel)
		self.tray.addMenu(self.tray, menu)

		self.colourDialog = QColorDialog()
		self.brightnessDialog = QInputDialog()
		self.brightnessDialog.setWindowTitle("Set Brightness")
		self.brightnessDialog.setLabelText("Brightness:")
		self.brightnessDialog.setIntValue(self.brightness)
		self.brightnessDialog.setIntRange(0, 100)

		self.tray.display()

	def getModesInfo(self):
		modes = ()
		for option in ["On", "Off", "Light", "Face"]:
			modes += (option, partial(self.mode, Placeholder, option)),

		return modes

	def getDevicesInfo(self):
		self.pyAudio = pyaudio.PyAudio()
		self.default_device = -1

		audio_devices = ()
		for loopback in self.pyAudio.get_loopback_device_info_generator():
			if (self.default_device == -1):
				self.default_device = loopback["index"]
				
			audio_devices += (loopback["name"].removesuffix("[Loopback]"), partial(self.audioDevice, Placeholder, loopback["index"]), loopback["index"]),

		for device in sd.query_devices():
			if (device["max_input_channels"] == 0 or device["hostapi"] != 2):
				continue

			if (self.default_device == -1):
				self.default_device = device["index"]
			
			audio_devices += (device["name"], partial(self.audioDevice, Placeholder, device["index"]), device["index"]),

		return audio_devices
	
	def volume_to_rgb(self, volume):
		colour = colorsys.hsv_to_rgb(volume / 360, 1, 1)

		r = colour[2] * 255
		g = colour[1] * 255
		b = colour[0] * 255

		return int(r), int(g), int(b)
	
	def audio_callback(self, in_data, frames, time_info, status):

		if (self.play == "Off" or self.passtime > time.time()):
			return (in_data, pyaudio.paContinue)

		self.passtime = time.time() + 0.2
		
		volStr = self.colour

		if (self.play == "On"):
			volume_norm = np.linalg.norm(np.frombuffer(in_data, dtype=np.int16)) ** (1/1.9)
			volume = np.clip(int(volume_norm), 0, 300)

			volTuple = self.volume_to_rgb(volume)

			volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

			if (volume_norm == 0.0):
				return (in_data, pyaudio.paContinue)
		elif (self.play == "Face"):
			volStr = ledface.GetClosestEmotionLED()

		self.server = socket.socket(type=socket.SOCK_DGRAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		volStr += " " + str(self.brightness)

		try:
			self.server.connect(self.server_ip)
			self.server.sendall(volStr.encode("ascii"))
			self.server.close()
		except:
			pass

		return (in_data, pyaudio.paContinue)
	
	def getAudio(self):
		if (self.stream):
			self.stream.close()

		device = self.pyAudio.get_device_info_by_index(self.device)
		self.stream = self.pyAudio.open(format=pyaudio.paInt16, channels=device["maxInputChannels"], rate=int(device["defaultSampleRate"]), frames_per_buffer=512, input=True, input_device_index=device["index"], stream_callback=self.audio_callback)

	def setPlay(self, status):
		self.play = status

		if (status == "Face"):
			ledface.RegisterCamera()
		else:
			ledface.CloseCamera()

		self.saveToFile()

	def setAudio(self, status):
		self.device = status
		self.getAudio()

		self.saveToFile()

	def setColour(self, status):
		self.colour = status

		self.saveToFile()

	def setBrightness(self, status):
		self.brightness = status

		self.saveToFile()

	def saveToFile(self):
		f = open("play.txt", "w")
		f.write(self.play + "," +  str(self.device) + "," + self.colour + "," + str(self.brightness))
		f.close()

	def mode(self, checked, option):
		if (self.play == option):
			return
		
		self.setPlay(option)

	def audioDevice(self, checked, option):
		if (self.device == option):
			return
		
		self.setAudio(option)

	def lightColour(self):
		defaultColour = self.colour.split(" ")
		defaultColour = "#%02x%02x%02x" % (int(defaultColour[0]), int(defaultColour[1]), int(defaultColour[2]))
		self.colourDialog.setCurrentColor(QColor(defaultColour))

		if self.colourDialog.exec():
			colour = self.colourDialog.currentColor()

			rgbStr = "%d %d %d" % (colour.red(), colour.green(), colour.blue())

			if (rgbStr == self.colour):
				return
			
			self.setColour(rgbStr)

	def brightnessLevel(self):
		if self.brightnessDialog.exec():
			self.setBrightness(self.brightnessDialog.intValue())

	def on_quit_callback(self):
		self.stream.close()
		self.tray.quit()

		os._exit(0)

LEDApp()