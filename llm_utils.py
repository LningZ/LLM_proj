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

# === 自动重试封装 ===
@retry(wait=wait_exponential(multiplier=1, min=1, max=10),
       stop=stop_after_attempt(3),
       reraise=True)
def chat_completion(prompt: str, model="gpt-4.1-nano", temperature=0.3,*,verbose: bool = True) -> str:
    """
    给定 prompt，请求 LLM 输出标准 JSON 字符串（不含解释或 markdown）
    """
    system_prompt = (
        "You are a precise manufacturing assistant.\n"
        "Return only a valid JSON array of process steps.\n"
        "Each item must include: step, tool, operation, rpm, feed.\n"
        "Example:\n"
        '[{"step": "Roughing", "tool": "End Mill", "operation": "Milling", "rpm": 5000, "feed": 1200}]\n\n'
        "Do not explain. Do not format with markdown. No commentary."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        global TOKENS_USED
        if response.usage is not None:
            TOKENS_USED += response.usage.total_tokens  
        
        content = response.choices[0].message.content.strip()
        if verbose:
            print("LLM Response:\n", content)
        return content

    
    except Exception as e:
        print("LLM 调用失败: ", str(e))
        return ""