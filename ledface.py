import cv2
import numpy as np
"""
TODO Make TensorFlow compatible with Python 3.14
from deepface import DeepFace

cap = cv2.VideoCapture(0)
face_classifier = cv2.CascadeClassifier(
	cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_bounding_box(vid):
	gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
	faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
	for (x, y, w, h) in faces:
		cv2.rectangle(vid, (x, y), (x + w, y + h), (0, 255, 0), 4)
	return faces

while(1):
	ret, frame = cap.read()

	emotion_analysis = DeepFace.analyze(frame, actions=['emotion'])

	faces = detect_bounding_box(
		frame
	)  # apply the function we created to the video frame

	# Show the image with detected emotion
	cv2.putText(frame, emotion_analysis['dominant_emotion'], (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
	cv2.imshow("Emotion Detection", frame)

	if cv2.waitKey(1) & 0xFF == ord("q"):
		break

cap.release()
cv2.destroyAllWindows()
"""

CAM = cv2.VideoCapture(0)
def RegisterCamera():
	global CAM

	CAM = cv2.VideoCapture(0)

def CloseCamera():
	CAM.release()

def GetClosestEmotionLED():
	global CAM

	colour = "228 112 37"

	ret, frame = CAM.read()
	if (ret == False):
		return "0 0 0"
	
	img_rgb = cv2.imread("images/happy.png")
	img_rgb2 = cv2.imread("images/sad.png")
	img_rgb3 = cv2.imread("images/angry.png")
	img_rgb4 = cv2.imread("images/normal.png")

	# Convert it to grayscale
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	img_gray2 = cv2.cvtColor(img_rgb2, cv2.COLOR_BGR2GRAY)
	img_gray3 = cv2.cvtColor(img_rgb3, cv2.COLOR_BGR2GRAY)
	img_gray4 = cv2.cvtColor(img_rgb4, cv2.COLOR_BGR2GRAY)

	template = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Perform match operations.
	res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
	res2 = cv2.matchTemplate(img_gray2, template, cv2.TM_CCOEFF_NORMED)
	res3 = cv2.matchTemplate(img_gray3, template, cv2.TM_CCOEFF_NORMED)
	res4 = cv2.matchTemplate(img_gray4, template, cv2.TM_CCOEFF_NORMED)

	value = res.max()
	value2 = res2.max()
	value3 = res3.max()
	value4 = res4.max()
	
	if (value > value2 and value > value3 and value > value4):
		colour = "0 255 0"
	elif (value2 > value3 and value2 > value4):
		colour = "0 0 255"
	elif (value3 > value4):
		colour = "0 255 0"

	return colour