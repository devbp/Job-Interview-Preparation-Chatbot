from openai import OpenAI
from interviewapp.config import Settings
from dataclasses import dataclass
from interviewapp.prompt import system_prompts
from interviewapp.responseformat import InterviewResponseFormat


@dataclass
class LLMGenerationOption:
    """Settings for one request to the model.

    agent: a key of system_prompts; picks the system prompt.
    response_format: "text" for a plain reply, "json" for an InterviewResponseFormat object.
    """
    model: str
    agent: str
    temperature: float
    reasoning_effort: str
    max_tokens: int
    response_format: str


class LLMClient:
    """Sends chat conversations to OpenRouter through the OpenAI SDK.

    Usage:
        client = LLMClient(Settings())
        reply = client.ask_llm(options, [{"role": "user", "content": "Hi"}])
    """

    def __init__(self, settings: Settings):
        """settings: provides the OpenRouter base_url and api_key."""
        self._settings = settings
        self._client = OpenAI(base_url=settings.base_url, api_key=settings.api_key)
        self._system_prompts = system_prompts

    def ask_llm(self, llmoptions: LLMGenerationOption, history: list[dict]):
        """Send the agent's system prompt plus the conversation, and return the model's reply.

        llmoptions: model, agent and generation settings for this request.
        history: list of {"role": "user" | "assistant", "content": ...} dicts,
            oldest first, ending with the new user message.

        Returns the reply text ("text" format) or an InterviewResponseFormat
        object ("json" format). Raises an exception if the request fails or the
        reply is empty, so the caller can show the reason to the user.
        """
        messages = [
            {
                "role": "system",
                "content": self._system_prompts[llmoptions.agent],
            },
        ]
        for message in history:
            content = message["content"]
            # JSON-mode replies are stored as pydantic objects; the API needs text
            if not isinstance(content, str):
                content = content.model_dump_json()
            messages.append({"role": message["role"], "content": content})

        request = dict(
            model=llmoptions.model,
            messages=messages,
            temperature=llmoptions.temperature,
            max_tokens=llmoptions.max_tokens,
            reasoning_effort=llmoptions.reasoning_effort,
        )

        if llmoptions.response_format == "json":
            response = self._client.chat.completions.parse(
                **request, response_format=InterviewResponseFormat
            )
            reply = response.choices[0].message.parsed
        else:
            response = self._client.chat.completions.create(**request)
            reply = response.choices[0].message.content

        if not reply:
            # Usually means max_tokens was used up (often by reasoning) before any visible text
            raise ValueError(
                f"The model returned an empty reply (finish reason: {response.choices[0].finish_reason}). "
                "Try a higher Max Tokens value."
            )
        return reply
