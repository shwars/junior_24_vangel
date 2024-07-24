from diffusers import DiffusionPipeline
import torch
import json

with open('prompts.json',encoding='utf-8') as f:
    prompts = json.load(f)

for e in [1000,2000,3000,4000]:
    pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    pipe.load_lora_weights(f"GorvitsArt/checkpoint-{e}/pytorch_lora_weights.safetensors")
    for p in prompts:
        image = pipe(f"{p['prompt']}, a drawing in annagortits style", num_inference_steps=25).images[0]
        image.save(f"results/{p['title'].replace(' ','_')}_{e}.png")