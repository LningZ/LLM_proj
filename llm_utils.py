# llm_utils.py

import os
import json
from typing import List, Dict, Any

import openai
from openai import OpenAIError
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt

from pydantic import BaseModel, PositiveInt, NonNegativeInt, ValidationError
import tiktoken

# === Load environment variables (e.g., OPENAI_API_KEY) from .env ===
load_dotenv()

# === Initialize OpenAI client ===
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Global token usage counter ===
TOKENS_USED: int = 0

# === Pydantic schema for outline-level step ===
class OutlineStep(BaseModel):
    step: str
    description: str

# === Pydantic schema for detailed machining step ===
class DetailStep(BaseModel):
    step: str
    tool: str
    operation: str
    rpm: NonNegativeInt
    feed: NonNegativeInt

# === LLM call wrapper ===
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o",
    temperature: float = 0.3,
    *,
    verbose: bool = True
) -> str:
    """
    Call OpenAI chat model with a list of role-content messages.
    
    Args:
        messages (List[Dict]): List of messages with role/content.
        model (str): OpenAI model name (default: gpt-4o).
        temperature (float): Sampling temperature (default: 0.3).
        verbose (bool): If True, print response content.

    Returns:
        str: LLM-generated content (plain text).
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    
    # === Token counting ===
    global TOKENS_USED
    if response.usage:
        TOKENS_USED += response.usage.total_tokens
    else:
        # Fallback: estimate token usage locally if server doesn't return usage
        enc = tiktoken.encoding_for_model(model)
        prompt_tokens = sum(len(enc.encode(m["content"])) for m in messages)
        completion_tokens = len(enc.encode(response.choices[0].message.content))
        TOKENS_USED += prompt_tokens + completion_tokens

    content = response.choices[0].message.content.strip()
    if verbose:
        print("LLM Response:\n", content)
    return content

# === Parse and validate LLM-generated JSON output ===
def parse_llm_output(response_text: str, schema: BaseModel) -> List[dict]:
    """
    Parse LLM output (in JSON format) and validate each item using a Pydantic schema.

    Args:
        response_text (str): Raw JSON string returned by the LLM.
        schema (BaseModel): Pydantic class to validate each item.

    Returns:
        List[dict]: Validated list of dictionaries.

    Raises:
        ValueError: If JSON cannot be parsed or any field fails validation.
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
            raise ValueError(f"Field validation failed: {ve}")

    return validated_list
