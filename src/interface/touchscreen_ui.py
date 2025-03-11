"""
RetinAI Touchscreen User Interface for Raspberry Pi 5

This script creates a simple graphical user interface (GUI) using tkinter.
The interface is designed for a touchscreen device allowing users to navigate
between screens, enter information, and interact with the application.

Features: (CHANGED)
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
from network.exampleClient import backendRequests
from network.exampleClientVariables import imagesLocation
import time
import random
import requests
from PIL import Image, ImageTk
import os

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

        # Reset flags for left and right eye capture
        self.left_eye_taken = False
        self.right_eye_taken = False

        # disable fullscreen for testing
        # self.root.attributes('-fullscreen', True)
        self._clear_frame()

        # Open and set assets
        bg_image = Image.open(BASE_PATH / "assets/start/Start Screen Background.png")
        start_button_image = Image.open(BASE_PATH / "assets/start/Start Scan Button.png")
        simulation_button_image = Image.open(BASE_PATH / "assets/start/Simulation Button.png")

        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.start_button_image = ImageTk.PhotoImage(start_button_image)
        self.simulation_button_photo = ImageTk.PhotoImage(simulation_button_image)

        # Set Canvas background image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        canvas.pack(fill="both", expand=True)

        # Set start button position and bind
        button_x, button_y = 640, 360
        canvas_button = canvas.create_image(button_x, button_y, image=self.start_button_image)
        def on_click(event):
            self.show_eye_selection_screen()
        canvas.tag_bind(canvas_button, "<Button-1>", on_click)

        # Set simulation button position and bind
        sim_button_x, sim_button_y = 1125, 650
        canvas_simulation_button = canvas.create_image(sim_button_x, sim_button_y, image=self.simulation_button_photo)
        def on_simulation_click(event):
            self.show_simulation_screen()
        canvas.tag_bind(canvas_simulation_button, "<Button-1>", on_simulation_click)

    def show_simulation_screen(self):
        """
        Show the simulation screen with six selectable images.
        """
        self._clear_frame()

        # Reset selected images
        self.selected_images = []

        # Open and set assets
        sim_bg_image = Image.open(BASE_PATH / "assets/simulation screen/simulation background.png")
        sim_next_image = Image.open(BASE_PATH / "assets/simulation screen/Next button.png")
        sim_back_image = Image.open(BASE_PATH / "assets/simulation screen/Back Button.png")
        sim_regresh_image = Image.open(BASE_PATH / "assets/simulation screen/Refresh Button.png")

        self.sim_bg_photo = ImageTk.PhotoImage(sim_bg_image)
        self.sim_next_photo = ImageTk.PhotoImage(sim_next_image)
        self.sim_back_photo = ImageTk.PhotoImage(sim_back_image)
        self.sim_refresh_photo = ImageTk.PhotoImage(sim_regresh_image)

        # Set Canvas background image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.sim_bg_photo, anchor="nw")
        canvas.pack(fill="both", expand=True)

        # Create next, back, and refresh buttons
        self.create_button(canvas, 1200, 660, self.sim_next_photo,self.submit_selected_images)
        self.create_button(canvas, 60, 60, self.sim_back_photo,self.show_welcome_screen)
        self.create_button(canvas, 60, 660, self.sim_refresh_photo,self.show_simulation_screen)

        # Define image_dir as a Path object (PiOS)
        # image_dir = Path('/home/RetinAi/Desktop/Embedded/raspi_raw')
        # Define image_dir as a Path object (Windows)
        image_dir = Path('../../Embedded/raspi_raw')

        # Randomly select 6 images from the directory
        try:
            image_file_names = random.sample(list(image_dir.glob("*.jpg")), 6)
        except ValueError:
            messagebox.showerror("Error", "Not enough images in the directory!")
            return

        # Initialize dictionaries to track buttons and their states
        self.image_buttons = {}

        # 2x3 Grid placement of random images
        button_width, button_height = 200, 200  # Button size
        padding_x, padding_y = 95, 80  # Padding between buttons
        start_x, start_y = 365, 260  # Starting position

        for i, image_file in enumerate(image_file_names):
            # Calculate position for each button in grid
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + padding_x)
            y = start_y + row * (button_height + padding_y)

            # Load and resize the image
            img = Image.open(image_file).resize((button_width, button_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # Create a button for the image directly on the canvas
            btn = tk.Button(
                canvas,
                image=photo,
                command=lambda f=image_file: self.select_image(f),
                relief="flat", bg="white"
            )
            btn.image = photo  # Keep a reference to avoid garbage collection

            # Place the button on the canvas at calculated coordinates
            canvas.create_window(x, y, window=btn)

            # Store the button in the dictionary for later updates
            self.image_buttons[image_file] = btn

            # Create a label for the image name and place it below the button
            label_text = image_file.name if hasattr(image_file, "name") else str(image_file)
            label = tk.Label(canvas, text=label_text, font=("Helvetica", 12), bg="white")
            canvas.create_window(x, y + button_height // 2 + 15, window=label)

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
        Show the results screen with images and their diagnosis results side by side
        """
        self._clear_frame()

        # Open and set assets
        sim_results_bg_image = Image.open(BASE_PATH / "assets/results screen/results background.png")
        sim_results_finish_image = Image.open(BASE_PATH / "assets/results screen/finish button.png")

        self.sim_background_bg_photo = ImageTk.PhotoImage(sim_results_bg_image)
        self.sim_finish_photo = ImageTk.PhotoImage(sim_results_finish_image)

        # Set Canvas background image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.sim_background_bg_photo, anchor="nw")
        canvas.pack(fill="both", expand=True)

        # Define positions and dimensions for images and labels
        image_width, image_height = 350, 350  # Image size
        padding_x, padding_y = 120, 20  # Padding between elements
        start_x, start_y = 405, 400  # Starting position for first image

        for i, result in enumerate(results):
            filename = result['filename']
            diagnosis = result['diagnosis']
            is_correct = result['is_correct']

            # Load and resize the image
            img_path = Path(self.demo_client.images_dir) / filename
            img = Image.open(img_path).resize((image_width, image_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # Calculate position for each image and label
            x = start_x + i * (image_width + padding_x)
            y = start_y

            # Create a button or label for the image directly on the canvas
            img_label = tk.Label(canvas, image=photo)
            img_label.image = photo  # Keep a reference to avoid garbage collection
            canvas.create_window(x, y, window=img_label)

            # Create a label for the diagnosis result below the image
            result_text = (
                f"Filename: {filename}\n"
                f"Diagnosis: {diagnosis}\n"
                f"Correct: {'Yes' if is_correct else 'No'}"
            )
            result_label = tk.Label(
                canvas,
                text=result_text,
                font=("Helvetica", 14),
                fg="green" if is_correct else "red",
                justify="left",
                bg="white"
            )
            canvas.create_window(x, y + image_height // 2 + 45, window=result_label)

        # Create finish button
        self.create_button(canvas, 1200, 660, self.sim_finish_photo,self.show_welcome_screen)

    def create_button(self, canvas, x, y, img, event_function=None, *args, **kwargs):
        button = canvas.create_image(x, y, image=img)
        if event_function is not None:
            canvas.tag_bind(button, "<Button-1>", lambda event: event_function(*args, **kwargs))
        return button

    def show_eye_selection_screen(self):
        """
        Show the eye selection screen for capturing left and right eye images.
        """
        self._clear_frame()

        # Open and set assets
        bg_select_eye_image = Image.open(BASE_PATH / "assets/eye select/Eye Selection screen.png")
        back_button_image = Image.open(BASE_PATH / "assets/eye select/Back Button.png")
        submit_button_image = Image.open(BASE_PATH / "assets/eye select/Submit.png")
        submit_button_disabled_image = Image.open(BASE_PATH / "assets/eye select/Submit.png")
        select_left_eye_image = Image.open(BASE_PATH / "assets/eye select/left eye.png")
        select_left_eye_disabled_image = Image.open(BASE_PATH / "assets/eye select/left eye disabled.png")
        select_right_eye_image = Image.open(BASE_PATH / "assets/eye select/right eye.png")
        select_right_eye_disabled_image = Image.open(BASE_PATH / "assets/eye select/right eye disabled.png")

        self.bg_select_eye_image = ImageTk.PhotoImage(bg_select_eye_image)
        self.back_button_image = ImageTk.PhotoImage(back_button_image)
        self.submit_button_image = ImageTk.PhotoImage(submit_button_image)
        self.submit_button_disabled_image = ImageTk.PhotoImage(submit_button_disabled_image)
        self.select_left_eye_image = ImageTk.PhotoImage(select_left_eye_image)
        self.select_left_eye_disabled_image = ImageTk.PhotoImage(select_left_eye_disabled_image)
        self.select_right_eye_image = ImageTk.PhotoImage(select_right_eye_image)
        self.select_right_eye_disabled_image = ImageTk.PhotoImage(select_right_eye_disabled_image)

        # Set Canvas background image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.bg_select_eye_image, anchor="nw")
        canvas.pack(fill="both", expand=True)

        # Set start button position and bind
        back_b_x, back_b_y = 80, 75
        l_b_x, l_b_y = 380, 400
        r_b_x, r_b_y = 900, 400
        s_b_x, s_b_y = 1200, 650
        
        self.create_button(canvas, back_b_x, back_b_y, self.back_button_image, self.show_welcome_screen)

        # Left Eye button
        if not self.left_eye_taken:
            self.create_button(canvas, l_b_x, l_b_y, self.select_left_eye_image, self.capture_photo_with_countdown, "Left")
        else:
            self.create_button(canvas, l_b_x, l_b_y, self.select_left_eye_disabled_image)

        # Right Eye button
        if not self.right_eye_taken:
            self.create_button(canvas, r_b_x, r_b_y, self.select_right_eye_image, self.capture_photo_with_countdown, "Right")
        else:
            self.create_button(canvas, r_b_x, r_b_y, self.select_right_eye_disabled_image)

        # Submit button, greyed out until both eyes are captured
        if self.left_eye_taken and self.right_eye_taken:
            self.create_button(canvas, s_b_x, s_b_y, self.submit_button_image, self.submit_images_and_show_results)
        else:
            self.create_button(canvas, s_b_x, s_b_y, self.submit_button_disabled_image)

    def capture_photo_with_countdown(self, side):
        """
        Show a countdown screen for 5 seconds, capture the photo, display it briefly, 
        and return to the eye selection screen.
        """
        self._clear_frame()

        bg_count_down_image = Image.open(BASE_PATH / "assets/timer screen/Timer Background.png")
        self.bg_count_down_image = ImageTk.PhotoImage(bg_count_down_image)

        # Set Canvas background image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.bg_count_down_image, anchor="nw")
        canvas.pack(fill="both", expand=True)

        countdown_text_id = canvas.create_text(640, 450, text="5", font=("M Plus 1", 150), fill="white")

        def update_countdown(seconds_left):
            if seconds_left > 0:
                canvas.itemconfig(countdown_text_id, text=str(seconds_left))
                self.current_frame.after(1000, update_countdown, seconds_left - 1)  # Call again after 1 second
            else:
                # Capture the photo after countdown finishes
                try:
                    # Define filename based on side of the eye
                    filename = f"1_{side.lower()}.jpg"
                    filepath = f"/home/RetinAi/Desktop/firmware/RetinAI-Firmware/src/vision/captured_photos/{filename}"

                    # Check if a file with the same name exists and remove it
                    file_path = Path(filepath)
                    if file_path.exists():
                        print(f"Existing file found: {filepath}. It will be overwritten.")
                        file_path.unlink()  # Delete the existing file

                    # Call external capture_photo function with side as an argument
                    capture_photo(side.lower())  # Ensure `capture_photo` uses consistent naming

                    # Update flags based on which eye was captured
                    if side == "Left":
                        self.left_eye_taken = True
                    elif side == "Right":
                        self.right_eye_taken = True

                    # Display the captured photo briefly
                    self.display_captured_photo(filepath)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to capture {side} eye photo: {str(e)}")
                    self.show_eye_selection_screen()  # Return to selection screen in case of error

        update_countdown(3)  # Start countdown from 3 seconds

    def display_captured_photo(self, filepath):
        """
        Display the captured photo for 1-2 seconds before returning to the eye selection screen.
        """
        self._clear_frame()

        # Load background image and convert it to a PhotoImage for Tkinter
        bg_picture_taken_image = Image.open(BASE_PATH / "assets/picture taken/picture taken.png")
        self.bg_picture_taken_image = ImageTk.PhotoImage(bg_picture_taken_image)

        # Create a canvas with the desired dimensions
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        # Place the background image at the top-left corner
        canvas.create_image(0, 0, image=self.bg_picture_taken_image, anchor="nw")
        canvas.pack(fill="both", expand=True)

        try:
            # Load the captured image and resize it for display
            img = Image.open(filepath).resize((500, 400))
            self.captured_photo = ImageTk.PhotoImage(img)

            # Create the captured photo on the canvas, centered
            canvas.create_image(655 , 400, image=self.captured_photo, anchor="center")

            # Return to eye selection screen after 2 seconds
            self.current_frame.after(2000, self.show_eye_selection_screen)

        except FileNotFoundError:
            messagebox.showerror("Error", f"Photo not found: {filepath}")
            self.show_eye_selection_screen()  # Return to selection screen in case of error

    def submit_images_and_show_results(self):
        """
        Submit captured images to the backend API and display results.
        """
        try:
            # Send POST request with both images
            response = backendRequests("post")  # Call postRequest() from exampleClient.py
            
            # Check response status
            if response.status_code == 200:
                # Parse JSON response
                results = response.json()  # Convert JSON response to Python dictionary
                
                # Extract filenames of captured images from the directory
                image_files = os.listdir(imagesLocation)
                image_paths = [os.path.join(imagesLocation, img) for img in image_files]
                
                # Show results screen with images and diagnosis
                self.show_results_screen(results)
            else:
                messagebox.showerror("Error", f"Failed to get results: {response.status_code}")
        
        except requests.ConnectionError as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server:\n{str(e)}")
        except requests.HTTPError as e:
            messagebox.showerror("HTTP Error", f"Server returned an error:\n{str(e)}")
        except FileNotFoundError as e:
            messagebox.showerror("File Error", f"File not found:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    def show_results_screen(self, results):
        """
        Display submitted images and their respective diagnosis results side by side
        """
        self._clear_frame()

        results_bg_image = Image.open(BASE_PATH / "assets/results screen/results background.png")
        finish_button_image = Image.open(BASE_PATH / "assets/results screen/finish button.png")

        self.results_bg_photo = ImageTk.PhotoImage(results_bg_image)
        self.finish_button_photo = ImageTk.PhotoImage(finish_button_image)

        # Set Canvas background image
        canvas = tk.Canvas(self.current_frame, width=1280, height=720)
        canvas.create_image(0, 0, image=self.results_bg_photo, anchor="nw")
        canvas.pack(fill="both", expand=True)

        # Define positions and dimensions for images and labels
        image_width, image_height = 350, 350  # Image size
        padding_x, padding_y = 120, 20  # Padding between elements
        start_x, start_y = 405, 400  # Starting position for first image

        # Display first two images from results
        for i, image_info in enumerate(results["image_Info"][:2]):
            filename = image_info["name"]
            eye_side = image_info["eyeSide"]
            prediction = image_info["prediction"]
            selected = image_info["selectedForDisp"]

            # Load and resize the image
            img_path = Path(imagesLocation) / filename
            img = Image.open(img_path).resize((image_width, image_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # Calculate position for each image and label
            x = start_x + i * (image_width + padding_x)
            y = start_y

            # Create image label directly on canvas
            img_label = tk.Label(canvas, image=photo)
            img_label.image = photo
            canvas.create_window(x, y, window=img_label)

            # Create info label below image
            result_text = ("")
            if prediction:
                result_text = (
                    f"{filename}\n"
                    f"Prediction: {prediction}\n"
                )
            else:
                result_text = (
                    f"{filename}\n"
                    f"Prediction: Inconclusive\n"
                )
            result_label = tk.Label(
                canvas,
                text=result_text,
                font=("Helvetica", 14),
                fg="black",  # White text color
                justify="center",
                bg="white"  # Transparent background
            )
            canvas.create_window(x, y + image_height // 2 + 45, window=result_label)

        # Create finish button
        self.create_button(canvas, 1200, 660, self.finish_button_photo, self.show_welcome_screen)

    def show_success_screen(self):
        """
        Show success screen if both images have been captured.
        """
        self._clear_frame()

        success_label = tk.Label(self.current_frame, text="Both images captured successfully!", font=("Helvetica", 18))
        success_label.pack(pady=20)

        next_button = tk.Button(self.current_frame, text="View Results", font=("Helvetica", 16), command=self.show_information_screen)
        next_button.pack(pady=20)

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
