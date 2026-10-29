from pydantic import BaseModel


class Interview_Response_Format(BaseModel):
    question: str
    job: str
    technical_skills: list[str]
    behavioral_skills: list[str]    
    answer: str
    language: str
    
