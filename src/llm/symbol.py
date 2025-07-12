from openai import OpenAI
import dotenv
import os
from ..utils.logger import logger

dotenv.load_dotenv()


class SymbolProcessor:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"), base_url=os.getenv("GROQ_BASE_URL")
        )
        self.model = os.getenv("GROQ_ADD_SYMBOL_MODEL", "llama3-8b-8192")

    def add_symbol(self, text):
        """为输入的文本添加合适的标点符号"""

        system_prompt = """
        Please add appropriate punctuation to the user’s input and return it. Apart from this, do not add or modify anything else. Do not translate the user's input. Do not add any explanation. Do not answer the user's question and so on. Just output the user's input with punctuation!
        """
        try:
            logger.info(f"正在添加标点符号...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return text, e

    def optimize_result(self, text):
        """优化识别结果"""
        # system_prompt = """
        # You are a content input optimizer.

        # Since the user’s input is the result of speech recognition, there may be some obvious inaccuracies or errors.
        # Please optimize the user’s input based on your knowledge.
        # If the user’s speech recognition result is fine, no changes are necessary—just output it directly.
        # Additionally, the user’s speech recognition input might lack necessary punctuation.
        # Please add the appropriate punctuation and return the final result.

        # Notice:
        #     •	We only need to optimize the user’s input content; there is no need to answer the user’s question!!!
        #     •	Do not add any explanation.
        #     •	Do not add any other content.
        #     •	Do not translate the user’s input.
        # """

        system_prompt = """
        You are a speech recognition content input optimizer.
        Please optimize the user’s input based on your knowledge.
        And add appropriate punctuation to the user’s input.
        Do not change the user's language.
        Do not add any explanation.
        Do not add answer to the user's question,just output the optimized content.
        """
        try:
            logger.info(f"正在优化识别结果...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return text, e
