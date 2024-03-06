"""
This is a Python script for handling image names.

Author: luoqxi
Date: 2024/3/6
"""

import os


def check_duplicate_images(folder_path):

    print(f">>> Checking for duplicate images in {folder_path}")
    # Traverse through all the directories and subdirectories
    for root, dirs, files in os.walk(folder_path):
        # Create a dictionary to store the image names and their formats
        image_dict = {}

        # Iterate over the files in the current directory
        for file in files:
            # Check if the file is an image
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Get the file name without the extension
                file_name = os.path.splitext(file)[0]

                # Get the file format
                file_format = os.path.splitext(file)[1]

                # Check if the file name already exists in the dictionary
                if file_name in image_dict:
                    # Check if the file format is different
                    if file_format != image_dict[file_name]:
                        print(f"Duplicate image name with different format found: {file_name}{file_format} and {file_name}{image_dict[file_name]} in {root}")

                # Add the file name and format to the dictionary
                image_dict[file_name] = file_format
    print(f">>> Finished checking for duplicate images in {folder_path}")


if __name__ == "__main__":
    check_duplicate_images("your input folder")
