import socket
#import board
#import neopixel

DEFAULT_RGB = "255 126 0"
#pixels = neopixel.NeoPixel(board.D18, 55, brightness=1) # 55 is number of pixels (NEEDS TO BE CHANGED)

def setRGB(data):
	rgb = data.split()

	print(rgb)

	#pixels.fill((rgb[0], rgb[1], rgb[2]))

setRGB(DEFAULT_RGB)

s = socket.socket()
s.bind(("0.0.0.0", 5000))
s.listen()

while True:
	c,a = s.accept()

	with c:
		while True:
			data = c.recv(1024).decode("ascii")
			
			if (data == ""):
				break

			default = False

			setRGB(data)

	setRGB(DEFAULT_RGB)