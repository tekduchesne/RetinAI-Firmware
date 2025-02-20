import os
import threading
import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((320, 240), 0, 32)
pygame.key.set_repeat(100)

# Focus parameters
MIN_FOCUS = 0
MAX_FOCUS = 1000
INITIAL_FOCUS = 500
STEP_SIZE = 10

# Thread-safe focus control
focus_lock = threading.Lock()
current_focus = INITIAL_FOCUS

def set_focus(value):
    """Set focus using v4l2-ctl with proper error handling"""
    global current_focus
    with focus_lock:
        clamped = max(MIN_FOCUS, min(value, MAX_FOCUS))
        if clamped != current_focus:
            ret = os.system(f"v4l2-ctl -d /dev/v4l-subdev0 -c focus_absolute={clamped}")
            if ret == 0:
                current_focus = clamped
                print(f"Focus set to: {current_focus}")
            else:
                print("Focus adjustment failed! Check v4l2 interface")

def run_focus_control():
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    set_focus(current_focus + STEP_SIZE)
                elif event.key == K_DOWN:
                    set_focus(current_focus - STEP_SIZE)
                elif event.key == K_q:
                    pygame.quit()
                    os._exit(0)

def run_camera():
    camera_cmd = (
        "libcamera-still -t 0 "
        "--autofocus-mode manual "
        "--tuning-file /usr/share/libcamera/ipa/rpi/pisp/imx477_af.json "
        "--width 2028 --height 1520 "
        "--viewfinder-width 320 --viewfinder-height 240"
    )
    os.system(camera_cmd)

if __name__ == "__main__":
    # Set initial focus position
    set_focus(INITIAL_FOCUS)
    
    # Start focus control thread
    focus_thread = threading.Thread(target=run_focus_control, daemon=True)
    focus_thread.start()

    # Start camera preview
    run_camera()
