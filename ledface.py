import os
os.environ["KERAS_BACKEND"] = "jax"

import sys
import cv2
import numpy as np
from keras import models
from keras.src.utils import backend_utils

if getattr(sys, "frozen", False):
	path = os.path.join(sys._MEIPASS, "model/cnn_model.keras")
else:
	path = "model/cnn_model.keras"

MODEL = models.load_model(path)
EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
FACE_CLASSIFIER = cv2.CascadeClassifier(
	cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def CropFrame(frame):
	global FACE_CLASSIFIER

	gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = FACE_CLASSIFIER.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))

	if (len(faces) == 0):
		return []
	
	for (x, y, w, h) in faces:
		crop = gray_image[y:y + h, x:x + w]

	return crop

CAM = None
def RegisterCamera():
	global CAM
	if CAM != None:
		return

	CAM = cv2.VideoCapture(0)

def CloseCamera():
	global CAM
	if CAM == None:
		return

	CAM.release()
	CAM = None

def GetClosestEmotionLED(Default: str):
	global CAM
	global MODEL
	global EMOTIONS

	if CAM == None or not CAM.isOpened():
		return Default

	ret, frame = CAM.read()
	if ret == False or len(frame) == 0:
		return Default
	
	cropped_frame = CropFrame(frame)

	if len(cropped_frame) == 0:
		return Default
	
	resized = cv2.resize(cropped_frame,(48, 48))
	normalized = resized / 255
	reshaped = np.reshape(normalized,(-1, 48, 48, 1))
	reshaped = np.vstack([reshaped])
	prediction = MODEL.predict(reshaped)

	emotion = EMOTIONS[np.argmax(prediction)]

	if emotion == "Angry":
		return "255 39 32"
	elif emotion == "Disgust":
		return "32 255 39"
	elif emotion == "Happy":
		return "248 255 32"
	elif emotion == "Sad":
		return "39 32 255"
	elif emotion == "Surprise" or emotion == "Fear":
		return "255 151 32"
	else:
		return Default