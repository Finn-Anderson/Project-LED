import socket
import board
import neopixel
import asyncio
import numpy as np
import math

DEFAULT_RGBA = "0 0 0 0"
PREVIOUS_RGBA = DEFAULT_RGBA
CURRENT_RGBA = DEFAULT_RGBA
TARGET_RGBA = DEFAULT_RGBA
COUNT = 0

def setRGBA(data):
	global PREVIOUS_RGBA
	global TARGET_RGBA
	global COUNT
	
	if (DEFAULT_RGBA != data):
		COUNT = 0
	
	if (TARGET_RGBA == data):
		return
	
	PREVIOUS_RGBA = TARGET_RGBA
	TARGET_RGBA = data

def numRounded(value):
	if (value < 0):
		return math.floor(value)
	else:
		return math.ceil(value)
	
async def setRGBAFill():
	global PREVIOUS_RGBA
	global CURRENT_RGBA
	global TARGET_RGBA
	global COUNT
	
	while True:
		await asyncio.sleep(0.01)
			
		targetData = TARGET_RGBA.split()
		currentData = CURRENT_RGBA.split()
		priorData = PREVIOUS_RGBA.split()
		
		r = int(np.clip(int(currentData[0]) + numRounded((int(targetData[0]) - int(priorData[0]) / 10), 0, 255)))
		g = int(np.clip(int(currentData[1]) + numRounded((int(targetData[1]) - int(priorData[1]) / 10), 0, 255)))
		b = int(np.clip(int(currentData[2]) + numRounded((int(targetData[2]) - int(priorData[2]) / 10), 0, 255)))
		a = int(np.clip(int(currentData[3]) + numRounded((int(targetData[3]) - int(priorData[3]) / 10), 0, 100)))
		
		temp_rgb = "{} {} {} {}".format(r, g, b, a)

		if (CURRENT_RGBA == temp_rgb):
			setCount()
			
			continue
		
		CURRENT_RGBA = temp_rgb

		pixels = neopixel.NeoPixel(board.D18, 300, brightness = float(a) / 100.0)
		pixels.fill((r, g, b))

def setCount():
	global PREVIOUS_RGBA
	global CURRENT_RGBA
	global TARGET_RGBA
	global COUNT
	
	COUNT += 1
	
	if (COUNT == 500):
		setRGBA(DEFAULT_RGBA)
		
async def server():
	s = socket.socket(type=socket.SOCK_DGRAM)
	s.bind(("0.0.0.0", 5000))
	s.setblocking(0)
	
	loop = asyncio.get_event_loop()

	print ("Connected")
	
	while True:
		try:
			data, _ = await loop.sock_recvfrom(s, 1024)
			data = data.decode("ascii")
		
			if (data != ""):
				setRGBA(data)
		except Exception as e:
			print(e)

			setRGBA(DEFAULT_RGBA)

			print ("Disconnected")
	
async def main():
	setRGBA(DEFAULT_RGBA)
	
	async with asyncio.TaskGroup() as tg:
		tg.create_task(setRGBAFill())
		tg.create_task(server())

asyncio.run(main())