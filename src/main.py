"""
RetinAI main loop for the kiosk firmware

This script uses the vision, network, and interface implementations
to run the RetinAI Kiosk.

Features:
- tkinter User interface for instructions, input, and diagnosis results
- Vision system to take retinal photos
- Network commands to send and receive information from the ML server

"""

# from vision.<...> import ...
# from network.<...> import ...
import tkinter as tk
from interface.touchscreen_ui import TouchscreenUI

def main():
    # Initialize vision system (WIP)
    print("Initializing vision system...")

    # Start the GUI
    root = tk.Tk()
    app = TouchscreenUI(root)
    app.start()
    root.mainloop() # Server communication called in touchscreen_ui.py (WIP)

if __name__ == "__main__":
    main()
