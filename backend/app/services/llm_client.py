import os
from functools import lru_cache

from openai import OpenAI


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the running process")

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    return OpenAI(**kwargs)


def get_llm_model() -> str:
    model = os.getenv("LLM_MODEL")
    if not model:
        raise ValueError("LLM_MODEL is not set in the running process")
    return model