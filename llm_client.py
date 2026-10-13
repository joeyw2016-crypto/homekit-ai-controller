"""
LLM 客户端：统一封装 DeepSeek API 调用
用法：call_llm(system_prompt, user_text) -> 回复文本
"""
import os
import requests

API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.getenv("_API_KEY", "xxxxx")


def call_llm(system_prompt, user_text, temperature=0.3):
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": temperature,
            "max_tokens": 500,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
