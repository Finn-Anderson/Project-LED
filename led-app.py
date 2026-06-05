import time
import numpy as np
import sounddevice as sd
from functools import partial, Placeholder
import sys
import os
if os.name == 'nt':
	import pyaudiowpatch as pyaudio
else:
	import pyaudio
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

		self.passtime = -1
		self.passVolume = 0

		modes = self.getModesInfo()
		devices = self.getDevicesInfo()
		self.device = self.default_device

		try:
			text = open("play.txt", "r").read()
			text = text.split(",")
			self.play = text[0]
			if (self.play == "Face"):
				ledface.RegisterCamera()
			for device in devices:
				if (device[2] == int(text[1])):
					self.device = int(text[1])
					break
			self.colour = text[2]
			self.defaultTimer = int(text[3])
			self.brightness = int(text[4])
			self.server_ip = (text[5], 5000)
		except:
			self.play = "On"
			self.colour = "228 112 37"
			self.defaultTimer = 3
			self.brightness = 50
			self.server_ip = ("192.168.0.3", 5000)

			self.saveToFile()

		self.getAudio()

		if getattr(sys, "frozen", False):
			path = os.path.join(sys._MEIPASS, "images/icon.png")
		else:
			path = "images/icon.png"

		self.tray = unisystray.Tray(path, self.on_quit_callback)
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
		menu.createAction("Default Timer", self.timerSeconds)
		menu.createAction("Brightness", self.brightnessLevel)
		menu.createAction("IP Address", self.ipAddress)
		self.tray.addMenu(self.tray, menu)

		self.colourDialog = QColorDialog()

		self.timerDialog = QInputDialog()
		self.timerDialog.setWindowTitle("Set Default Light Timer")
		self.timerDialog.setLabelText("Seconds before no music on music mode switches to light mode:")
		self.timerDialog.setIntValue(self.defaultTimer)

		self.brightnessDialog = QInputDialog()
		self.brightnessDialog.setWindowTitle("Set Brightness")
		self.brightnessDialog.setLabelText("Brightness:")
		self.brightnessDialog.setIntValue(self.brightness)
		self.brightnessDialog.setIntRange(0, 100)

		self.ipDialog = QInputDialog()
		self.ipDialog.setWindowTitle("Set IP Address")
		self.ipDialog.setLabelText("IP Address:")
		self.ipDialog.setTextValue(self.server_ip[0])

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
		if os.name == 'nt':
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

			if (volume < 100):
				self.passVolume += 0.2
			else:
				self.passVolume = 0

			if (self.passVolume <= self.defaultTimer):
				volTuple = self.volume_to_rgb(volume)

				volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])
		elif (self.play == "Face"):
			volStr = ledface.GetClosestEmotionLED(volStr)

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

	def setDefaultTimer(self, status):
		self.defaultTimer = status

		self.saveToFile()

	def setBrightness(self, status):
		self.brightness = status

		self.saveToFile()

	def setIP(self, status):
		self.server_ip = (status, 5000)

		self.saveToFile()

	def saveToFile(self):
		f = open("play.txt", "w")
		f.write(self.play + "," +  str(self.device) + "," + self.colour + "," + str(self.defaultTimer) + "," + str(self.brightness) + "," + self.server_ip[0])
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

	def timerSeconds(self):
		if self.timerDialog.exec():
			self.setDefaultTimer(self.timerDialog.intValue())

	def brightnessLevel(self):
		if self.brightnessDialog.exec():
			self.setBrightness(self.brightnessDialog.intValue())

	def ipAddress(self):
		if self.ipDialog.exec():
			self.setIP(self.ipDialog.textValue())

	def on_quit_callback(self):
		self.stream.close()
		self.tray.quit()

		os._exit(0)

LEDApp()