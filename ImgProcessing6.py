"""
这是一个Python脚本,主要功能是批量处理图像文件,使用前请备份原图像。功能包括:
1.收集所有图像的大小信息
2.使用KMeans对图像进行聚类,得到代表性的几种尺寸
3.按照这几种代表性尺寸,对图像进行缩放和裁剪,使其总分辨率小于1088*1088，且长宽两边像素数均是32的倍数
4.将图像以100%质量转换为JPEG格式,同时计算图像裁剪后的面积损失比例
5.生成统计报告,包含图像尺寸分布、损失比例等信息
6.按损失比例对图像排序,输出损失比例最大的文件
7.删除非JPG和TXT格式的文件
8.删除像素数过小的图像
主要用到了os、shutil、PIL、sklearn、multiprocessing等模块,实现了图像的批量处理和统计分析等功能。
"""
import os
import collections
import shutil
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from pathlib import Path

def collect_dimensions(file):
    try:
        img = Image.open(file)
        width, height = img.size
        return (width, height, file)  # 返回文件路径
    except IOError:
        return None  # 如果文件不能被打开为图像，就跳过

def write_statistics(directory, labels, common_sizes, loss_ratios):
    # Check if all labels have corresponding sizes in common_sizes
    if set(labels) - set(range(len(common_sizes))):
        raise ValueError("Not all labels have corresponding sizes in common_sizes.")
    
    # Use collections.Counter to count the frequency of each size
    size_counts = collections.Counter(labels)
    total = len(labels)
    
    # Calculate size_ratios
    size_ratios = {size: count / total for size, count in size_counts.items()}

    # Find the most common size
    common_size = max(size_ratios, key=size_ratios.get)

    # Calculate statistics of loss ratios
    loss_ratios_values = [ratio for _, ratio in loss_ratios]
    avg_loss_ratio = np.mean(loss_ratios_values)
    min_loss_ratio = np.min(loss_ratios_values)
    max_loss_ratio = np.max(loss_ratios_values)
    std_loss_ratio = np.std(loss_ratios_values)

    # Sort all files by loss ratio in descending order
    sorted_files = sorted([(file, ratio) for file, ratio in loss_ratios], key=lambda x: x[1], reverse=True)
    
    # Create a list for the top 10 files with the largest loss ratio
    top_10_loss_files = sorted_files[:10]
    
    # Create a list for files with a loss ratio greater than 10%
    large_loss_files = [file_ratio for file_ratio in sorted_files if file_ratio[1] > 0.1]

    # Merge and deduplicate the two lists
    merged_files = list(dict.fromkeys(top_10_loss_files + large_loss_files))

    with open(directory / 'statistics.txt', 'w') as file:
        # Write general statistics to the file
        file.write("################ General Statistics ################\n")
        file.write(f"Total number of images: {total:,}\n")
        file.write(f"Most common size: {common_sizes[common_size]} (Ratio: {size_ratios[common_size]*100:.2f}%)\n")
        file.write("\n")

        # Write statistics of loss ratios
        file.write("################ Loss Ratios Statistics ################\n")
        file.write(f"Average area loss ratio: {avg_loss_ratio * 100:.2f}%\n")
        file.write(f"Min area loss ratio: {min_loss_ratio * 100:.2f}%\n")
        file.write(f"Max area loss ratio: {max_loss_ratio * 100:.2f}%\n")
        file.write(f"Standard deviation of area loss ratio: {std_loss_ratio * 100:.2f}%\n")
        file.write("\n")
        
        # Write statistics of sizes
        file.write("################ Sizes Statistics ################\n")
        file.write(f"{'Size':<10}{'Count':<10}{'Ratio (%)':<10}\n")
        # Sort sizes by ratio in descending order
        sorted_sizes = sorted(size_ratios.items(), key=lambda x: x[1], reverse=True)
        for size, ratio in sorted_sizes:
            count = size_counts[size]
            # Only write sizes with a count greater than 0
            if count > 0:
                file.write(f"{str(common_sizes[size]):<20}{count:<10,}{ratio * 100:<10.2f}\n")
        
        file.write("\nFiles with large loss ratio (Top 10 or >10%):\n")
        for filename, ratio in merged_files:
            file.write(f"File: {filename}, Loss ratio: {ratio * 100:.2f}%\n")

