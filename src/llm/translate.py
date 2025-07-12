import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TranslateProcessor:
    def __init__(self):
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('SILICONFLOW_API_KEY')}",
            "Content-Type": "application/json",
        }
        self.model = os.getenv("SILICONFLOW_TRANSLATE_MODEL", "THUDM/glm-4-9b-chat")

    def translate(self, text):
        system_prompt = """
        You are a translation assistant.
        Please translate the user's input into English.
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        }
        try:
            response = requests.request(
                "POST", self.url, headers=self.headers, json=payload
            )
            return (
                response.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
        except Exception as e:
            return text, e
