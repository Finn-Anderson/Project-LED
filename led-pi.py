import socket
#import board
#import neopixel

DEFAULT_RGB = "0 0 0"
PREVIOUS_RGB = DEFAULT_RGB
#pixels = neopixel.NeoPixel(board.D18, 55, brightness=1) # 55 is number of pixels (NEEDS TO BE CHANGED)

def setRGB(data):
	rgb = data.split()

	if (PREVIOUS_RGB == rgb):
		return

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
			try:
				data = c.recv(1024).decode("ascii")
				
				if (data == ""):
					break

				setRGB(data)
			except:
				break

	setRGB(DEFAULT_RGB)