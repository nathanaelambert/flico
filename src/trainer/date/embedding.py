import pandas as pd
import torch
import requests
import src.utils.colors as c

from PIL import Image
from tqdm import tqdm
import timeout_decorator
from transformers import AutoProcessor, AutoModel
import numpy as np


_BATCH_SIZE = 32
_TIMEOUT = 200

def siglip(df: pd.DataFrame, cache)-> pd.DataFrame: 
    """Encode images URL with SigLIP model"""
    print(f"Loading HuggingFace model for siglip embedding...{c.GREY}")
    model_name = "google/siglip-base-patch16-224"
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    print(f"{c.RESET}")
    df = df[df['sig_lip_vect_n'].isna()]
    print(f"Ignoring {c.RED}{len(df[df['url_n'].isna()])}{c.RESET} pictures with 'None' url_n")
    df = df[df['url_n'].notna()]
    if len(df) == 0:
        return df
    embedder = _make_siglip_embedder(processor, model, cache)
    with tqdm(total=len(df), desc="Siglip embed", unit="img") as pbar:
        for start in range(0, len(df), _BATCH_SIZE):
            batch_mask = df.index[start:start + _BATCH_SIZE]
            try:
                _process_batch(df, batch_mask, embedder)
            except TimeoutError:
                break
            finally:
                pbar.update(len(batch_mask))
    return df[df["sig_lip_vect_n"].notna()]

def _make_siglip_embedder(processor, model, cache):
    def _siglip_embedding(url):
        try:
            image = cache.get(url) # Image.open(requests.get(url, stream=True).raw).convert('RGB')
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
            embedding = outputs.pooler_output[0].cpu().numpy().astype(np.float32)
            assert embedding.shape == (768,)
            return embedding.astype(np.float32)
        except Exception as exc:
            print(f"{c.RESET}\n{c.RED}X [{url}]: ({exc}){c.RESET}{c.GREY}")
            return None
    return _siglip_embedding


@timeout_decorator.timeout(_TIMEOUT, timeout_exception=TimeoutError)
def _process_batch(df, batch_indices, embedder):

    df.loc[batch_indices, "sig_lip_vect_n"] = df.loc[batch_indices, "url_n"].apply(embedder)

