'''
对智谱api打标的数据进行清洗，清洗后再拿image-cleaner优化下。
'''
import os

def remove_newlines(text):
    return text.replace('\n', ' ')

def clean_article(file_path):
    print(f"Processed file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        article = file.read()
        # 删除以"Overall"开始及其后面的内容
        cleaned_article = article.split("Overall,", 1)[0]
        cleaned_article = remove_newlines(cleaned_article)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_article)

def clean_articles_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            clean_article(file_path)

if __name__ == "__main__":
    folder_path = "your input folder"
    # 指定包含文章文件的目录路径
    articles_directory = "your input folder"
    clean_articles_in_directory(articles_directory)


