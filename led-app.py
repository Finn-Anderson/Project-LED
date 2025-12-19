import sched, time
import numpy as np
import math
import sounddevice as sd
from infi.systray import SysTrayIcon
import os
import socket
import colorsys

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
	global COUNT

	if (PLAY == "False" or PASSTIME > time.currentTime):
		return

	PASSTIME = time.currentTime + 0.2
	
	volStr = "228 112 37"

	if (PLAY == "True"):
		volume_norm = np.linalg.norm(indata) ** 3
		volume = np.clip(int(volume_norm), 0, 300)

		volTuple = volume_to_rgb(volume)

		volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

		if (volume_norm == 0.0):
			return

	SERVER.sendto(volStr.encode("ascii"), SERVER_IP)
	
def getAudio(timer):
	timer.enter(86400, 1, getAudio, (timer, ))

	with sd.InputStream(device="Voicemeeter Out B1 (VB-Audio Voicemeeter VAIO), Windows WASAPI", channels=2, callback=audio_callback):
		sd.sleep(86400000)

def setPlay(status):
	global PLAY

	PLAY = status

	f = open("play.txt", "w")
	f.write(PLAY)
	f.close()

def on(systray):
	global PLAY

	if (PLAY == "True"):
		return
	
	setPlay("True")

def off(systray):
	global PLAY

	if (PLAY == "False"):
		return

	setPlay("False")

def light(systray):
	global PLAY

	if (PLAY == "Light"):
		return
	
	setPlay("Light")

def on_quit_callback(systray):
	SERVER.close()

	os._exit(1)
    
menu_options = (("Music Mode", None, (("On", None, on), ("Off", None, off), ("Light", None, light),)),)
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

timer = sched.scheduler(time.time, time.sleep)
PLAY = open("play.txt", "r").read()

SERVER_IP = ("192.168.50.9", 5000)

SERVER = socket.socket(type=socket.SOCK_DGRAM)

PASSTIME = -1
COUNT = 20

timer.enter(0, 1, getAudio, (timer, ))
timer.run()