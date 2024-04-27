'''
从特定目录下的Parquet文件中提取图像和文本数据，并将它们分别保存为JPEG和TXT文件。
'''
import os
import pandas as pd
from PIL import Image
import io

parquet_directory = 'your input folder'
output_directory = 'your output folder'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

for i in range(7):
    file_path = os.path.join(parquet_directory, f'train-0000{i}-of-00007.parquet')
    
    df = pd.read_parquet(file_path)
    
    for index, row in df.iterrows():
        image_data = row['image']  # 图片数据在'image'列中
        caption = row['caption']   # 文本数据在'caption'列中
        
        if isinstance(image_data, dict) and 'bytes' in image_data:
            image_bytes = image_data['bytes']
        else:
            print(f"Skipping index {index}: image data is not in the expected format.")
            continue
        
        image = Image.open(io.BytesIO(image_bytes))
        image_filename = f'image_{i}_{index}.jpg'  # 修改文件扩展名为.jpg
        image_path = os.path.join(output_directory, image_filename)
        
        image.save(image_path, format='JPEG', quality=100)
        
        text_filename = f'image_{i}_{index}.txt'
        text_path = os.path.join(output_directory, text_filename)
        with open(text_path, 'w', encoding='utf-8') as text_file:
            text_file.write(caption)

print("所有文件已提取并保存。")