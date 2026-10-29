
from openai import OpenAI
from interviewapp.config import Settings
from dataclasses import dataclass
from prompt import system_prompts
from responseformat import Interview_Response_Format


@dataclass
class LLMGenerationoption:
    model: str
    agent: str
    temperature: float
    reasoning_effort: str    
    max_tokens: int
    response_format: str


class LLMClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        #self._system_prompt = system_prompt
        self._client = OpenAI(base_url=settings.base_url, api_key=settings.api_key)
        self._system_prompts=system_prompts
        
    def Ask_LLM(self, llmoptions:LLMGenerationoption,prompt="Can you write a python script to scrape a website?"):
       
      
        my_messages = [     
         {
            "role": "system",
            "content": self._system_prompts[llmoptions.agent],
        }, 
          
        {
            "role": "user",
            "content": prompt,
        },
                ]
       
        try:
            if llmoptions.response_format == "json":
                currnet_response_format = Interview_Response_Format
                response = self._client.chat.completions.parse(
               
                model=llmoptions.model,
                messages=my_messages,
                temperature= llmoptions.temperature,
                max_tokens=llmoptions.max_tokens,
                response_format=currnet_response_format,
                reasoning_effort=llmoptions.reasoning_effort
                
            )
                return response.choices[0].message.parsed

            else:
                currnet_response_format = None    
            
                response = self._client.chat.completions.create(
                
                    model=llmoptions.model,
                    messages=my_messages,
                    temperature= llmoptions.temperature,
                    max_tokens=llmoptions.max_tokens,
                    response_format=currnet_response_format,
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

 

