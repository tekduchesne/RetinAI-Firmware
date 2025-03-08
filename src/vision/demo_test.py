from demo_diagnoses import DemoClient

demo = DemoClient(images_dir='../../data/raspi_raw', csv_dir='../../data/test.csv')

image_filenames = ["0004.jpg", "0024.jpg", "0029.jpg"]

# Send images and get results
try:
    results = demo.send_images_and_get_diagnosis(image_filenames)
    print("Diagnosis Results:", results)
except Exception as e:
    print("Error:", str(e))
