# llm_utils.py
import os
import openai
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt
from typing import List, Dict, Any
from pydantic import BaseModel, PositiveInt, ValidationError,NonNegativeInt
import json
import tiktoken


# === 加载 .env 文件中的环境变量 ===
load_dotenv()

# === 初始化客户端 ===
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 全局 token 统计 ===
TOKENS_USED: int = 0

class OutlineStep(BaseModel):
    step: str
    description: str


class DetailStep(BaseModel):
    step: str
    tool: str
    operation: str
    rpm: NonNegativeInt
    feed: NonNegativeInt


@retry(wait=wait_exponential(multiplier=1, min=1, max=10),
       stop=stop_after_attempt(3),
       reraise=True)
def chat_completion(messages: list,
                    model: str = "gpt-4o",
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
        
    else:
        enc = tiktoken.encoding_for_model(model)# fallback：本地估算
        prompt_tokens = sum(len(enc.encode(m["content"])) for m in messages)
        completion_tokens = len(enc.encode(response.choices[0].message.content))
        TOKENS_USED += prompt_tokens + completion_tokens

    content = response.choices[0].message.content.strip()
    if verbose:
        print("LLM Response:\n", content)  
    return content

# === LLM JSON 解析 + Pydantic 校验 ===
def parse_llm_output(response_text: str, schema: BaseModel) -> List[dict]:
    """
    Load JSON text from LLM, validate each item with a Pydantic schema,
    and return a list of dictionaries.
    """
    
    try:
        raw_list = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parsing failed: {e}")

    validated_list = []
    for item in raw_list:
        try:
            obj = schema(**item)  
            validated_list.append(obj.dict())
        except ValidationError as ve:
            raise ValueError(f"Field validation failed : {ve}")

    return validated_list



def repair_invalid_row(row: Dict, material: str,
                       rpm_min: int, rpm_max: int,
                       feed_min: int, feed_max: int) -> Dict:
    """
    修正单个工序中的rpm和feed，返回修正后的 {"rpm":..., "feed":...}
    """
    prompt = (
        "You previously output the following machining step, but the spindle speed or feed rate violates material limits:\n"
        f"{json.dumps(row, ensure_ascii=False)}\n\n"
        f"For {material}, spindle speed must be between {rpm_min}-{rpm_max} rpm, "
        f"and feed rate between {feed_min}-{feed_max} mm/min.\n"
        "Please return ONLY the corrected JSON object with the same fields and valid rpm and feed."
    )

    system_msg = {"role": "system", "content": "You are a CNC process planner."}
    user_msg = {"role": "user", "content": prompt}

    raw = chat_completion(messages=[system_msg, user_msg], verbose=False)
    return json.loads(raw)
