import pandas as pd
import torch
import requests
import src.utils.colors as c

from PIL import Image
from transformers import AutoProcessor, AutoModel
import numpy as np

print(f"Loading HuggingFace model for siglip embedding...{c.GREY}")
model_name = "google/siglip-base-patch16-224"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()
print(f"{c.RESET}")

def siglip(df: pd.DataFrame)-> pd.DataFrame: 
    """Encode images URL with SigLIP model"""
    vector_dimension = 768
    url_column = 'url_n' #320px
    embedding_column = 'sig_lip_vect_n'
    df[embedding_column] = [None] * len(df)
    embeddings = []
    print(f"Embedding {len(df)} pictures with siglip...{c.GREY}")
    for index, row in df.iterrows():
        try:
            image = Image.open(requests.get(row[url_column], stream=True).raw).convert('RGB')
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
            embedding = outputs.pooler_output[0].cpu().numpy().astype(np.float32)
            assert embedding.shape == (vector_dimension,)
            embeddings.append(embedding.astype(np.float32))
            print('.', end='', flush=True)
        except Exception as exc:
            print(f"{c.RESET}\n{c.RED}X (row {index}: {exc}){c.RESET}{c.GREY}")
            embeddings.append(None)
    
    df[embedding_column] = embeddings
    print(f"\n{c.RESET}", flush=True)
    return df