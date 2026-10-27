import streamlit as st
import random
import time
import requests
#from openai import OpenAI
from interviewapp.config import Settings
from interviewapp.llm_client import LLMClient,LLMGenerationoption
from dataclasses import dataclass



class InterviewApp:
    def __init__(self, settings: Settings,llmclient:LLMClient):
        self._settings=settings
        self._llmclient=llmclient
       
        

    def render_settings(self):
        st.title("Job Interview Preparation Agent")
        tune_temperature = st.select_slider(
            "Select Tuning Temperature",
            options=settings.temperatures
        )
        st.write("Tune Temperature", tune_temperature)
        # Initialize chat history

        model_select = st.selectbox(
            "Select Model",
            settings.models,
        )

        st.write("You selected:", model_select)


        reasoning_effect_option = st.selectbox(
            "Select Reasoning Effect",
            settings.reasoning_efforts
        )



        st.write("You selected:", reasoning_effect_option)


        max_tokens = st.selectbox(
            "Modify Temperature",
            settings.max_tokens
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []


        

        return LLMGenerationoption(model_select,float(tune_temperature),reasoning_effect_option,int(max_tokens))
    
    def render_message_history(self):
         # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def handle_input(self,llmoptions:LLMGenerationoption)  :  
        self.render_message_history()

        # Accept user input
        prompt = st.chat_input(placeholder="What is up?")
        if not prompt:
            return
        # Display user message in chat message container
        with st.chat_message("user"):                
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})



        # Display assistant response in chat message container
        with st.chat_message("assistant"):            
            response=self._llmclient.Ask_LLM(llmoptions,prompt)
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        


if __name__ == "__main__":
    settings=Settings()

    llmclient=LLMClient(settings)
    myapp=InterviewApp(settings,llmclient)
    options=myapp.render_settings()
    myapp.handle_input(options)


