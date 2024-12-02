import sched, time
import numpy as np
import struct
import math
import sounddevice as sd

n = 0

def audio_callback(indata, frames, time, status):
	global n

	volume_norm = np.linalg.norm(indata) * 10
	volume = np.clip(int(volume_norm), 0, 200)

	print(volume)
	
def getAudio(timer):
	
	with sd.InputStream(device="Voicemeeter Out B1 (VB-Audio Voicemeeter VAIO), Windows DirectSound", channels=8, callback=audio_callback):
		sd.sleep(86400000)

	timer.enter(86400, 1, getAudio, (timer, ))

timer = sched.scheduler(time.time, time.sleep)
timer.enter(0, 1, getAudio, (timer, ))
timer.run()