def compress_and_convert(args):
    file, common_sizes = args
    try:
        img = Image.open(file)
        max_pixels = 1088*1088

        def adjust_dimensions(width, height):
            # Ensure both dimensions are multiples of 32
            width = (width // 32) * 32
            height = (height // 32) * 32
            return width, height

        original_width, original_height = img.size  # Add this line to record original dimensions
        cropped_pixels = 0  # Add this line to record the total cropped pixels

        # Check if the image needs to be scaled
        if original_width * original_height > max_pixels:
            # Resize the image
            img.thumbnail((1088, 1088), Image.LANCZOS)

        width, height = img.size

        # Check if the image needs to be cropped
        if width * height > max_pixels:
            # Compute the number of pixels to be removed
            pixels_to_remove = width * height - max_pixels
            cropped_pixels += pixels_to_remove  # Update cropped pixels if the image is being cropped

            # Determine the side to be cropped
            if width > height:
                # Crop the width
                reduction = (pixels_to_remove // height) * 32
                left = reduction // 2
                right = width - reduction // 2
                img = img.crop((left, 0, right, height))
            else:
                # Crop the height
                reduction = (pixels_to_remove // width) * 32
                top = reduction // 2
                bottom = height - reduction // 2
                img = img.crop((0, top, width, bottom))

            # Update the dimensions for the next iteration
            width, height = img.size

        # Adjust dimensions to be multiple of 32 by cropping
        width, height = adjust_dimensions(width, height)
        left = (img.width - width) // 2
        top = (img.height - height) // 2
        right = (img.width + width) // 2
        bottom = (img.height + height) // 2

        # Compute the number of pixels to be removed
        pixels_to_remove = img.width * img.height - width * height
        cropped_pixels += pixels_to_remove  # Update cropped pixels if the image is being cropped

        img = img.crop((left, top, right, bottom))

        # Convert to 'YCbCr' and save as .jpg
        img = img.convert('YCbCr')
        new_filename = file.with_suffix('.jpg')  # Always save as .jpg
        img.save(new_filename, "JPEG", quality=100)  # Use Pillow's save method for JPEG encoding
        img.close()  # Close the image after processing

        # Update area loss ratio calculation with original dimensions
        loss_ratio = cropped_pixels / (original_width * original_height)

        return str(file), loss_ratio, (width, height)

    except IOError:
        return None  # If the file cannot be opened as an image, skip it

def remove_non_jpg_files(directory):
    for file in directory.rglob('*'):
        if file.suffix.lower() != '.jpg' and file.suffix.lower() != '.txt' and file.is_file():
            file.unlink()

def remove_small_images(directory):
    max_pixels = 0.85 * 1088 * 1088  # 计算总像素数比1088*1088小15%以上的像素数
    for file in directory.rglob('*.jpg'):
        with Image.open(file) as img:  # Use 'with' statement to ensure the file is properly closed
            if imgwidth * img.height < max_pixels:
                file.unlink()

def main(directory, n_clusters):
    directory = Path(directory)
    files = list(directory.rglob('*'))  # Use rglob to avoid unnecessary traversals

    small_images_folder = directory.parent / 'small_images'
    small_images_folder.mkdir(exist_ok=True)

    with tqdm(total=2, desc="Total progress", dynamic_ncols=True) as pbar:
        with Pool(cpu_count()) as p:
            with tqdm(total=len(files), desc='Collecting dimensions', dynamic_ncols=True) as pbar1:
                dimensions = []
                small_files = []  # 创建一个新列表存储小图片
                for i, result in enumerate(p.imap_unordered(collect_dimensions, files), 1):
                    if result is not None:
                        dim, file = result[:-1], result[-1]  # 分离出dimension和文件路径
                        dimensions.append(dim)
                        # 如果文件的像素小于1088*1088的85%，则添加至small_files列表
                        if dim[0] * dim[1] < 0.85 * 1088 * 1088:
                            shutil.copy2(file, small_images_folder)
                    pbar1.update()
                pbar.update()
        
        dimensions = [dim for dim in dimensions if dim is not None]  # Use list comprehension

        kmeans = KMeans(n_clusters=n_clusters, n_init='auto', random_state=0).fit(dimensions)
        common_sizes = kmeans.cluster_centers_

        with Pool(cpu_count()) as p:
            with tqdm(total=len(files), desc='Processing images', dynamic_ncols=True) as pbar2:
                results = list(p.imap_unordered(compress_and_convert, [(file, common_sizes) for file in files]))  # Store the results in a list first
                loss_ratios = [(filename, ratio) for filename, ratio, _ in results if filename is not None]
                new_dimensions = [(width, height) for _, _, (width, height) in results if width is not None]
                pbar2.update()
                pbar.update()

        loss_ratios = [ratio for ratio in loss_ratios if ratio is not None]

        write_statistics(directory, kmeans.labels_, new_dimensions, loss_ratios)  # Use new_dimensions instead of common_sizes

    # 在所有图片处理完成后，删除所有非jpg和非txt文件
    remove_non_jpg_files(directory)
    
    # 在所有图片处理完成后，删除像素数过小的图像
    remove_small_images(directory)

if __name__ == '__main__':
    main('your input folder', 12)