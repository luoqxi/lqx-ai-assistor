'''
使用预训练的模型生成图像，并将生成的图像保存到文件。
diffusers库请参考 https://huggingface.co/docs/diffusers/using-diffusers/conditional_image_generation
'''
import torch
from diffusers import StableDiffusionXLPipeline
from tqdm import tqdm 
from PIL import Image 
from compel import Compel, ReturnedEmbeddingsType
import hpsv2
import os

def convert_image_to_generation_width_height(width, height):
    # 定义标准尺寸
    height_dimensions = {
        '640, 1536': (640, 1536),
        '768, 1344': (768, 1344),
        '832, 1216': (832, 1216),
        '896, 1152': (896, 1152),
        '1024, 1024': (1024, 1024)
    }

    width_dimensions = {
        '1024, 1024': (1024, 1024),
        '1152, 896': (1152, 896),
        '1216, 832': (1216, 832),
        '1344, 768': (1344, 768),
        '1536, 640': (1536, 640)
    }

    if width > height:
        # 如果宽度大于高度，则以宽度为标准尺寸
        standard_dimensions = width_dimensions
    else:
        # 如果高度大于宽度，则以高度为标准尺寸
        standard_dimensions = height_dimensions

    # 计算原始图像的长宽比
    aspect_ratio = width / height

    # 找到最接近的标准纵横比
    closest_ratio = min(standard_dimensions.items(), key=lambda x: abs((x[1][0] / x[1][1]) - aspect_ratio))

    # 返回最接近的长宽比对应的尺寸
    return closest_ratio[1]
    

output_dir = "your output folder"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

input_dir = "your dataset folder"

model_path = "your pre-trained ckpt"

pipeline = StableDiffusionXLPipeline.from_single_file(
    model_path,variant="fp16", use_safetensors=True, 
    torch_dtype=torch.float16).to("cuda")

compel = Compel(tokenizer=[pipeline.tokenizer, pipeline.tokenizer_2] , text_encoder=[pipeline.text_encoder, pipeline.text_encoder_2], 
                returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED, requires_pooled=[False, True])

for subdir in tqdm(os.listdir(input_dir),position=0):
    subdir_path = os.path.join(input_dir, subdir)
    for file in tqdm(os.listdir(subdir_path),position=1):
        if file.endswith(".txt"):
            # 创建输出子目录
            output_subdir_path = os.path.join(output_dir, subdir)
            output_file_path = os.path.join(output_subdir_path, file.replace('.txt', '.jpg'))
            if not os.path.exists(output_subdir_path):
                os.mkdir(output_subdir_path)
            
            # 跳过现有图片
            if os.path.exists(output_file_path): continue
            # 读取文件
            prompt = ''
            file_path = os.path.join(subdir_path, file)

            image_path = file_path.replace('.txt', '.jpg')
            # print(image_path)
            ori_image = Image.open(image_path) 
            width_height = convert_image_to_generation_width_height(ori_image.width,ori_image.height)
            # print(width_height)
            # break
            with open(file_path, "r") as f:
                prompt = f.read()
                f.close()
            prompt = prompt.replace('\n', ' ')
            
            conditioning, pooled = compel(prompt)
            guidance_scale = 7
            steps = 30
            # 生成图片
            image = pipeline(prompt_embeds=conditioning, 
                             pooled_prompt_embeds=pooled, 
                             num_inference_steps=steps,
                             guidance_scale=guidance_scale,
                             width=width_height[0], 
                             height=width_height[1]
                             ).images[0]

            # image.show()
            
            image.save(output_file_path)

            # Tried HPSv2 compared to original image
            # generated result: 0.36572265625
            # original result: 0.2137451171875
            # as of this point, HPSv2 is able to evaluate images quality

            # generated_result = hpsv2.score(image, prompt, hps_version="v2.1")[0]
            # hpsv2.score(image, prompt, hps_version="v2.1")[0]
            # print(f'generated_result:{generated_result}')
            # image_path = file_path.replace('.txt', '.jpg')
            # original_result = hpsv2.score(image_path, prompt, hps_version="v2.1")[0]
            # print(f'original_result:{original_result}')
            # break
    # break
