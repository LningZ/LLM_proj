# llm_utils.py
import os
import openai
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import List, Dict, Any


# === 加载 .env 文件中的环境变量 ===
load_dotenv()

# === 初始化客户端 ===
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 全局 token 统计 ===
TOKENS_USED: int = 0

@retry(wait=wait_exponential(multiplier=1, min=1, max=10),
       stop=stop_after_attempt(3),
       reraise=True)
def chat_completion(messages: list,
                    model: str = "gpt-4.1-nano",
                    temperature: float = 0.3,
                    *,
                    verbose: bool = True) -> str:
    """
    Call OpenAI chat completion with a list of messages.
    `messages` must already include system / user roles.
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    # token counter
    global TOKENS_USED
    if response.usage:
        TOKENS_USED += response.usage.total_tokens

    content = response.choices[0].message.content.strip()
    if verbose:
        print("LLM Response:\n", content)
    return content
