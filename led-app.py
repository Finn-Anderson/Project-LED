import time
import numpy as np
import sounddevice as sd
import pyaudiowpatch as pyaudio
from infi.systray import SysTrayIcon
from functools import partial, Placeholder
import os
import socket
import colorsys
import ledface
from tkinter import colorchooser
import tkinter as tk

root = tk.Tk()
root.title("Set Brightness")
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
w = 200
h = 48
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry("%dx%d+%d+%d" % (w, h, x, y))

def setBrightness(entry):
	global BRIGHTNESS

	try:
		value = int(np.round(float(entry.get().strip())))
		value = np.clip(value, 0, 100)
	except:
		value = ""

	b = str(value)
	entry_text.set(b)

	if (value != ""):
		BRIGHTNESS = b

entry_text = tk.StringVar()
entry_text.set("")
entry = tk.Entry(root, textvariable=entry_text)
entry.pack()
entry.bind('<KeyRelease>', lambda e: setBrightness(e.widget))

root.withdraw()

def volume_to_rgb(volume):
	colour = colorsys.hsv_to_rgb(volume / 360, 1, 1)

	r = colour[2] * 255
	g = colour[1] * 255
	b = colour[0] * 255

	return int(r), int(g), int(b)

def audio_callback(in_data, frames, time_info, status):
	global PLAY
	global PASSTIME
	global SERVER
	global SERVER_IP
	global COLOUR
	global BRIGHTNESS

	if (PLAY == "Off" or PASSTIME > time.time()):
		return (in_data, pyaudio.paContinue)

	PASSTIME = time.time() + 0.2
	
	volStr = COLOUR

	if (PLAY == "On"):
		volume_norm = np.linalg.norm(np.frombuffer(in_data, dtype=np.int16)) ** (1/1.9)
		volume = np.clip(int(volume_norm), 0, 300)

		volTuple = volume_to_rgb(volume)

		volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

		if (volume_norm == 0.0):
			return (in_data, pyaudio.paContinue)
	elif (PLAY == "Face"):
		volStr = ledface.GetClosestEmotionLED()

	SERVER = socket.socket(type=socket.SOCK_DGRAM)
	SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	volStr += " " + BRIGHTNESS

	try:
		SERVER.connect(SERVER_IP)
		SERVER.sendall(volStr.encode("ascii"))
		SERVER.close()
	except:
		pass

	return (in_data, pyaudio.paContinue)
	
def getAudio():
	global P
	global DEVICE
	global STREAM

	if (STREAM):
		STREAM.close()

	device = P.get_device_info_by_index(DEVICE)
	STREAM = P.open(format=pyaudio.paInt16, channels=device["maxInputChannels"], rate=int(device["defaultSampleRate"]), frames_per_buffer=512, input=True, input_device_index=device["index"], stream_callback=audio_callback)

async def test():
	await getAudio()

def setPlay(status):
	global PLAY

	PLAY = status
	if (status == "Face"):
		ledface.RegisterCamera()
	else:
		ledface.CloseCamera()

	saveToFile()

def setAudio(status):
	global DEVICE

	DEVICE = status
	getAudio()

	saveToFile()

def setColour(status):
	global COLOUR

	COLOUR = status

	saveToFile()

def saveToFile():
	global PLAY
	global DEVICE
	global COLOUR

	f = open("play.txt", "w")
	f.write(PLAY + "," +  str(DEVICE) + "," + COLOUR)
	f.close()

def mode(systray, option):
	global PLAY

	if (PLAY == option):
		return
	
	setPlay(option)

def audioDevice(systray, option):
	global DEVICE

	if (DEVICE == option):
		return
	
	setAudio(option)

def lightColour(systray):
	global COLOUR
	defaultColour = COLOUR.split(" ")
	color_code = colorchooser.askcolor(title="Choose color", color=(int(defaultColour[0]), int(defaultColour[1]), int(defaultColour[2])))
	
	if (color_code[0] == None):
		return
	
	rgb = color_code[0]
	rgbStr = str(rgb[0]) + " " + str(rgb[1]) + " " + str(rgb[2])
	
	if (COLOUR == rgbStr):
		return
	
	setColour(rgbStr)

def brightness(systray):
	global BRIGHTNESS
	entry_text.set(str(BRIGHTNESS))
	root.deiconify()

def on_quit_callback(systray):
	SERVER.shutdown(socket.SHUT_RDWR)
	SERVER.close()

	os._exit(1)

P = pyaudio.PyAudio()
default_device = -1
audio_devices = ()
for loopback in P.get_loopback_device_info_generator():
	if (default_device == -1):
		default_device = loopback["index"]
		
	audio_devices += ((loopback["name"].removesuffix("[Loopback]"), None, partial(audioDevice, Placeholder, loopback["index"])),)

for device in sd.query_devices():
	if (device["max_input_channels"] == 0 or device["hostapi"] != 2):
		continue

	if (default_device == -1):
		default_device = device["index"]
	
	audio_devices += ((device["name"], None, partial(audioDevice, Placeholder, device["index"])),)
		
modes = ()
for option in ["On", "Off", "Light", "Face"]:
	modes += ((option, None, partial(mode, Placeholder, option)),)

menu_options = (("Music Mode", None, modes), ("Input Device", None, audio_devices), ("Light Colour", None, lightColour), ("Brightness", None, brightness))
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

try:
	text = open("play.txt", "r").read()
	text = text.split(",")
	PLAY = text[0]
	DEVICE = int(text[1])
	COLOUR = text[2]
except:
	PLAY = "On"
	DEVICE = default_device
	COLOUR = "228 112 37"

STREAM = None
EVENT = None

SERVER_IP = ("192.168.0.3", 5000)

PASSTIME = -1
BRIGHTNESS = "60"

setColour(COLOUR)
setPlay(PLAY)
setAudio(DEVICE)
root.mainloop()