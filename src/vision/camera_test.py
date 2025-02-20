import time
from picamera2 import Picamera2
from libcamera import controls

def initialize_camera():
    """
    Initialize the camera and set default configurations.
    """
    picam2 = Picamera2()

    # Start the camera with a preview for debugging
    picam2.start(show_preview=True)

    # Set lens position to manual mode and define initial lens position
    picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0})

    return picam2

def capture_photo(picam2, filename):
    """
    Capture a photo and save it with a given filename.
    
    Args:
        picam2: The initialized camera object.
        filename: The name of the file to save the photo as.
    """
    picam2.capture_file(filename)
    print(f"Photo captured and saved as {filename}")

def test_lens_positions(picam2):
    """
    Test different lens positions and capture photos with a delay in between.
    """
    positions = [0.0, 1.0, 2.0, 3.0]
    for pos in positions:
        # Set lens position
        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": pos})
        print(f"Set LensPosition to {pos}")
        
        # Allow time for the lens to adjust
        time.sleep(1)
        
        # Capture photo
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_lens_{pos}_{timestamp}.jpg"
        capture_photo(picam2, filename)

def main():
    # Initialize the camera
    picam2 = initialize_camera()

    # Test different lens positions with delays
    # test_lens_positions(picam2)
    
    # Capture photo
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"test_lens_{timestamp}.jpg"
    capture_photo(picam2, filename)

    # Stop the camera
    picam2.stop()

if __name__ == "__main__":
    main()
