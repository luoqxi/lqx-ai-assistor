from diffusers import UNet2DConditionModel
import torch
from safetensors.torch import load_file, save_file

# local safetensors
model_path = "your safetensors path"
state_dict = load_file(model_path)
unet = UNet2DConditionModel.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", subfolder="unet", torch_dtype=torch.float16)
unet_state_dict = {k: v.half() for k, v in state_dict.items() if k.startswith("unet.")}
unet_state_dict = {k.replace("unet.", ""): v for k, v in unet_state_dict.items()}
unet.load_state_dict(unet_state_dict, strict=False)
# save unet safetensors
save_file(unet.state_dict(), "your safetensors path-UNET.safetensors")