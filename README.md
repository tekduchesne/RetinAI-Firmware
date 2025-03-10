# RetinAI Kiosk Firmware
This repository contains the kiosk firmware for initiazing hardware components
and user interface to carry out taking retinal images to be processed in the cloud 

To run the main interface loop of the kiosk comprising of all of RetinAI's functionality,
run 'main.py' on the Raspi directly
```
python main.py
```

## Project Structure:

retinai-kiosk-firmware/
```
├── src/
│   ├── vision/
│   │   ├── captured_photos/           # Folder for captured photos
│   │   ├── camera_impl.py             # Functions to control Arducam
│   │   ├── pwmControl.py              # Functions to control PWM for pi
│   │   ├── demo_diagnoses.py          # Class to send selected images to the API, get the diagnosis, and compare with true labels
│   │   ├── demo_test.py               # Demo of DemoClient functionality
│   │   ├── focus_test.py              # Functions to test Arducam focusing algorithm
│   │   └── camera_test.py             # Functions to test Arducam camera
│   ├── interface/
│   │   ├── interface_ui/              # Folder for UI Assets
│   │   └── touchscreen_ui.py          # UI loop for instructions and kiosk controls, allows user to navigate between screens
│   ├── network/
│   │   ├── testImages/                # Folder to store test images
│   │   ├── exampleClient.py           # Raspberry Pi functions to call backend api + Demo
│   │   └── exampleClientVariables.py  # Example environment variables file for kiosk
│   └── main.py                        # Main loop for the kiosk firmware
│
├── README.md                          # Overview of the project & instructions
├── .gitignore
└── requirements.txt                   # Dependencies
```
