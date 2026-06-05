import os
os.environ["KERAS_BACKEND"] = "jax"

import sys
import cv2
import numpy as np
from keras import models

if getattr(sys, "frozen", False):
	path = os.path.join(sys._MEIPASS, "model/cnn_model.keras")
else:
	path = "model/cnn_model.keras"

model = models.load_model(path)
emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
face_classifier = cv2.CascadeClassifier(
	cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def CropFrame(frame):
	gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))

	if (len(faces) == 0):
		return []
	
	for (x, y, w, h) in faces:
		crop = gray_image[y:y + h, x:x + w]

	return crop

CAM = None
def RegisterCamera():
	global CAM

	CAM = cv2.VideoCapture(0)

def CloseCamera():
	if CAM == None:
		return

	CAM.release()
	cv2.destroyAllWindows()

def GetClosestEmotionLED(Default: str):
	global CAM

	ret, frame = CAM.read()
	if ret == False:
		return Default
	
	cropped_frame = CropFrame(frame)

	if len(cropped_frame) == 0:
		return Default
	
	resized = cv2.resize(cropped_frame,(48, 48))
	normalized = resized / 255
	reshaped = np.reshape(normalized,(-1, 48, 48, 1))
	reshaped = np.vstack([reshaped])
	prediction = model.predict(reshaped)

	emotion = emotions[np.argmax(prediction)]

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