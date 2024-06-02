import os
from collections import defaultdict

def generate_image_gallery_markdown(directory, output_file):
    # Ensure the directory exists
    if not os.path.exists(directory):
        print("Directory does not exist.")
        return

    # Get the list of files in the directory
    files = os.listdir(directory)
    
    # Filter image files (assuming common image file extensions)
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = [file for file in files if file.endswith(image_extensions)]

    # Create a dictionary to hold lists of files by topic
    images_by_topic = defaultdict(list)

    for file in image_files:
        # Split the file name to get the topic
        topic = file.split('-')[0]
        images_by_topic[topic].append(file)

    # Create the Markdown structure
    markdown_content = "# Administration\n"
    markdown_content += "> Restricted area \n"

    for topic, images in images_by_topic.items():
        topic_name = topic.replace("_", " ").capitalize()
        markdown_content += "## {}\n".format(topic_name)
        markdown_content += "<table>\n"
        for i in range(0, len(images), 2):
            markdown_content += "  <tr>\n"
            markdown_content += "    <td><img src=\"/admin/{}\" alt=\"{}\" style=\"width:100%\"></td>\n".format(images[i], images[i])
            if i + 1 < len(images):
                markdown_content += "    <td><img src=\"/admin/{}\" alt=\"{}\" style=\"width:100%\"></td>\n".format(images[i + 1], images[i + 1])
            else:
                markdown_content += "    <td></td>\n"
            markdown_content += "  </tr>\n"
        markdown_content += "</table>\n"
        markdown_content += "\n"

    # Write the Markdown content to a file
    with open(output_file, "w") as md_file:
        md_file.write(markdown_content)

    print("Markdown file generated successfully.")

# Specify the directory you want to list files from
directory_path = "./docs/admin"
markdown_file = os.path.join(directory_path, "README.md")

generate_image_gallery_markdown(directory_path, markdown_file)