import pandas as pd
import torch
import requests
from PIL import Image
from transformers import AutoProcessor, AutoModel
import numpy as np


from src.trainer.db import photos_without_embedding

model_name = "google/siglip-base-patch16-224"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()

def encode_with_siglip(url_n, size=320, vector_dimension=768):
    """Encode image URL with SigLIP model"""
    image = Image.open(requests.get(url_n, stream=True).raw).convert('RGB')
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    embedding = outputs.pooler_output[0].cpu().numpy()
    assert embedding.shape == (768,), f"Expected (768,), got {embedding.shape}"
    return embedding.astype(np.float32)

def generate_embeddings(embedding_name: str):
    """Generate sig_lip_vect_n embeddings in batch for machine_learning_photo table"""
    photos = photos_without_embdedding("siglip320")
    print(f"Found {len(photos)} photos")
    pics_embedded = 0
    for idx, photo in photos.iterrows():
            try:
                embedding = encode_with_siglip(photo['url_n']).tolist()
                update_picture(id, owner_nsid, embedding_name, embedding)
                pics_saved += 1
            except Exception as e:
                print(f"{c.RED}Embedding {photo['id']}: {e}{c.RESET}")


       

if __name__ == "__main__":
    generate_sig_lip_embeddings("sig_lip_vect_n")
