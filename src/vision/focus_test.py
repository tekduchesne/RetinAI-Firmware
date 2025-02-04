import os
import threading
import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((320, 240), 0, 32)
pygame.key.set_repeat(100)

def runFocus():
    temp_val = 512  # Initial focus value (midpoint)
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                print(f"Current focus value: {temp_val}")
                if event.key == K_UP:  # Increase focus value
                    print('Focus UP')
                    if temp_val < 1000:
                        temp_val += 10
                    else:
                        print("Focus value is already at maximum.")
                elif event.key == K_DOWN:  # Decrease focus value
                    print('Focus DOWN')
                    if temp_val > 12:
                        temp_val -= 10
                    else:
                        print("Focus value is already at minimum.")
                
                # Convert focus value to I2C data format
                value = (temp_val << 4) & 0x3FF0
                dat1 = (value >> 8) & 0x3F
                dat2 = value & 0xF0

                # Send I2C command to adjust focus manually
                try:
                    result = os.system(f"i2cset -y 1 0x0c {dat1} {dat2}")
                    if result != 0:
                        print("Error: I2C write failed. Check your connection or device address.")
                except Exception as e:
                    print(f"I2C write error: {e}")

def runCamera():
    # Use libcamera-still in preview mode without autofocus
    cmd = "libcamera-still -t 0"
    os.system(cmd)

if __name__ == "__main__":
    # Start the manual focus control thread
    t1 = threading.Thread(target=runFocus, daemon=True)
    t1.start()

    # Run the camera preview in the main thread
    runCamera()
