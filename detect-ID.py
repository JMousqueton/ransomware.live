import cv2
import os

# Update the path to the directory containing the PNG files
directory_path = './docs/screenshots/posts/'

# Load the pre-trained Haar Cascade classifier for face detection (as an illustrative example)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to check a single image for an ID-like object
def check_image_for_id(image_path):
    # Attempt to load the image
    image = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image is None:
        print(f"Error loading image {image_path}. Check if the file exists and is a valid image.")
        return False  # Indicate that the image could not be processed

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect objects in the image (using face detection as an example)
    objects = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Check if any objects were detected
    if len(objects) > 0:
        return True  # Indicate that an ID-like object was detected
    else:
        return False  # Indicate that no ID-like objects were detected

# Iterate over all PNG files in the directory and check each for ID-like objects
for filename in os.listdir(directory_path):
    if filename.endswith(".png"):
        full_path = os.path.join(directory_path, filename)

        # Check the image for an ID-like object and print the result
        if check_image_for_id(full_path):
            print(f"An ID-like object detected in https://www.ransomware.live/screenshots/posts/{filename}")
        #else:
        #    print(f"No ID-like objects detected in {filename}")

