
import os
from models import aimodel
from dataclasses import dataclass

#@dataclass
class Settings:
   
    api_key: str = os.getenv("OPENROUTER_API_KEY")
    base_url: str = "https://openrouter.ai/api/v1"
   
    models: tuple[str, ...] = (
        aimodel["anthropic"]+ aimodel["openai"]
        
    )
    temperatures: tuple[float, ...] = (0.2, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8)
    max_tokens: tuple[int, ...]=(100,500,1000,1500)
    reasoning_efforts: tuple[str, ...] = ("minimal", "medium", "high")


