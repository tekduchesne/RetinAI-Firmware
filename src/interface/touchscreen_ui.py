"""
RetinAI Touchscreen User Interface for Raspberry Pi 5

This script creates a simple graphical user interface (GUI) using tkinter.
The interface is designed for a touchscreen device allowing users to navigate
between screens, enter information, and interact with the application.

Features:
- Welcome screen with navigation
- User input screen for selecting eye
    - Left/Right eye
- Loading screen for while picture of eye being taken
- Success screen
- Failure screen to retake picture of eye
- Information screen to display results
"""
import tkinter as tk
from PIL import Image, ImageTk

class TouchscreenUI:
    """
    The TouchscreenUI class represents the GUI of the Retina Scanning Kiosk. 
    This class is designed to manage and display different screens (or views) to guide the user through the retina scanning process
    while also calling relevant vision and network functions in the background.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("RetinAI Touchscreen Interface")
        self.root.geometry("1280x720")  # Raspberry Pi touchscreen resolution
        self.current_frame = None
        self.selected_eye = None  # Store selected eye (Left or Right)
        self.left_eye_taken = False  # Track if left eye photo is captured
        self.right_eye_taken = False  # Track if right eye photo is captured

    def start(self):
        """Start the application by showing the welcome screen."""
        self.show_welcome_screen()

    def show_welcome_screen(self):
        """
        Show the welcome screen with a background image.
        """
        self.root.attributes('-fullscreen', True)
        self._clear_frame()

        # Load and resize background image
        bg_image = Image.open("src/interface/interface_ui/logo-1280x720.png")
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        # Create Canvas and set image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        canvas.pack(fill="both", expand=True)

        # Place labels and buttons on top
        welcome_label = tk.Label(self.current_frame, text="Welcome to the RetinAI Scanning Kiosk",
                                font=("Helvetica", 18), bg="white", fg="black")
        welcome_label.place(relx=0.5, rely=0.3, anchor="center")  # Center text

        # Load transparent button image
        start_button_image = Image.open("src/interface/interface_ui/start_button.png")
        self.start_button_image = ImageTk.PhotoImage(start_button_image)

        # Create an oval-shaped button using Canvas
        button_x, button_y = 640, 360  # Center coordinates for the button
        button_width, button_height = self.start_button_image.width(), self.start_button_image.height()

        # Transparent oval on the canvas
        canvas.create_oval(button_x - button_width // 2, button_y - button_height // 2,
                           button_x + button_width // 2, button_y + button_height // 2,
                           outline="", fill="") 

        # Add the transparent image as a clickable object
        canvas_button = canvas.create_image(button_x, button_y, image=self.start_button_image)
        
        # Bind click event to the canvas image
        def on_click(event):
            self.show_eye_selection_screen()
        
        canvas.tag_bind(canvas_button, "<Button-1>", on_click)

    def show_simulation_screen(self):
        """
        Show the simulation screen with a six options of images in from the vision/simulation_photos directory.
        Images can be refreshed with refresh button on the bottom right of the screen
        """


    def show_eye_selection_screen(self):
        """
        Show the eye selection screen for the user to indicate which eye they would like to take an image of.
        Previously selected 
        """
        self._clear_frame()

        prompt_label = tk.Label(self.current_frame, text="Select which eye to scan:", font=("Helvetica", 18))
        prompt_label.pack(pady=20)

        # Left Eye button, greyed out if already selected
        if not self.left_eye_taken:
            left_eye_button = tk.Button(self.current_frame, text="Left Eye", font=("Helvetica", 16), command=lambda: self.capture_photo("Left"))
            left_eye_button.pack(pady=10)
        else:
            left_eye_button = tk.Button(self.current_frame, text="Left Eye (Complete)", font=("Helvetica", 16), state="disabled", disabledforeground="gray")
            left_eye_button.pack(pady=10)

        # Right Eye button, greyed out if already selected
        if not self.right_eye_taken:
            right_eye_button = tk.Button(self.current_frame, text="Right Eye", font=("Helvetica", 16), command=lambda: self.capture_photo("Right"))
            right_eye_button.pack(pady=10)
        else:
            right_eye_button = tk.Button(self.current_frame, text="Right Eye (Complete)", font=("Helvetica", 16), state="disabled", disabledforeground="gray")
            right_eye_button.pack(pady=10)

        back_button = tk.Button(self.current_frame, text="Back", font=("Helvetica", 16), command=self.show_welcome_screen)
        back_button.pack(pady=20)

    def capture_photo(self, side):
        """
        Capture photo for the selected eye side.
        """
        if side == "Left":
            self.left_eye_taken = True
        elif side == "Right":
            self.right_eye_taken = True

        self.selected_eye = side  # Store the selected eye
        self.show_loading_screen()

    def show_loading_screen(self):
        """
        Show a loading screen while photo is captured.
        """
        self._clear_frame()

        loading_label = tk.Label(self.current_frame, text="Capturing the eye image... Please wait.", font=("Helvetica", 18))
        loading_label.pack(pady=20)

        # Simulate a loading process
        self.root.after(2000, self.check_capture_status)  # TODO: Replace with actual capture process logic

    def check_capture_status(self):
        """
        Check if both images have been taken.
        """
        if self.left_eye_taken and self.right_eye_taken:
            self.show_success_screen()
        else:
            self.show_eye_selection_screen()  # Return to eye selection screen if both eyes are not taken yet

    def show_success_screen(self):
        """
        Show success screen if both images have been captured.
        """
        self._clear_frame()

        success_label = tk.Label(self.current_frame, text="Both images captured successfully!", font=("Helvetica", 18))
        success_label.pack(pady=20)

        next_button = tk.Button(self.current_frame, text="View Results", font=("Helvetica", 16), command=self.show_information_screen)
        next_button.pack(pady=20)

    # TODO: use failure screen if image is unsatisfactory and repeat capture
    # def show_failure_screen(self):
    #     """
    #     Show failure screen if image capture fails.
    #     """
    #     self._clear_frame()

    #     failure_label = tk.Label(self.current_frame, text="Image capture failed. Please try again.", font=("Helvetica", 18))
    #     failure_label.pack(pady=20)

    #     retry_button = tk.Button(self.current_frame, text="Retry", font=("Helvetica", 16), command=self.show_eye_selection_screen)
    #     retry_button.pack(pady=20)

    def show_information_screen(self):
        """
        Show analysis results screen.
        """
        self._clear_frame()

        info_label = tk.Label(self.current_frame, text="Analysis Results:\n[Placeholder for results]", font=("Helvetica", 18))
        info_label.pack(pady=20)

        done_button = tk.Button(self.current_frame, text="Done", font=("Helvetica", 16), command=self.show_welcome_screen)
        done_button.pack(pady=20)

    def _clear_frame(self):
        """
        Clear the current frame and create a new one.
        """
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)
