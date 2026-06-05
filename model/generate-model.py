import os
os.environ["KERAS_BACKEND"] = "jax"

from keras import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from keras.optimizers import Adam
from keras.utils import to_categorical
import pandas as pd
import numpy as np

data = pd.read_csv("fer2013.csv.gz", compression="gzip")
data["pixels"] = data["pixels"].apply(lambda x: np.array(x.split(), dtype="float32"))

train_data = data[data["Usage"] == "Training"]
test_data = data[data["Usage"] == "PublicTest"]

x_train = np.array(train_data["pixels"].tolist()).reshape(-1, 48, 48, 1) / 255
y_train = np.array(train_data["emotion"])
x_test = np.array(test_data["pixels"].tolist()).reshape(-1, 48, 48, 1) / 255
y_test = np.array(test_data["emotion"])

num_classes = len(np.unique(y_train))
y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(48, 48, 1)),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Conv2D(128, (3, 3), activation="relu"),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Flatten(),
    Dense(512, activation="relu"),
    Dropout(0.5),
    Dense(num_classes, activation="softmax")
])

model.compile(loss="categorical_crossentropy", optimizer=Adam(0.0001), metrics=["accuracy"])

model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=128, epochs=32)

model.save("cnn_model.keras")