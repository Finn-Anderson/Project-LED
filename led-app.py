import sched, time
import numpy as np
import struct
import math
import sounddevice as sd

def volume_to_rgb(volume):
	degree = volume * 1.8  #200 * 1.8 = 360

	arc = math.floor(degree / 120)

	r = 0
	g = 0
	b = 0

	if (arc == 0):
		r = 1 - (degree / 120) - 0.1
		b = degree / 120 + 0.1
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
	volume_norm = np.linalg.norm(indata) * 10
	volume = np.clip(int(volume_norm), 0, 200)

	print(volume, volume_to_rgb(volume))
	
def getAudio(timer):
	
	with sd.InputStream(device="Voicemeeter Out B1 (VB-Audio Voicemeeter VAIO), Windows DirectSound", channels=8, callback=audio_callback):
		sd.sleep(86400000)

	timer.enter(86400, 1, getAudio, (timer, ))

timer = sched.scheduler(time.time, time.sleep)
timer.enter(0, 1, getAudio, (timer, ))
timer.run()