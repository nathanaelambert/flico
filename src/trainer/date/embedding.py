import pandas as pd
import torch
import requests
from PIL import Image
from transformers import AutoProcessor, AutoModel
import numpy as np

model_name = "google/siglip-base-patch16-224"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()

def siglip(url_n, size=320, vector_dimension=768):
    """Encode image URL with SigLIP model"""
    image = Image.open(requests.get(url_n, stream=True).raw).convert('RGB')
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    embedding = outputs.pooler_output[0].cpu().numpy()
    assert embedding.shape == (768,), f"Expected (768,), got {embedding.shape}"
    return embedding.astype(np.float32)
