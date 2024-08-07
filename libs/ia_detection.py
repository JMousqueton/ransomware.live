import cv2
# Load the pre-trained Haar Cascade classifier for face detection 

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def check_image_for_face(image_path):
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