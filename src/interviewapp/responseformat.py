from pydantic import BaseModel


class InterviewResponseFormat(BaseModel):
    """Structure the model must fill when the response format is "json" (used by LLMClient.ask_llm)."""
    question: str
    job: str
    technical_skills: list[str]
    behavioral_skills: list[str]
    answer: str
    language: str

    def to_markdown(self) -> str:
        """Return the reply as readable markdown for the chat window."""
        return "\n\n".join([
            f"**Question:** {self.question}",
            f"**Job:** {self.job}",
            f"**Technical skills:** {', '.join(self.technical_skills)}",
            f"**Behavioral skills:** {', '.join(self.behavioral_skills)}",
            f"**Answer:** {self.answer}",
            f"*Language: {self.language}*",
        ])
