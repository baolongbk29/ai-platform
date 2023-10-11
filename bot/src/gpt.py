import os
import requests
import json

from core import config

class GPT2_Medium_VN:
    def __init__(self):
        self.url = config.HUGGINFACE_MODEL_URL
        self.headers = {
            "Authorization": f"Bearer {config.HUGGINFACE_INFERENCE_TOKEN}"}
        self.payload = {
            "inputs": "",
        }
        # # self.url = "https://api-inference.huggingface.co/models/chronopt-research/vietnamese-gpt2-medium"
        # self.headers = {"Authorization": "Bearer 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"}
    def query(self, input: str) -> list:
        self.payload["inputs"] = input
        # data = json.dumps(self.payload)
        response = requests.post(self.url, headers=self.headers, json=self.payload)
        data = json.loads(response.content.decode("utf-8"))
        text = data[0]['generated_text']
        # res = str(text.split("Human:")[0]).strip("\n").strip()
        # print(res)
        return text


if __name__ == "__main__":
    GPT2_Medium_VN().query("Hoàng Sa, Trường Sa là của")