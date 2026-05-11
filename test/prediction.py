import torch
import requests
import joblib
import numpy as np
from huggingface_hub import hf_hub_download
from PIL import Image
from transformers import AutoProcessor, AutoModel

"""
See example at:
https://huggingface.co/nathanaelambert/svr50siglip320flico-05-2026/blob/main/README.md
"""
model_path = hf_hub_download("nathanaelambert/svr50siglip320flico-05-2026", "svr50_siglip320_model.joblib")
svr_model = joblib.load(model_path)
model_name = "google/siglip-base-patch16-224"
processor = AutoProcessor.from_pretrained(model_name)
siglip_model = AutoModel.from_pretrained(model_name)

urls = ['https://live.staticflickr.com/7800/47197763982_5ec8fd2b3d_n.jpg',
        'https://live.staticflickr.com/1509/24846544039_2310399be3_n.jpg'
]
labels = ['1921', '1966']
embeddings = []

for url in urls:
    image = Image.open(requests.get(url, stream=True).raw).convert('RGB')
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = siglip_model.get_image_features(**inputs)
    embedding = outputs.pooler_output[0].cpu().numpy().astype(np.float32)
    assert embedding.shape == (768,)
    embeddings.append(embedding)

X = np.stack(embeddings)
predicted_dates = [int(x) for x in svr_model.predict(X)]
print(predicted_dates)