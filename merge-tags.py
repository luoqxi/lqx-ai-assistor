import os

def concatenate_txt_files(directory_path, output_file):
    # 获取目录下所有以.txt结尾的文件
    txt_files = [file for file in os.listdir(directory_path) if file.endswith('.txt')]

    # 拼接所有.txt文件的内容
    concatenated_content = ""
    for txt_file in txt_files:
        file_path = os.path.join(directory_path, txt_file)
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            concatenated_content += file_content

    # 将拼接后的内容写入all.txt文件
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write(concatenated_content)

# 示例用法
directory_path = 'your input folder'    # 替换为您的目录路径
output_file = 'all.txt'

concatenate_txt_files(directory_path, output_file)