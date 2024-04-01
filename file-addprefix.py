# -*- coding: utf-8 -*-
import os

def add_prefix_to_files(folder_path, prefix):
    files = os.listdir(folder_path)
    for file in files:
        file_path = os.path.join(folder_path, file)       
        new_file_name = prefix + file
        new_file_path = os.path.join(folder_path, new_file_name)
        os.rename(file_path, new_file_path)        
        print(f"文件 {file} 重命名为 {new_file_name}")

folder_path = "/path/to/your/folder"
prefix = "your prefix_"

if __name__ == "__main__":
    add_prefix_to_files(folder_path, prefix)

