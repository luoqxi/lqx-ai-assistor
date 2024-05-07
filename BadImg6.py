"""
这是一个Python程序,主要用来检测图像质量,其主要功能为:
1.使用PIL打开图像,并计算SSIM和FFT两种指标评估图像质量。
2.使用多进程并行处理大量图像,加速计算。
3.对指标进行归一化处理。
4.按质量得分排序图像,找到质量最差的前N张。
5.生成质量检测报告,列出质量最差图片及其各项指标。
6.将质量最差图片复制到结果目录。
7.绘制质量得分、SSIM和FFT曲线图。
8.日志记录错误图片。
所以该程序实现了针对大量图片的自动化质量检测与报告生成。
主要用到了PIL、OpenCV、scipy、scikit-learn、matplotlib等模块。
"""
import os
import cv2
import numpy as np
from tqdm import tqdm
import logging
from skimage.metrics import structural_similarity as ssim
from sklearn.preprocessing import MinMaxScaler
from shutil import copy
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial
from PIL import Image

logging.basicConfig(filename="image_processing.log", level=logging.INFO)

def compute_scores(image_path):
    try:
        # Use PIL to open the image and convert to grayscale
        img = Image.open(image_path).convert('L')
        img = np.array(img)  # Convert the image to a NumPy array

        reference = np.ones_like(img) * 255  # reference image, you may want to use a different one

        # Compute SSIM
        ssim_score = ssim(img, reference)

        # Compute Fourier Transform
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        fshift += 1e-8
        magnitude_spectrum = 20*np.log(np.abs(fshift))

        # Use the mean value of the magnitude spectrum as the quality score
        fft_score = np.mean(magnitude_spectrum)

        return image_path, ssim_score, fft_score
    except Exception as e:
        logging.error(f"Failed to compute quality for {image_path} with error {e}")
        return image_path, -1, -1

def check_directory(directory, n_worst):
    scores_dict = {}
    image_paths = []
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image_paths.append(os.path.join(foldername, filename))

    # Use multiprocessing to process images in parallel
    pool = Pool()
    for image_path, ssim_score, fft_score in tqdm(pool.imap_unordered(compute_scores, image_paths), total=len(image_paths), desc="Processing images"):
        scores_dict[image_path] = {'ssim': ssim_score, 'fft': fft_score}
    pool.close()
    pool.join()

    # Normalize scores
    ssim_scores = np.array([item['ssim'] for item in scores_dict.values()]).reshape(-1, 1)
    fft_scores = np.array([item['fft'] for item in scores_dict.values()]).reshape(-1, 1)

    # Stack ssim_scores and fft_scores horizontally
    scores = np.hstack((ssim_scores, fft_scores))

    scaler = MinMaxScaler()
    scores_normalized = scaler.fit_transform(scores)

    # Separate ssim_scores_normalized and fft_scores_normalized
    ssim_scores_normalized, fft_scores_normalized = np.hsplit(scores_normalized, 2)

    # Compute quality scores  
    # quality_scores = (ssim_scores_normalized + fft_scores_normalized) / 2
    # quality_scores = 0.1*ssim_scores_normalized + 0.9*fft_scores_normalized
    quality_scores = (ssim_scores_normalized + fft_scores_normalized) / 2
    sorted_scores = sorted(list(zip(scores_dict.keys(), quality_scores.flatten())), key=lambda x: x[1])

    # Create a directory to store the results
    result_dir = os.path.join(os.path.dirname(directory), 'LowQualityImages')
    os.makedirs(result_dir, exist_ok=True)

    # Create txt file for storing sorted images
    with open(os.path.join(result_dir, 'LowQualityImagesReport.txt'), 'w') as f:
        f.write(f"Image Quality Inspection Report\n")
        f.write(f"Directory inspected: {directory}\n")
        f.write(f"Total images inspected: {len(scores_dict)}\n")
        f.write(f"Number of worst quality images: {n_worst}\n\n")
        f.write(f"List of worst quality images:\n")
        for idx, score in enumerate(sorted_scores[:n_worst], start=1):  # Only write the first n_worst images
            f.write(f"\nImage {idx}:\n")
            f.write(f"\tPath: {score[0]}\n")
            f.write(f"\tQuality Score: {score[1]:.4f}\n")
            f.write(f"\tSSIM Score: {scores_dict[score[0]]['ssim']:.4f}\n")
            f.write(f"\tFFT Score: {scores_dict[score[0]]['fft']:.4f}\n\n")

    # Copy the worst quality images to the result directory
    for score in sorted_scores[:n_worst]:  # Only copy the first n_worst images
        dst = os.path.join(result_dir, os.path.basename(score[0]))
        copy(score[0], dst)

    ## Plot the scores
    plot_scores(sorted_scores, ssim_scores_normalized, fft_scores_normalized, quality_scores, result_dir)

def plot_scores(sorted_scores, ssim_scores_normalized, fft_scores_normalized, quality_scores, result_dir):
    fig, ax = plt.subplots()

    sorted_indices = np.argsort(quality_scores.flatten())  # Get the sorting indices

    x = range(len(sorted_scores))
    y1 = np.array(quality_scores.flatten().tolist())[sorted_indices]
    y2 = np.array(ssim_scores_normalized.flatten().tolist())[sorted_indices]
    y3 = np.array(fft_scores_normalized.flatten().tolist())[sorted_indices]

    ax.plot(x, y1, label='Quality Scores', color='blue', linestyle='-')
    ax.scatter(x, y2, s=2, label='SSIM Scores', color='green')
    ax.scatter(x, y3, s=2, label='FFT Scores', color='red')

    ax.set_xlabel('Image Index')
    ax.set_ylabel('Score')
    ax.set_title('Image Scores')
    ax.legend()

    ax.grid(True)  # Add grid lines

    ax.set_ylim(0, 1)

    plt.savefig(os.path.join(result_dir, 'image_scores.png'))

if __name__ == "__main__":
    source_dir = "your input folder"
    n_worst = 50
    check_directory(source_dir, n_worst)