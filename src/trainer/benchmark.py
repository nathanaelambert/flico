"""
adapted from : https://gitlab.epfl.ch/rcp/aiaas/client-usage-examples/-/blob/main/openai-image-understanding.py
"""
import os
from dotenv import load_dotenv
import base64
import requests
from openai import OpenAI
from typing import Optional
import json

def encode_image(image_url: str) -> Optional[str]:   
    try:
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.0; rv:42.0) Gecko/20100101 Firefox/42.0"
        response = requests.get(image_url, headers={"User-Agent": user_agent})
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return base64.b64encode(response.content).decode("utf-8")
    except requests.RequestException as e:
        print(f"Error during image download: {e}")
        return None

def predict_date_taken(client, image_url: str) -> int:
    base64_image = encode_image(image_url)
    if base64_image is not None:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": """
                        Predict the year this image was taken as a four-digit integer (e.g., 2020). 
                        Respond ONLY with valid JSON: {\"year\": <YEAR>}
                        Examples:
                        - If 1995: {\"year\": 1995}
                        - If 2023: {\"year\": 2023}
                        No explanations or extra text.""",
                    },
                ],
            },
        ]
        try:
            completion = client.chat.completions.create(
                model="Qwen/Qwen3-VL-235B-A22B-Thinking",
                messages=messages,
                response_format={"type": "json_object"}
            )
            response_content = completion.choices[0].message.content
            try:
                return int(json.loads(response_content["year"]))
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Parse error: {e}. Raw: {response_content}")
                return 1000
        except Exception as e:
            print(f"Error during request: {e}")
            return 1000
    else:
        print("Error during image encoding.")
        return 1000


def main():
    load_dotenv()
    client = OpenAI(base_url="https://inference.rcp.epfl.ch/v1", api_key=os.getenv('RCP_API_KEY_QWEN3'))
    image_url = "https://live.staticflickr.com/231/513806605_2c403048b1_n.jpg"
    

if __name__ == "__main__":
    main()
