"""
Camera Testing
Testing Features:
- Init camera
- Capture photo with timestamp
"""

import time
from camera_impl import initialize_camera, capture_photo

def main():
    # Initialize the camera
    picam2 = initialize_camera()

    # Ensure the camera focuses before taking the photo
    picam2.start_focus()  # Make sure this triggers autofocus if applicable

    # Allow time for the camera to focus
    time.sleep(2)  # Adjust the sleep time based on how long the camera takes to focus
    
    # Capture a photo of the left eye
    capture_photo(picam2, "left")
    
    # Stop the camera after capturing the image
    picam2.stop()

if __name__ == "__main__":
    main()