import sched, time
import numpy as np
import math
import sounddevice as sd
from infi.systray import SysTrayIcon
import os
import socket
import colorsys

COUNT = 0
START_UP = 1

def volume_to_rgb(volume):
	colour = colorsys.hsv_to_rgb(volume / 360, 1, 1)

	r = colour[2] * 255
	g = colour[1] * 255
	b = colour[0] * 255

	return int(r), int(g), int(b)

def audio_callback(indata, frames, time, status):
	global play
	global passTime
	global s
	global SERVER_IP
	global COUNT
	global START_UP

	if (play == "False" or passTime > time.currentTime):
		return

	volume_norm = np.linalg.norm(indata) ** 2.5
	volume = np.clip(int(volume_norm), 0, 300)

	volTuple = volume_to_rgb(volume)

	volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

	passTime = time.currentTime + 0.2

	if (volume == 0):
		COUNT = COUNT + 1	
	else:
		COUNT = 0

	if (COUNT >= 20 or (volume == 0 and START_UP == 1)):
		return
	
	START_UP = 0

	s.sendto(volStr.encode("ascii"), SERVER_IP)
	
def getAudio(timer):
	timer.enter(86400, 1, getAudio, (timer, ))

	with sd.InputStream(device="Voicemeeter Out B1 (VB-Audio Voicemeeter VAIO), Windows WASAPI", channels=2, callback=audio_callback):
		sd.sleep(86400000)

def setPlay(bool):
	global play

	play = bool

	f = open("play.txt", "w")
	f.write(play)
	f.close()

def on(systray):
	if (play == "True"):
		return
	
	setPlay("True")

def off(systray):
	global SERVER_IP

	if (play == "False"):
		return

	setPlay("False")

def on_quit_callback(systray):
	s.close()

	os._exit(1)
    
menu_options = (("Music Mode", None, (("On", None, on), ("Off", None, off),)),)
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

timer = sched.scheduler(time.time, time.sleep)
play = open("play.txt", "r").read()

SERVER_IP = ("192.168.50.9", 5000)

s = socket.socket(type=socket.SOCK_DGRAM)

passTime = -1

timer.enter(0, 1, getAudio, (timer, ))
timer.run()