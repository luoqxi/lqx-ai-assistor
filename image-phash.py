'''
利用感知哈希值（Perceptual Hash，pHash）给图片计算哈希值，找出重复的图片。
'''
import os
import shutil
import imagehash
from PIL import Image
from tqdm import tqdm
import concurrent.futures
import logging
import time


def calculate_hash(image_path, corrupt_folder, target_size=(256, 256)):
    try:
        with Image.open(image_path) as img:
            img = img.resize(target_size)
            hash_val = imagehash.phash(img)
        return image_path, hash_val, os.path.getsize(image_path), None
    except Exception as e:
        logging.error(f"无法处理图片 {image_path}: {e}")
        shutil.move(image_path, os.path.join(corrupt_folder, os.path.basename(image_path)))
        return image_path, None, 0, e


def find_duplicates(directory, hash_size=8):
    start_time = time.time()

    # 创建新的文件夹用于存放重复的和损坏的图片
    duplicate_folder = os.path.join(directory, "_duplicates")
    corrupt_folder = os.path.join(directory, "_corrupt")
    os.makedirs(duplicate_folder, exist_ok=True)
    os.makedirs(corrupt_folder, exist_ok=True)

    # 存储图片哈希值、路径和大小
    hashes = {}

    # 支持的图像格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

    # 遍历文件夹获取所有图片的路径
    image_paths = [os.path.join(dirpath, filename)
                   for dirpath, _, filenames in os.walk(directory)
                   for filename in filenames if filename.lower().endswith(image_extensions)]

    print('开始计算图片哈希值...')
    duplicate_count = 0
    corrupt_count = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(calculate_hash, image_path, corrupt_folder): image_path for image_path in image_paths}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(image_paths)):
            image_path = futures[future]
            try:
                _, hash_val, image_size, error = future.result()
                if error:
                    corrupt_count += 1
                elif hash_val is not None:
                    if hash_val in hashes:
                        # 比较当前图片和已存储的图片大小
                        saved_path, saved_size = hashes[hash_val]
                        if image_size > saved_size:
                            # 如果当前图片更大，则移动之前的图片到重复文件夹，并更新哈希表
                            duplicate_filename = f"{hash_val}_{os.path.basename(saved_path)}"
                            shutil.move(saved_path, os.path.join(duplicate_folder, duplicate_filename))
                            duplicate_count += 1
                            hashes[hash_val] = (image_path, image_size)
                        else:
                            # 如果当前图片更小，则移动当前图片
                            duplicate_filename = f"{hash_val}_{os.path.basename(image_path)}"
                            shutil.move(image_path, os.path.join(duplicate_folder, duplicate_filename))
                            duplicate_count += 1
                    else:
                        # 如果是第一次遇到该哈希值,则将其记录下来
                        hashes[hash_val] = (image_path, image_size)
            except Exception as e:
                logging.error(f"在处理文件时发生错误 {image_path}: {e}")

    elapsed_time = time.time() - start_time
    print(f'处理完成。找到并移动了 {duplicate_count} 张重复的图片和 {corrupt_count} 张损坏的图片,总耗时 {elapsed_time:.2f} 秒。')

if __name__ == "__main__":
    directory = "your input folder"

    logging.basicConfig(level=logging.ERROR)
    find_duplicates(directory)