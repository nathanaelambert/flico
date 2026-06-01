import pandas as pd
import torch
import requests
import src.utils.colors as c

from PIL import Image
from tqdm import tqdm
import timeout_decorator
from transformers import AutoProcessor, AutoModel
import numpy as np

from ..db import update_ml_photo

_BATCH_SIZE = 512
_TIMEOUT = 2000

def siglip(df: pd.DataFrame, cache): 
    """Encode images URL with SigLIP model"""
    print(f"Loading HuggingFace model for siglip embedding...{c.GREY}")
    model_name = "google/siglip-base-patch16-224"
    processor = AutoProcessor.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {c.BLUE}{device}{c.GREY}")
    model = AutoModel.from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    print(f"{c.RESET}")
    df = df[df['sig_lip_vect_n'].isna()]
    print(f"Ignoring {c.RED}{len(df[df['url_n'].isna()])}{c.RESET} pictures with 'None' url_n")
    df = df[df['url_n'].notna()]
    if len(df) == 0:
        return df
    with tqdm(total=len(df), desc="Siglip embed", unit="img") as pbar:
        for start in range(0, len(df), _BATCH_SIZE):
            batch_mask = df.index[start:start + _BATCH_SIZE]
            batch_df = df.loc[batch_mask]
            try:
                _process_batch(df, batch_df, model, processor, cache, device)
            except TimeoutError:
                print("timeout")
                break
            finally:
                pbar.update(len(batch_mask))

@timeout_decorator.timeout(_TIMEOUT, timeout_exception=TimeoutError)
def _process_batch(df, batch_df, model, processor, cache, device):
    urls = batch_df["url_n"].tolist()
    images = cache.get_images(urls, download_missing=True, fast_cache=False, disk_save=False, silent=False)
    embeddings = _siglip_embeddings(images, processor, model, device)
    batch_df["sig_lip_vect_n"] = embeddings
    updated_rows = batch_df[batch_df["sig_lip_vect_n"].notna()
    ]
    if len(updated_rows):
        update_ml_photo(updated_rows, "sig_lip_vect_n")


def _siglip_embeddings(images, processor, model, device):
    valid_positions = []
    valid_images = []
    for i, img in enumerate(images):
        if img is not None:
            valid_positions.append(i)
            valid_images.append(img)
    if not valid_images:
        return [None] * len(images)
    try:
        inputs = processor(images=valid_images, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.inference_mode():
            outputs = model.get_image_features(**inputs)
        embeddings = outputs.pooler_output.cpu().numpy().astype(np.float32)
        result = [None] * len(images)
        for pos, emb in zip(valid_positions, embeddings):
            assert emb.shape == (768,)
            result[pos] = emb
        return result
    except Exception as exc:
        print(f"{c.RESET}\n{c.RED} batch failed: ({exc}){c.RESET}{c.GREY}")
        return [None] * len(images)

