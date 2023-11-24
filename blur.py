from PIL import Image, ImageFilter
import os
import sys

def blur_image(input_path, output_path, blur_radius):
    try:
        # Open the input image
        img = Image.open(input_path)
        
        # Apply Gaussian blur with the specified radius
        blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Get the directory and filename from the input path
        directory, filename = os.path.split(output_path)
        
        # Generate the new path for the blurred image
        output_path = os.path.join(directory,filename)
        
        # Save the blurred image to the output path
        blurred_img.save(output_path)
        
        print(f"Image blurred successfully and saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def rename_original_image(input_path):
    try:
        # Get the directory and filename from the input path
        directory, filename = os.path.split(input_path)
        
        # Generate the new name for the original image
        new_name = os.path.splitext(filename)[0] + "-ORIG.png"
        
        # Create the new path for the renamed original image
        new_path = os.path.join(directory, new_name)
        
        # Rename the original image
        os.rename(input_path, new_path)
        
        print(f"Original image renamed to {new_name}")
        return new_path
    except Exception as e:
        print(f"An error occurred while renaming the original image: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py input_image [blur_radius]")
        sys.exit(1)
    
    input_image_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        blur_radius = int(sys.argv[2])
    else:
        blur_radius = 5
    
    renamed_input_path = rename_original_image(input_image_path)
    
    if renamed_input_path:
        blur_image(renamed_input_path, input_image_path, blur_radius)
