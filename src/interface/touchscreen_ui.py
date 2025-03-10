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
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from vision.demo_diagnoses import DemoClient
from vision.camera_impl import capture_photo
import time
import random
import requests
from PIL import Image, ImageTk

# Define the base path to the 'interface_ui' directory
BASE_PATH = Path(__file__).parent / "interface_ui"

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

        self.selected_images = []
        # For simulation selected images and scanning (PiOS)
        # self.demo_client = DemoClient(images_dir='/home/RetinAi/Desktop/Embedded/raspi_raw', csv_dir='/home/RetinAi/Desktop/Embedded/test.csv')
        # For simulation selected images and scanning (Windows)
        self.demo_client = DemoClient(images_dir='../../Embedded/raspi_raw', csv_dir='../../Embedded/test.csv')

    def start(self):
        """Start the application by showing the welcome screen."""
        self.show_welcome_screen()

    def show_welcome_screen(self):
        """
        Show the welcome screen with a background image.
        """
        # disable for testing
        # self.root.attributes('-fullscreen', True)
        self._clear_frame()

        # Load and resize background image
        bg_image = Image.open(BASE_PATH / "logo-1280x720.png")
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
        start_button_image = Image.open(BASE_PATH / "purple_start_button.png")
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

        # Simulation button (bottom-right corner)
        simulation_button = tk.Button(self.current_frame, text="Simulation",
                                      command=self.show_simulation_screen,
                                      font=("Helvetica", 14), bg="blue", fg="white")
        simulation_button.place(relx=0.9, rely=0.9, anchor="center")

    def show_simulation_screen(self):
        """
        Show the simulation screen with six selectable images.
        """
        self._clear_frame()

        # Reset selected images when entering the simulation screen
        self.selected_images = []  # Clear any previously selected images

        # Load and resize background image
        sim_bg_path = BASE_PATH / "main_background.png"  # Path to the background image
        if not sim_bg_path.exists():
            messagebox.showerror("Error", f"Background image not found: {sim_bg_path}")
            return

        sim_bg = Image.open(sim_bg_path).resize((1280, 720))  # Resize to fit screen
        self.sim_bg = ImageTk.PhotoImage(sim_bg)  # Store reference to avoid garbage collection

        # Add background image as a Label
        bg_label = tk.Label(self.current_frame, image=self.sim_bg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cover entire screen

        # Define image_dir as a Path object (PiOS)
        # image_dir = Path('/home/RetinAi/Desktop/Embedded/raspi_raw')
        # Define image_dir as a Path object (Windows)
        image_dir = Path('../../Embedded/raspi_raw')

        try:
            # Randomly select 6 images from the directory
            image_file_names = random.sample(list(image_dir.glob("*.jpg")), 6)
        except ValueError:
            messagebox.showerror("Error", "Not enough images in the directory!")
            return

        # Create a grid frame for images and center it
        grid_frame = tk.Frame(self.current_frame, bg="black")  # Transparent-like background
        grid_frame.place(relx=0.5, rely=0.45, anchor="center")  # Center the grid frame

        # Initialize dictionaries to track buttons and their states
        self.image_buttons = {}

        # Display images in a grid (2 rows x 3 columns)
        for i, image_file in enumerate(image_file_names):
            # Create a sub-frame for each image and its label
            item_frame = tk.Frame(grid_frame)
            item_frame.grid(row=i // 3, column=i % 3, padx=20, pady=20)

            # Load and resize the image
            img = Image.open(image_file).resize((250, 250))  # Resize for display
            photo = ImageTk.PhotoImage(img)

            # Create a button for the image
            btn = tk.Button(item_frame, image=photo,
                            command=lambda f=image_file: self.select_image(f),
                            relief="flat", bg="white")
            btn.image = photo  # Keep a reference to avoid garbage collection
            btn.pack()  # Pack the button inside the item frame

            # Store the button in the dictionary for later updates
            self.image_buttons[image_file] = btn

            # Create a label for the image name and place it below the button
            label = tk.Label(item_frame, text=image_file.name, font=("Helvetica", 12))
            label.pack()

        # Submit button (place it below the grid and center it)
        submit_button = tk.Button(self.current_frame, text="Submit",
                                command=self.submit_selected_images,
                                font=("Helvetica", 14), bg="green", fg="white")
        submit_button.place(relx=0.6, rely=0.95, anchor="center")  # Center it at the bottom of main_frame

        # Back button for returning to welcome screen
        back_button = tk.Button(self.current_frame, text="Back", font=("Helvetica", 14), command=self.show_welcome_screen)
        back_button.place(relx=0.4, rely=0.95, anchor="center")

    def select_image(self, image_file):
        """
        Select or deselect an image.
        """
        if not hasattr(self, 'selected_images'):
            self.selected_images = []  # Initialize selected_images if not already defined

        if image_file in self.selected_images:
            # Deselect the image
            self.selected_images.remove(image_file)

            # Update button appearance to indicate deselection (reset to default)
            self.image_buttons[image_file].config(relief="flat", bg="SystemButtonFace")
        elif len(self.selected_images) < 2:
            # Select the image
            self.selected_images.append(image_file)

            # Update button appearance to indicate selection (e.g., gray out)
            self.image_buttons[image_file].config(relief="sunken", bg="lightgray")
        else:
            # Show a popup if trying to select more than two images
            messagebox.showwarning("Selection Limit", "You can only select up to two images.")

    def submit_selected_images(self):
        """
        Submit selected images for scanning.
        """
        # Ensure exactly two images are selected
        if not hasattr(self, 'selected_images') or len(self.selected_images) != 2:
            messagebox.showerror("Error", "Please select exactly two images!")
            return

        # Extract filenames of selected images
        image_filenames = [img.name for img in self.selected_images]

        # DEBUG: Print filenames being submitted
        print(f"Submitting filenames: {image_filenames}")

        try:
            start_time = time.time()
            results = self.demo_client.send_images_and_get_diagnosis(image_filenames)
            elapsed_time = time.time() - start_time

            print(f"Diagnosis Results: {results}")  # DEBUG: Print API response

            # Navigate to results screen with diagnosis results
            self.show_results_sim_screen(image_filenames, results)

        except requests.ConnectionError as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server:\n{str(e)}")
        except requests.HTTPError as e:
            messagebox.showerror("HTTP Error", f"Server returned an error:\n{str(e)}")
        except FileNotFoundError as e:
            messagebox.showerror("File Error", f"File not found:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    def show_results_sim_screen(self, image_filenames, results):
        """
        Show the results screen with images and their diagnosis results side by side.
        """
        self._clear_frame()

        # Create a main frame for results
        main_frame = tk.Frame(self.current_frame, width=1280, height=720)
        main_frame.pack(expand=True, fill="both")
        main_frame.grid_propagate(False)

        # Create a grid frame for displaying images and results
        grid_frame = tk.Frame(main_frame)
        grid_frame.place(relx=0.5, rely=0.4, anchor="center")  # Center it

        # Display images and their results side by side
        for i, result in enumerate(results):
            filename = result['filename']
            diagnosis = result['diagnosis']
            is_correct = result['is_correct']

            # Load and resize the image
            img_path = Path(self.demo_client.images_dir) / filename
            img = Image.open(img_path).resize((350, 350))  # Resize for display
            photo = ImageTk.PhotoImage(img)

            # Create a label for the image
            img_label = tk.Label(grid_frame, image=photo)
            img_label.image = photo 
            img_label.grid(row=0, column=i, padx=20, pady=10)

            # Create a label for the diagnosis result
            result_text = (
                f"Filename: {filename}\n"
                f"Diagnosis: {diagnosis}\n"
                f"Correct: {'Yes' if is_correct else 'No'}"
            )
            result_label = tk.Label(
                grid_frame,
                text=result_text,
                font=("Helvetica", 14),
                fg="green" if is_correct else "red",
                justify="left",
            )
            result_label.grid(row=1, column=i, padx=20, pady=10)

        # Done button to return to welcome screen
        done_button = tk.Button(
            main_frame,
            text="Done",
            font=("Helvetica", 16),
            bg="blue",
            fg="white",
            command=self.show_welcome_screen,
        )
        done_button.place(relx=0.5, rely=0.9, anchor="center")

    def show_eye_selection_screen(self):
        """
        Show the eye selection screen for the user to indicate which eye they would like to take an image of.
        The "Submit" button will be greyed out until both eyes are captured.
        """
        self._clear_frame()

        # Prompt label
        prompt_label = tk.Label(self.current_frame, text="Select which eye to scan:", font=("Helvetica", 18))
        prompt_label.pack(pady=20)

        # Left Eye button, greyed out if already selected
        if not self.left_eye_taken:
            left_eye_button = tk.Button(
                self.current_frame,
                text="Left Eye",
                font=("Helvetica", 16),
                command=lambda: self.capture_photo_with_countdown("Left")
            )
            left_eye_button.pack(pady=10)
        else:
            left_eye_button = tk.Button(
                self.current_frame,
                text="Left Eye (Complete)",
                font=("Helvetica", 16),
                state="disabled",
                disabledforeground="gray"
            )
            left_eye_button.pack(pady=10)

        # Right Eye button, greyed out if already selected
        if not self.right_eye_taken:
            right_eye_button = tk.Button(
                self.current_frame,
                text="Right Eye",
                font=("Helvetica", 16),
                command=lambda: self.capture_photo_with_countdown("Right")
            )
            right_eye_button.pack(pady=10)
        else:
            right_eye_button = tk.Button(
                self.current_frame,
                text="Right Eye (Complete)",
                font=("Helvetica", 16),
                state="disabled",
                disabledforeground="gray"
            )
            right_eye_button.pack(pady=10)

        # Submit button, greyed out until both eyes are captured
        submit_button_state = "normal" if self.left_eye_taken and self.right_eye_taken else "disabled"
        submit_button = tk.Button(
            self.current_frame,
            text="Submit",
            font=("Helvetica", 16),
            state=submit_button_state,  # Enable only if both eyes are captured
            command=self.show_information_screen  # Placeholder for backend submission logic
        )
        submit_button.pack(pady=20)

        # Back button for returning to the welcome screen
        back_button = tk.Button(self.current_frame, text="Back", font=("Helvetica", 16), command=self.show_welcome_screen)
        back_button.pack(pady=20)

    def capture_photo_with_countdown(self, side):
        """
        Show a countdown screen for 5 seconds, capture the photo, display it briefly, 
        and return to the eye selection screen.
        """
        self._clear_frame()

        # Countdown label
        countdown_label = tk.Label(
            self.current_frame,
            text="Get ready! Capturing photo in:",
            font=("Helvetica", 18)
        )
        countdown_label.pack(pady=20)

        countdown_number_label = tk.Label(self.current_frame, text="5", font=("Helvetica", 36), fg="red")
        countdown_number_label.pack(pady=20)

        def update_countdown(seconds_left):
            if seconds_left > 0:
                countdown_number_label.config(text=str(seconds_left))
                self.current_frame.after(1000, update_countdown, seconds_left - 1)  # Call again after 1 second
            else:
                # Capture the photo after countdown finishes
                try:
                    capture_photo(side.lower())  # Call external capture_photo function

                    # Update flags based on which eye was captured
                    if side == "Left":
                        self.left_eye_taken = True
                    elif side == "Right":
                        self.right_eye_taken = True

                    # Display the captured photo briefly
                    self.display_captured_photo(side)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to capture {side} eye photo: {str(e)}")
                    self.show_eye_selection_screen()  # Return to selection screen in case of error

        update_countdown(3)  # Start countdown from 5 seconds

    def display_captured_photo(self, side):
        """
        Display the captured photo for 1-2 seconds before returning to the eye selection screen.
        """
        self._clear_frame()

        # Path to the captured photo
        photo_path = f"/home/RetinAi/Desktop/firmware/RetinAI-Firmware/src/vision/captured_photos/{side.lower()}_eye.jpg"

        try:
            # Load and display the captured image
            img = Image.open(photo_path).resize((400, 300))  # Resize for display
            photo = ImageTk.PhotoImage(img)

            img_label = tk.Label(self.current_frame, image=photo)
            img_label.image = photo  # Keep reference to avoid garbage collection
            img_label.pack(pady=20)

            success_label = tk.Label(
                self.current_frame,
                text=f"{side} eye photo captured successfully!",
                font=("Helvetica", 18),
                fg="green"
            )
            success_label.pack(pady=20)

            # Return to eye selection screen after 2 seconds
            self.current_frame.after(2000, self.show_eye_selection_screen)

        except FileNotFoundError:
            messagebox.showerror("Error", f"Photo not found: {photo_path}")
            self.show_eye_selection_screen()  # Return to selection screen in case of error

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
