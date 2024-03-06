"""
This script is used to clean up the image tags in the dataset.
It removes the unnecessary prefix of the image tags.
"""
import os
import re


def contains_chinese(text):
    chinese_pattern = re.compile('[\u4e00-\u9fa5]')
    return bool(chinese_pattern.search(text))


def is_empty_file(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) == 0


def move_to_error_folder(file_path):
    os.rename(file_path, os.path.join(os.path.dirname(file_path),
                                      "error", os.path.basename(file_path)))


def process_txt_file(file_path):
    if is_empty_file(file_path):
        print(f'The file {file_path} is empty.')
        move_to_error_folder(file_path)
    else:
        content = ''
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError as e:
            print(f"file_path: {file_path} UnicodeDecodeError: {e}")
            move_to_error_folder(file_path)

        content = content.lstrip()

        if contains_chinese(content):
            print(f"File contains Chinese characters and will not be processed: {file_path}")
            move_to_error_folder(file_path)
        else:
            prefixes = ['The image shows', 'The photo shows', 'The picture shows',
                        'The image showcases', 'The image depicts', 'The image features',
                        'The image captures',
                        'This image shows', 'This photo shows', 'This picture shows',
                        'This image showcases', 'This image depicts', 'This image features',
                        'this image captures']
            for prefix in prefixes:
                if content.startswith(prefix):
                    content = content[len(prefix):].lstrip()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        print(f"Processed file: {file_path}")


def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                process_txt_file(file_path)


if __name__ == "__main__":
    folder_path = "your input folder"
    process_folder(folder_path)
