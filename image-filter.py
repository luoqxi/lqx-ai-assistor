import os
import shutil
from PIL import Image
from ultralytics import YOLO

def copy_images_based_on_conditions(source_directory, target_directory, non_target_directory, min_size=(768, 768)):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    if not os.path.exists(non_target_directory):
        os.makedirs(non_target_directory)

    # 加载预训练的YOLOv8n模型
    model = YOLO('yolov8n.pt')  # 使用轻量版的YOLOv8n模型

    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        # 检查图片尺寸
                        if img.size[0] >= min_size[0] and img.size[1] >= min_size[1]:
                            # 检测图片中是否有人物
                            results = model(img)
                            has_person = False
                            for result in results:
                                for bbox in result.boxes:
                                    if int(bbox.cls) == 0:  # '0' 类别是 'person'
                                        has_person = True
                                        break
                                if has_person:
                                    break

                            if has_person:
                                print(f"Copying {file_path} to {target_directory} (size: {img.size}, person detected)")
                                shutil.copy2(file_path, os.path.join(target_directory, file))
                            else:
                                print(f"Copying {file_path} to {non_target_directory} (size: {img.size}, no person detected)")
                                shutil.copy2(file_path, os.path.join(non_target_directory, file))
                        else:
                            print(f"Copying {file_path} to {non_target_directory} (size: {img.size}, too small)")
                            shutil.copy2(file_path, os.path.join(non_target_directory, file))

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    print("Finished filtering images.")
    
if __name__ == "__main__":
    source_directory = "D:\\AI\\Materials\\X"
    target_directory = "D:\\AI\\Materials\\GoodImages"
    non_target_directory = "D:\\AI\\Materials\\BadImages"
    copy_images_based_on_conditions(source_directory, target_directory, non_target_directory)
