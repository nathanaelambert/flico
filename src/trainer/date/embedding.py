import pandas as pd
import torch
import requests
import src.utils.colors as c

from PIL import Image
from transformers import AutoProcessor, AutoModel
import numpy as np

def make_siglip_embedder(processor, model):
    def _siglip_embedding(url):
        try:
            image = Image.open(requests.get(url, stream=True).raw).convert('RGB')
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
            embedding = outputs.pooler_output[0].cpu().numpy().astype(np.float32)
            assert embedding.shape == (768,)
            print('.', end='', flush=True)
            return embedding.astype(np.float32)
        except Exception as exc:
            print(f"{c.RESET}\n{c.RED}X ({exc}){c.RESET}{c.GREY}")
            return None
    return _siglip_embedding

def siglip(df: pd.DataFrame)-> pd.DataFrame: 
    """Encode images URL with SigLIP model"""
    print(f"Loading HuggingFace model for siglip embedding...{c.GREY}")
    model_name = "google/siglip-base-patch16-224"
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    print(f"{c.RESET}")
    df = df[df['sig_lip_vect_n'].isna()]
    if len(df) == 0:
        return df
    df['sig_lip_vect_n'] = df['url_n'].apply(make_siglip_embedder(processor, model))
    print(f"\n{c.RESET}", flush=True)
    return df