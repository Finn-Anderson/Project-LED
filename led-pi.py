'''from rgbled import rgbled
from bleak import BleakClient
from bleak import BleakScanner
import asyncio

async def main():
	devices = await BleakScanner.discover()
	for d in devices:
		print(d)

asyncio.run(main())

DEFAULT_RGB = [255, 126, 0]
led = rgbled(DEFAULT_RGB[0], DEFAULT_RGB[1], DEFAULT_RGB[2])

def setRGB(r, g, b):
	led.changeto(r, g, b, 0.1)

def data_received(data):
	setRGB(data[0], data[1], data[2])

def client_disconnected():
	setRGB(DEFAULT_RGB[0], DEFAULT_RGB[1], DEFAULT_RGB[2])
	
server = BluetoothServer(data_received, auto_start = True, when_client_disconnects = client_disconnected)'''