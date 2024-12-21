RetinAI Kiosk Firmware (WIP README)
This repository contains the kiosk firmware for initiazing hardware components
and user interface to carry out taking retinal images to be processed in the cloud 

Project Structure:

retinai-kiosk-firmware/
│
├── src/
│   ├── vision/
│   │   ├── camera_impl.py          # Functions to control Arducam
│   │   └── camera_testing.py       # Functions to test Arducam
│   ├── interface/
│   │   └── ui_main.py              # UI for instructions and controls
│   ├── network/
│   │   └── server_communication.py # Logic to send image to server and response handling
│   └── main.py                     # Main loop for the kiosk firmware
│
├── configs/
│   ├── system_config.json          # JSON file with system parameters
│   └── camera_settings.json        # Presets for camera/LEDs
│
├── README.md                       # Overview of the project
├── .gitignore
└── requirements.txt                # Dependencies