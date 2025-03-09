# api_client.py
import requests
import os
import pandas as pd

class DemoClient:
    def __init__(self, kiosk_id='A1', request_url='http://3.12.41.57:8000/', images_dir='testImages', csv_dir='csv'):
        """
        Initialize the ApiClient with kiosk_id, API endpoint URL, and images directory.
        """
        self.kiosk_id = kiosk_id
        self.request_url = request_url
        self.images_dir = images_dir
        self.csv_dir = csv_dir

    def send_images_and_get_diagnosis(self, image_filenames):
        """
        Send selected images to the API, get the diagnosis, and compare with true labels.
        
        Args:
            image_filenames (list of str): List of image filenames to send.

        Returns:
            list of dict: A list of dictionaries containing the diagnosis and whether it matches the true label.
        """
        if not image_filenames:
            raise ValueError("At least one image must be provided.")

        # Prepare the images for the POST request
        files = []
        for image_filename in image_filenames:
            image_path = os.path.join(self.images_dir, image_filename)
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            files.append(('images', (image_filename, open(image_path, 'rb'), 'image/jpeg')))

        # Send the POST request
        full_url = f"{self.request_url}/eye_evaluation/{self.kiosk_id}"
        response = requests.post(full_url, files=files)

        if response.status_code != 200:
            raise Exception(f"API request failed with status code: {response.status_code}")

        # Get the diagnosis from the API response
        diagnosis = response.json()

        # Load the true labels from the CSV file
        try:
            test_df = pd.read_csv(self.csv_dir)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_dir}")

        # Compare each image's diagnosis with the true label
        results = []
        for image_filename in image_filenames:
            # Get the true label for the image
            true_label = test_df.loc[test_df['fundus'] == image_filename, 'types'].values
            if len(true_label) == 0:
                raise ValueError(f"True label not found for image: {image_filename}")
            true_label = true_label[0]

            # Get the diagnosis for the image from the image_Info list
            image_info = next((info for info in diagnosis['image_Info'] if info['name'] == image_filename), None)
            if image_info is None:
                raise ValueError(f"Diagnosis not found for image: {image_filename}")

            # Map API prediction to 0 (Normal) or 1 (Glaucoma)
            api_prediction = 0 if image_info['prediction'] == 'Normal' else 1

            # Compare the diagnosis with the true label
            is_correct = bool(api_prediction == true_label)

            # Append both diagnosis and correctness to results
            results.append({
                "filename": image_filename,
                "diagnosis": image_info['prediction'],  # "Normal" or "Glaucoma"
                "is_correct": is_correct
            })

        return results

