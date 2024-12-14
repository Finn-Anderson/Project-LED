import socket
import board
import neopixel
import asyncio
import numpy as np
import math

DEFAULT_RGB = "0 0 0"
PREVIOUS_RGB = DEFAULT_RGB
CURRENT_RGB = DEFAULT_RGB
TARGET_RGB = DEFAULT_RGB
pixels = neopixel.NeoPixel(board.D18, 300, brightness = 0.5) # middle number is the number of pixels (NEEDS TO BE CHANGED)source 
COUNT = 0

def setRGB(data):
	global PREVIOUS_RGB
	global TARGET_RGB
	global COUNT
	
	COUNT = 0
	
	if (TARGET_RGB == data):
		return
		
	print(data)
	
	PREVIOUS_RGB = TARGET_RGB
	TARGET_RGB = data

def numRounded(value):
	if (value < 0):
		return math.floor(value)
	else:
		return math.ceil(value)
	
async def setRGBFill():
	global PREVIOUS_RGB
	global CURRENT_RGB
	global TARGET_RGB
	global COUNT
	
	COUNT = 0
	
	while True:
		await asyncio.sleep(0.01)
		
		if (CURRENT_RGB == TARGET_RGB or COUNT >= 500):
			COUNT = COUNT + 1
			
			if (COUNT == 500):
				setRGB(DEFAULT_RGB)
				
				CURRENT_RGB = DEFAULT_RGB

				pixels.fill((0, 0, 0))
			
			continue
			
		COUNT = 0
			
		targetData = TARGET_RGB.split()
		currentData = CURRENT_RGB.split()
		priorData = PREVIOUS_RGB.split()
		
		r = int(np.clip(int(currentData[0]) + numRounded((int(targetData[0]) - int(currentData[0]) / 6), 0, 255)
		g = int(np.clip(int(currentData[1]) + numRounded((int(targetData[1]) - int(currentData[1]) / 6), 0, 255)
		b = int(np.clip(int(currentData[2]) + numRounded((int(targetData[2]) - int(currentData[2]) / 6), 0, 255)
		
		CURRENT_RGB = "{} {} {}".format(r, g, b)

		pixels.fill((r, g, b)))
		
async def server():
	s = socket.socket(type=socket.SOCK_DGRAM)
	s.bind(("0.0.0.0", 5000))
	s.setblocking(0)
	
	loop = asyncio.get_event_loop()
	
	while True:
		try:
			data, _ = await loop.sock_recvfrom(s, 1024)
			data = data.decode("ascii")
		
			if (data != ""):
				setRGB(data)
		except Exception as e:
			print(e)
			setRGB(DEFAULT_RGB)
	
async def main():
	setRGB(DEFAULT_RGB)
	
	async with asyncio.TaskGroup() as tg:
		tg.create_task(setRGBFill())
		tg.create_task(server())


asyncio.run(main())