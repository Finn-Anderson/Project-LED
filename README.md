# Project-LED
Project LED displays colours via music, facial expressions or a solid colour through an LED strip connected to a raspberry pi or other alternative boards that you can setup the led-pi code on. All data sent from the computer to the board is done through a network connection.

![Main menu](/readme_images/main.png)

Project LED allows you to control the mode (music, solid light, facial expressions or off), which input device to listen to (loopback output devices are only for Windows), solid light colour, timer between no music and switching to chosen solid light colour, brightness and ip address.

The expressions uses a Convolutional Neural Network model to analyse your face through a webcam and pick the emotion. The expressions mode currently has 7 light settings depending on your emotion. These emotions are anger, disgust, fear, happiness, sadness, surprise and neutral. Neutral facial expressions use the solid light colour set by the user.