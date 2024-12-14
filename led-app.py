import sched, time
import numpy as np
import math
import sounddevice as sd
from infi.systray import SysTrayIcon
import os
import socket

COUNT = 0

def volume_to_rgb(volume):
	degree = volume

	arc = math.floor(degree / 180)

	r = 0
	g = 0
	b = 0

	if (arc == 0):
		b = (1 - (degree / 180))
		g = (degree / 180)
	else:
		g = 1 - (degree / 180 - 1)
		r = degree / 180 - 1

	r = round(float(np.clip(r * 255, 0, 255)), 2)
	g = round(float(np.clip(g * 255, 0, 255)), 2)
	b = round(float(np.clip(b * 255, 0, 255)), 2)

	return int(r), int(g), int(b)

def audio_callback(indata, frames, time, status):
	global play
	global passTime
	global s
	global SERVER_IP
	global COUNT

	if (play == "False" or passTime > time.currentTime):
		return

	volume_norm = np.linalg.norm(indata) ** 2.5
	volume = np.clip(int(volume_norm), 0, 360)

	volTuple = volume_to_rgb(volume)

	volStr = "{} {} {}".format(volTuple[0], volTuple[1], volTuple[2])

	passTime = time.currentTime + 0.2

	if (volume == 0):
		COUNT = COUNT + 1	
	else:
		COUNT = 0

	if (COUNT >= 20):
		return

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

	s.sendto("0 0 255".encode("ascii"), SERVER_IP)

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
s.sendto("0 0 255".encode("ascii"), SERVER_IP)

passTime = -1

timer.enter(0, 1, getAudio, (timer, ))
timer.run()