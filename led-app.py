import sched, time
import numpy as np
import math
import sounddevice as sd
from infi.systray import SysTrayIcon
import os

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

	r = round(float(np.clip(r * 100, 0, 100)), 2)
	g = round(float(np.clip(g * 100, 0, 100)), 2)
	b = round(float(np.clip(b * 100, 0, 100)), 2)

	return r, g, b

def audio_callback(indata, frames, time, status):
	global play

	if (play == "False"):
		return

	volume_norm = np.linalg.norm(indata) * 10
	volume = np.clip(int(volume_norm), 0, 200)

	print(volume, volume_to_rgb(volume))
	
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
	if (play == "True"):
		return
	
	setPlay("True")

def off(systray):
	if (play == "False"):
		return

	setPlay("False")

def on_quit_callback(systray):
	os._exit(1)
    
menu_options = (("Music Mode", None, (("On", None, on), ("Off", None, off),)),)
systray = SysTrayIcon("icon.ico", "LED Controller", menu_options, on_quit=on_quit_callback)
systray.start()

timer = sched.scheduler(time.time, time.sleep)
play = open("play.txt", "r").read()

timer.enter(0, 1, getAudio, (timer, ))
timer.run()

if (play == "True"):
	pass  #Connect to bluetooth. Disconnect from bluetooth on quit. Else just send commands for on/off switch