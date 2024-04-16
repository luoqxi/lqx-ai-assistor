'''
关键字检索txt并移动文档和对应图片
'''
import os
import shutil
from concurrent.futures import ThreadPoolExecutor


# 定义源文件夹和目标文件夹路径
source_folder = r''  # 示例路径，需要根据实际情况进行修改
target_folder = r''  # 示例路径，需要根据实际情况进行修改
keywords = ['aerial view', 'aerial']  # 添加你的关键字列表

# 确保目标文件夹存在
os.makedirs(target_folder, exist_ok=True)

processed_files = 0
error_files = 0


def process_file(file_info):
    global processed_files, error_files
    subdir, file = file_info
    if file.lower().endswith('.txt'):
        file_path = os.path.join(subdir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read().lower()
                if any(keyword.lower() in file_content for keyword in keywords):
                    relative_dir = os.path.relpath(subdir, source_folder)
                    target_subdir = os.path.join(target_folder, relative_dir)
                    os.makedirs(target_subdir, exist_ok=True)

                    shutil.move(file_path, os.path.join(target_subdir, os.path.basename(file)))

                    base_name = os.path.splitext(file)[0]
                    for img_ext in ['.jpg', '.png']:
                        img_file = base_name + img_ext
                        img_path = os.path.join(subdir, img_file)
                        if os.path.exists(img_path):
                            shutil.move(img_path, os.path.join(target_subdir, img_file))
                            processed_files += 1
                            break
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            error_files += 1

all_files = [(subdir, file) for subdir, dirs, files in os.walk(source_folder) for file in files if file.endswith('.txt')]


with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    executor.map(process_file, all_files)

print(f'完成，共处理{processed_files}个文件，遇到{error_files}个错误。')
