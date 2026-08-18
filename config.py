import os
from typing import Dict, Literal
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Provider
    PROVIDER: Literal["groq", "nvidia", "anthropic", "mock"] = "groq"

    # Groq Cloud settings (Ultra-Fast LPUs)
    GROQ_API_KEY: str = Field(default="")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_TEXT_MODEL: str = "llama-3.1-8b-instant"
    GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"

    # NVIDIA NIM settings
    NVIDIA_API_KEY: str = Field(default="")
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_TEXT_MODEL: str = "meta/llama-3.1-70b-instruct"
    NVIDIA_VISION_MODEL: str = "meta/llama-3.2-11b-vision-instruct"
    NVIDIA_EMBED_MODEL: str = "nvidia/nv-embedqa-e5-v5"

    # Anthropic settings
    ANTHROPIC_API_KEY: str = Field(default="")
    ANTHROPIC_MODEL: str = "claude-opus-5"
    ANTHROPIC_BASE_URL: str = Field(default="")

    # Tavily Web Search
    TAVILY_API_KEY: str = Field(default="")

    # Qdrant Vector Store
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = Field(default="")

    # Application settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    SEMANTIC_CACHE_THRESHOLD: float = 0.96
    MAX_RETRIES: int = 2
    GROUNDING_THRESHOLD: float = 0.70

    # Deterministic Confidence Base Weights (Sum to 1.0)
    BASE_WEIGHTS: Dict[str, float] = {
        "coverage": 0.30,
        "grounding": 0.25,
        "retrieval_agreement": 0.15,
        "vision_match": 0.15,
        "taxonomy": 0.15,
    }
    CONFLICT_PENALTY: float = 0.08

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
