'''
使用ZhipuAI的API来对图像进行打标，并将打标结果保存到文本文件中。
需要安装依赖库: pip install zhipuai
需要申请ZhipuAI的APIKey，申请地址：https://open.bigmodel.cn/
'''
import os
import base64
from zhipuai import ZhipuAI

# 密钥
api_key = "your api key"  # 填写自己的APIKey
client = ZhipuAI(api_key=api_key)

# 打标文件路径
output_folder_path = 'your dataset folder'  # 注意复制的路径中的\要改为/


# 获取所有图片文件路径
def get_all_image_paths(directory):
    image_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    return image_paths


# 将图片转换为Base64编码
def image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# 保存分析结果到txt文件
def save_to_txt(file_name, content):
    txt_file_path = os.path.splitext(file_name)[0] + '.txt'
    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(content)
    print(f"文件 {txt_file_path} 已保存。")


# 打标并保存结果
def start_tags(file_dir):
    image_paths = get_all_image_paths(file_dir)
    for image_path in image_paths:
        # 检查对应的txt文件是否已存在，如果存在则跳过打标
        txt_file_path = os.path.splitext(image_path)[0] + '.txt'
        if os.path.exists(txt_file_path):
            print(f"文件 {txt_file_path} 已存在，跳过打标。")
            continue

        print(image_path, '开始打标')
        image_base64 = image_to_base64(image_path)
        response = client.chat.completions.create(
            model="glm-4v",  # 填写需要调用的模型名称
            messages=[
                {"role": "user",
                 "content": [
                     {
                         "type": "text",
                         "text": "请用英文详细描述这张图像。不要使用任何中文，不要分段落。"
                     },
                     {
                         "type": "image_url",
                         "image_url": {
                             "url": image_base64
                         }
                     }
                 ]
                 },
            ],
        )
        print(image_path, '打标结束')
        content = response.choices[0].message.content
        print(content)
        save_to_txt(image_path, content)


if __name__ == "__main__":
    # 打标逻辑
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
    start_tags(output_folder_path)
