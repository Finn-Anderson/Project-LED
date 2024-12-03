import sched, time
import numpy as np
import math
import sounddevice as sd
from infi.systray import SysTrayIcon
import os
import socket

def volume_to_rgb(volume):
	degree = volume * 1.8  # 200 * 1.8 = 360

	arc = math.floor(degree / 120)

	r = 0
	g = 0
	b = 0

	if (arc == 0):
		r = (1 - (degree / 120)) * 0.8
		b = (degree / 120) * 0.8 + 0.2
	elif (arc == 1):
		b = 1 - (degree / 120 - 1)
		g = degree / 120 - 1
	else:
		g = 1 - (degree / 120 - 2)
		r = degree / 120 - 2

	r = round(float(np.clip(r * 255, 0, 255)), 2)
	g = round(float(np.clip(g * 255, 0, 255)), 2)
	b = round(float(np.clip(b * 255, 0, 255)), 2)

	return r, g, b

def audio_callback(indata, frames, time, status):
	global play
	global passTime

	if (play == "False" or passTime > time.currentTime):
		return

	volume_norm = np.linalg.norm(indata) * 10
	volume = np.clip(int(volume_norm), 0, 200)

	volTuple = volume_to_rgb(volume)

	volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

	passTime = time.currentTime + 0.1

	s.send(volStr.encode("ascii"))
	
def getAudio(timer):
	timer.enter(86400, 1, getAudio, (timer, ))

	with sd.InputStream(device="Voicemeeter Out B1 (VB-Audio Voicemeeter VAIO), Windows DirectSound", channels=8, callback=audio_callback):
		sd.sleep(86400000)

def setPlay(bool):
	global play

	play = bool

	f = open("play.txt", "w")
	f.write(play)
	f.close()

def on(systray):
	global s

	if (play == "True"):
		return

	s = socket.socket()
	s.connect(("127.0.0.1", 5000))
	
	setPlay("True")

def off(systray):
	if (play == "False"):
		return

	setPlay("False")

	s.close()

def on_quit_callback(systray):
	s.close()

	os._exit(1)
    
menu_options = (("Music Mode", None, (("On", None, on), ("Off", None, off),)),)
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

timer = sched.scheduler(time.time, time.sleep)
play = open("play.txt", "r").read()

s = socket.socket()

passTime = -1

if (play == "True"):
	s.connect(("127.0.0.1", 5000))

timer.enter(0, 1, getAudio, (timer, ))
timer.run()