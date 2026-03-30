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

	if (PLAY == "Off" or PASSTIME > time.time()):
		return (in_data, pyaudio.paContinue)

	PASSTIME = time.time() + 0.2
	
	volStr = "228 112 37"

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

def saveToFile():
	global PLAY
	global DEVICE

	f = open("play.txt", "w")
	f.write(PLAY + "," +  str(DEVICE))
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

menu_options = (("Music Mode", None, modes),("Input Device", None, audio_devices))
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

try:
	text = open("play.txt", "r").read()
	text = text.split(",")
	PLAY = text[0]
	DEVICE = int(text[1])
except:
	PLAY = "On"
	DEVICE = default_device

STREAM = None
EVENT = None

SERVER_IP = ("192.168.0.3", 5000)

PASSTIME = -1

setPlay(PLAY)
setAudio(DEVICE)