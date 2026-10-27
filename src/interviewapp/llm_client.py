
from openai import OpenAI
from interviewapp.config import Settings
from dataclasses import dataclass
from prompt import system_prompt



@dataclass
class LLMGenerationoption:
    model: str
    temperature: float
    reasoning_effort: str
    #response_format: str
    max_tokens: int


class LLMClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        #self._system_prompt = system_prompt
        self._client = OpenAI(base_url=settings.base_url, api_key=settings.api_key)
        self._system_prompt=system_prompt
        
    def Ask_LLM(self, llmoptions:LLMGenerationoption,prompt="Can you write a python script to scrape a website?"):
       
      
        my_messages = [     
          self._system_prompt[0],
        
        {
            "role": "user",
            "content": prompt,
        },
                ]
       
        try:
            
            if llmoptions.reasoning_effort is None:
                llmoptions.reasoning_effort="medium"
            response = self._client.chat.completions.create(
               
                model=llmoptions.model,
                messages=my_messages,
                temperature= llmoptions.temperature,
                max_tokens=llmoptions.max_tokens,
                #response_format={"type":"json_object"},
                reasoning_effort=llmoptions.reasoning_effort
                
            )
            print(response)
            content = response.choices[0].message.content
            print("Response:", content)
            print("Tokens used:", response.usage.total_tokens)
            return content

        except Exception as e:
            print("Request failed:", e)
            return None

 

