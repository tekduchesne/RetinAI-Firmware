"""
Camera implementation

Features:
- Camera initializion method
- Capture Photo that takes in side of eye as argument and saves it
"""
import os

# Directory to save the captured photos
OUTPUT_DIR = "/home/RetinAi/Desktop/firmware/RetinAI-Firmware/src/vision/captured_photos"

# Initialize Arducam using libcamera
def initialize_camera():
    print("Camera initialized using libcamera.")
    # No explicit initialization is required for libcamera
    return True

# Capture photo of left/right eye and save it
def capture_photo(side):
    if side.lower() not in ["left", "right"]:
        print("Invalid input. Please choose 'left' or 'right'.")
        return
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Filename based on the side of the eye
    filename = f"{OUTPUT_DIR}/1_{side.lower()}.jpg"
    
    # Command to capture a photo using libcamera-still
    camera_cmd = (
        f"libcamera-still -o {filename} "
        "--width 2028 --height 1520 "
        "--tuning-file /usr/share/libcamera/ipa/rpi/pisp/imx477_af.json "
        "--autofocus-mode continuous "
    )
    
    os.system(camera_cmd)
    print(f"{side.capitalize()} retinal image saved as {filename}")
