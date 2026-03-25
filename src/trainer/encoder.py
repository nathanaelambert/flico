import pandas as pd
import torch
import requests
from PIL import Image
from transformers import AutoProcessor, AutoModel
from sqlalchemy import text
import numpy as np

from src.db.connector import get_engine

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

def generate_sig_lip_embeddings():
    """Generate sig_lip_vect_n embeddings in batch for machine_learning_photo table"""
    engine = get_engine('trainer')
    get_query = """
    SELECT mlp.owner_nsid, mlp.id, p.url_n
    FROM machine_learning_photo mlp
    JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
    WHERE mlp.sig_lip_vect_n IS NULL
    """
    photos = pd.read_sql_query(get_query, engine)
    print(f"Found {len(photos)} photos")
    for idx, row in photos.iterrows():
        try:
            embedding = encode_with_siglip(row['url_n'])
            update_query = text("""
            UPDATE machine_learning_photo 
            SET sig_lip_vect_n = :embedding
            WHERE owner_nsid = :owner_nsid AND id = :id
        """)
            with engine.connect() as conn:
                conn.execute(update_query, {
                    'embedding': embedding.tolist(),
                    'owner_nsid': row['owner_nsid'],
                    'id': row['id']
                })
                conn.commit()
            print(f"{idx} : url: {row['url_n']} was embedded")
        except Exception as e:
            print(f"❌ owner_nsid = '{row['owner_nsid']}' AND id = {row['id']}\n {e}")
            continue

if __name__ == "__main__":
    generate_sig_lip_embeddings()
