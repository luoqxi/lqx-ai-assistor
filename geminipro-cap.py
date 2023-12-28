import os
import PIL.Image
import google.generativeai as genai
from tqdm import tqdm

api_key = 'your api key' # https://makersuite.google.com/app/apikey

IMAGE_FOLDER = 'your input folder'
OUTPUT_FOLDER = 'your output folder'

image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
cap_extension = ".txt"
Processed = 0
query = "describe the picture."

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

image_files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if
               os.path.splitext(f)[1].lower() in image_extensions]


genai.configure(api_key=api_key)

# safety_settings = [
#     {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_NONE'},
#     {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
#     {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
#     {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'}
# ]
# generation_config = {
#     'candidate_count': 1,
#     'stop_sequences': None,
#     'max_output_tokens': None,
#     'temperature': 0.7,
#     'top_p': None,
#     'top_k': None,
# }

# model = genai.GenerativeModel(model_name='gemini-pro-vision', safety_settings=safety_settings,
#     generation_config=generation_config)
model = genai.GenerativeModel('gemini-pro-vision')

Processing = 0

for image_file in tqdm(image_files, desc="Processing images"):
    Processing = Processing + 1
    if Processing >= Processed:
        try:
            img = PIL.Image.open(image_file)

            response = model.generate_content([query, img.convert('RGB')], stream=False)

            output_filename = os.path.splitext(os.path.basename(image_file))[0] + cap_extension
            output_file_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)

            print(f"Caption saved to {output_file_path}")
        except Exception as e:
            print(f"Error processing {image_file}: {e}: {response.prompt_feedback}")
            with open(OUTPUT_FOLDER + "\error_list.txt", 'a+', encoding='utf-8') as file:
                file.write(image_file + "\n")
            # move to error folder
            os.rename(image_file, os.path.join(os.path.dirname(image_file), "error", os.path.basename(image_file)))

