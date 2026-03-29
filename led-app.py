import sched, time
import numpy as np
import math
import sounddevice as sd
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

def audio_callback(indata, frames, time, status):
	global PLAY
	global PASSTIME
	global SERVER
	global SERVER_IP

	if (PLAY == "Off" or PASSTIME > time.currentTime):
		return

	PASSTIME = time.currentTime + 0.2
	
	volStr = "228 112 37"

	if (PLAY == "On"):
		volume_norm = np.linalg.norm(indata) ** 3
		volume = np.clip(int(volume_norm), 0, 300)

		volTuple = volume_to_rgb(volume)

		volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

		if (volume_norm == 0.0):
			return
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
	
def getAudio(timer):
	timer.enter(86400, 1, getAudio, (timer, ))

	with sd.InputStream(device="Voicemeeter Out B1 (VB-Audio Voicemeeter VAIO), Windows WASAPI", channels=2, callback=audio_callback):
		sd.sleep(86400000)

def setPlay(status):
	global PLAY

	PLAY = status
	if (status == "Face"):
		ledface.RegisterCamera()
	else:
		ledface.CloseCamera()

	f = open("play.txt", "w")
	f.write(PLAY)
	f.close()

def mode(systray, option):
	global PLAY

	if (PLAY == option):
		return
	
	setPlay(option)

def on_quit_callback(systray):
	SERVER.shutdown(socket.SHUT_RDWR)
	SERVER.close()

	os._exit(1)
    
modes = ()
for option in ["On", "Off", "Light", "Face"]:
	modes += ((option, None, partial(mode, Placeholder, option)),)

menu_options = (("Music Mode", None, modes),)
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

timer = sched.scheduler(time.time, time.sleep)
PLAY = open("play.txt", "r").read()

SERVER_IP = ("192.168.0.3", 5000)

PASSTIME = -1

timer.enter(0, 1, getAudio, (timer, ))
timer.run()