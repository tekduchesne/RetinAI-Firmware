"""
Camera implementation

Features:
- Camera initializion method
- Capture Photo that takes in side of eye as argument and saves it
"""
from picamera2 import Picamera2
import time
from datetime import datetime

# Initialize Arducam using picamera2 library
def initialize_camera():
    # Initialize the camera
    picam2 = Picamera2()
    picam2.start()  # Start the camera
    return picam2

# Capture photo of left/right eye and save it
def capture_photo(picam2, side):
    if side.lower() not in ["left", "right"]:
        print("Invalid input. Please choose 'left' or 'right'.")
        return
    
    # Get the current time in YYYYMMDD_HHMMSS format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{side}_eye_{timestamp}.jpg"
    
    # Capture a photo and save it to the specified file
    picam2.capture_file(filename)
    print(f"{side.capitalize()} retinal image saved as {filename}")
