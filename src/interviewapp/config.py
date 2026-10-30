import os
from interviewapp.models import aimodel
from interviewapp.prompt import system_prompts

# Models in the catalog that can't be used for chat (embeddings, speech-to-text, audio)
NON_CHAT_MODEL_MARKERS = ("embedding", "whisper", "audio")


class Settings:
    """API connection details and the option lists shown on the Settings page.
    The first item of each list is the default choice."""

    api_key: str = os.getenv("OPENROUTER_API_KEY")
    base_url: str = "https://openrouter.ai/api/v1"

    models: tuple[str, ...] = tuple(
        model for model in aimodel["anthropic"] + aimodel["openai"]
        if not any(marker in model for marker in NON_CHAT_MODEL_MARKERS)
    )
    temperatures: tuple[float, ...] = (0.2, 0.3, 0.4, 0.6, 0.7, 0.8)
    # 1000 first so it is the default: 100 is too small for most replies
    max_tokens: tuple[int, ...] = (1000, 1500, 500, 2000)
    # Only the efforts most models accept; "xhigh"/"max" are rejected by many
    reasoning_efforts: tuple[str, ...] = ("low", "medium", "high")
    response_format: tuple[str, ...] = ("text", "json")
    agent_type: tuple[str, ...] = tuple(system_prompts)
