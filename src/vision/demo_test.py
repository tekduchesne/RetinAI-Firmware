from demo_diagnoses import DemoClient
import time  # Import the time module

# Initialize the DemoClient
demo = DemoClient(images_dir='../../Embedded/raspi_raw', csv_dir='../../Embedded/test.csv')

# List of image filenames to send
image_filenames = ["0004.jpg", "0024.jpg", "0029.jpg", "3134.jpg", "4400.jpg", "1922.jpg", "1867.jpg", "1418.jpg", "3304.jpg", "1871.jpg"]

# Start timing
start_time = time.time()

# Send images and get results
try:
    results = demo.send_images_and_get_diagnosis(image_filenames)
    print("Diagnosis Results:", results)
except Exception as e:
    print("Error:", str(e))

# End timing
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Time taken to retrieve results: {elapsed_time:.2f} seconds")
