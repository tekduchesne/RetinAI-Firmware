import subprocess
import threading
import time

def start_camera_feed():
    # Start the libcamera-vid process with a live feed
    feed_process = subprocess.Popen([
        'libcamera-vid', 
        '-t', '0',  # Run indefinitely
        '--autofocus-mode', 'manual',
        '--preview'  # Ensure preview is shown
    ])
    return feed_process

def capture_photo():
    # Capture a photo using libcamera-still
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"/home/pi/Pictures/captured_photo_{timestamp}.jpg"
    subprocess.run([
        'libcamera-still',
        '-o', output_filename,
        '--autofocus-mode', 'manual'
    ])
    print(f"Photo captured and saved to {output_filename}")

# Start the camera feed in a separate thread
feed_process = start_camera_feed()

try:
    while True:
        user_input = input("Press 'c' to capture a photo or 'q' to quit: ").strip().lower()
        if user_input == 'c':
            capture_photo()
        elif user_input == 'q':
            break
finally:
    # Stop the camera feed when done
    if feed_process:
        feed_process.terminate()
    print("Camera feed stopped.")
