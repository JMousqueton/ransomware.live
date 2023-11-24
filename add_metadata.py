import os
from PIL import Image

def add_metadata_to_png(directory, metadata):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            file_path = os.path.join(directory, filename)
            image = Image.open(file_path)

            # Add metadata to the image
            for key, value in metadata.items():
                image.info[key] = str(value)

            # Save the image to retain the metadata
            image.save(file_path)
            print(f"Added metadata to {filename}")

# Specify the directory where your PNG files are located
target_directory = "docs/screenshots"

# Specify the metadata you want to add (key-value pairs)
metadata_to_add = {
    "Author": "Ransomware.live",
    "Description": "This file bellow to Ransomware.live.",
    "CustomField": "(c) Ransomware.live"
}

add_metadata_to_png(target_directory, metadata_to_add)

