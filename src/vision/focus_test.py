import cv2
import numpy as np
import os
import time
import sys
import smbus
from picamera2 import Picamera2

# Initialize I2C bus (use 1 for Raspberry Pi 5)
bus = smbus.SMBus(1)

def focusing(val):
    value = (val << 4) & 0x3FF0
    data1 = (value >> 8) & 0x3F
    data2 = value & 0xF0

    print(f"Setting focus: {val}")
    bus.write_byte_data(0x0C, data1, data2)  # Directly send via SMBus

def sobel(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_sobel = cv2.Sobel(img_gray, cv2.CV_16U, 1, 1)
    return cv2.mean(img_sobel)[0]

def laplacian(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_laplacian = cv2.Laplacian(img_gray, cv2.CV_16U)
    return cv2.mean(img_laplacian)[0]

def capture_image(picam2):
    frame = picam2.capture_array()
    return frame

def calculation(picam2):
    image = capture_image(picam2)
    return laplacian(image)

if __name__ == "__main__":
    # Initialize Picamera2
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)  # Lower resolution for speed
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    
    time.sleep(1)
    print("Start focusing")

    max_index = 10
    max_value = 0.0
    last_value = 0.0
    dec_count = 0
    focal_distance = 10

    while True:
        focusing(focal_distance)
        val = calculation(picam2)

        if val > max_value:
            max_index = focal_distance
            max_value = val

        if val < last_value:
            dec_count += 1
        else:
            dec_count = 0

        if dec_count > 6:
            break

        last_value = val
        focal_distance += 15

        if focal_distance > 1000:
            break

    # Adjust to best focus and take high-res photo
    focusing(max_index)
    time.sleep(1)
    picam2.configure("still")
    picam2.start()
    time.sleep(0.5)
    picam2.capture_file("test.jpg")

    print(f"Best focus index: {max_index}, Sharpness: {max_value:.2f}")

    picam2.stop()
