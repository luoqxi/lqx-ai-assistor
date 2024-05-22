"""
这个脚本的主要作用是处理图像，包括调整图像的大小和裁剪图像，以满足特定的需求。
首先，脚本定义了一个名为 process_image 的函数，该函数接收一个图像文件的路径和一个输出文件夹的路径。
这个函数首先打开图像文件，然后获取图像的原始宽度和高度。然后，它会检查图像的长边是否超过2048像素，
如果超过，就将长边限制在2048像素，并按比例调整短边的大小。如果没有超过2048像素，就保持原始大小不变。
接着，函数会将图像的大小调整为新的宽度和高度。然后，它会检查新的宽度和高度是否是8的倍数，如果不是，
就将其调整为最接近的8的倍数。然后，函数会将图像裁剪到新的宽度和高度，裁剪的方式是从中心开始。
最后，函数会将处理后的图像保存到输出文件夹，并打印一条消息表示图像已经被处理并保存。
在 main 函数中，脚本会检查输出文件夹是否存在，如果不存在，就创建它。然后，脚本会使用 ThreadPoolExecutor 
来并行处理所有的图像文件。脚本会遍历输入文件夹中的所有文件，对于每一个图像文件，都会提交一个任务到线程池，
调用 process_image 函数来处理这个图像。
在脚本的最后，定义了输入文件夹和输出文件夹的路径，并调用 main 函数来开始处理图像。
"""
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor

def process_image(file_path, output_folder):
    try:
        with Image.open(file_path) as img:
            original_width, original_height = img.size
            
            # Limit the longer side to a maximum of 2048 pixels
            if original_width > original_height:
                if original_width > 2048:
                    new_width = 2048
                    scale_factor = new_width / original_width
                    new_height = int(original_height * scale_factor)
                else:
                    new_width = original_width
                    new_height = original_height
            else:
                if original_height > 2048:
                    new_height = 2048
                    scale_factor = new_height / original_height
                    new_width = int(original_width * scale_factor)
                else:
                    new_width = original_width
                    new_height = original_height

            # Resize the image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop the shorter side to make it a multiple of 8
            if new_width % 8 != 0:
                new_width = (new_width // 8) * 8
            if new_height % 8 != 0:
                new_height = (new_height // 8) * 8

            # Center crop
            left = (img.width - new_width) // 2
            top = (img.height - new_height) // 2
            right = left + new_width
            bottom = top + new_height

            img = img.crop((left, top, right, bottom))

            # Save to the output folder
            output_path = os.path.join(output_folder, os.path.basename(file_path))
            img.save(output_path)
            print(f"Processed {file_path} and saved to {output_path}")

    except Exception as e:
        print(f"Failed to process {file_path}: {str(e)}")

def main(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Use ThreadPoolExecutor to process all images
    with ThreadPoolExecutor() as executor:
        # Walk through the directory tree
        for dirpath, dirnames, filenames in os.walk(input_folder):
            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    file_path = os.path.join(dirpath, filename)
                    output_path = os.path.join(output_folder, os.path.relpath(dirpath, input_folder))
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    executor.submit(process_image, file_path, output_path)

if __name__ == "__main__":
    input_folder = r'your input folder'  # Input folder path
    output_folder = r'your output folder'  # Output folder path
    main(input_folder, output_folder)

