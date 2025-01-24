"""
Camera Testing
Testing Features:
- Init camera
- Capture photo with timestamp
"""

from camera_impl import initialize_camera, capture_photo

def main():
    # Initialize the camera
    picam2 = initialize_camera()
    
    # Capture a photo of the left eye
    capture_photo(picam2, "left")
    
    # Stop the camera after capturing the image
    picam2.stop()

if __name__ == "__main__":
    main()