import streamlit as st
import random
import time
import requests
from interviewapp.config import Settings
from interviewapp.llm_client import LLMClient,LLMGenerationoption
from dataclasses import dataclass



class InterviewApp:
    def __init__(self, settings: Settings,llmclient:LLMClient):
        self._settings=settings
        self._llmclient=llmclient

    def init_state(self):
        # Defaults kept in session_state so they survive switching pages
        if "llm_settings" not in st.session_state:
            st.session_state.llm_settings = {
                "model": self._settings.models[0],
                "agent": self._settings.agent_type[0],
                "reasoning_effort": self._settings.reasoning_efforts[0],
                "temperature": self._settings.temperatures[0],
                "max_tokens": self._settings.max_tokens[0],
                "response_format": self._settings.response_format[0],
            }
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def render_settings_page(self):
        st.title("Settings")
        current = st.session_state.llm_settings
        app_settings = self._settings

        current["model"] = st.selectbox(
            "Select Model",
            app_settings.models,
            index=app_settings.models.index(current["model"]),
        )
        current["agent"] = st.selectbox(
            "Select Agent Type",
            app_settings.agent_type,
            index=app_settings.agent_type.index(current["agent"]),
        )
        current["reasoning_effort"] = st.selectbox(
            "Select Reasoning Effort",
            app_settings.reasoning_efforts,
            index=app_settings.reasoning_efforts.index(current["reasoning_effort"]),
        )
        current["temperature"] = st.select_slider(
            "Select Tuning Temperature",
            options=app_settings.temperatures,
            value=current["temperature"],
        )
        current["max_tokens"] = st.selectbox(
            "Max Tokens",
            app_settings.max_tokens,
            index=app_settings.max_tokens.index(current["max_tokens"]),
        )
        current["response_format"] = st.selectbox(
            "Response Format",
            app_settings.response_format,
            index=app_settings.response_format.index(current["response_format"]),
        )
        st.success("Settings are applied to the chat automatically.")

    def get_llm_options(self):
        current = st.session_state.llm_settings
        return LLMGenerationoption(
            current["model"],
            current["agent"],
            float(current["temperature"]),
            current["reasoning_effort"],
            int(current["max_tokens"]),
            current["response_format"]
        )
        

    def render_chat_page(self):
        llmoptions = self.get_llm_options()
        st.title(llmoptions.agent)
        st.caption(
            f"Model: {llmoptions.model} · Temperature: {llmoptions.temperature} · "
            f"Reasoning: {llmoptions.reasoning_effort} · Max tokens: {llmoptions.max_tokens},Format: {llmoptions.response_format} "
        )
        self.handle_input(llmoptions)

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
    myapp.init_state()

    page = st.navigation([
        st.Page(myapp.render_chat_page, title="Chat", icon=":material/chat:", url_path="chat", default=True),
        st.Page(myapp.render_settings_page, title="Settings", icon=":material/settings:", url_path="settings"),
    ])
    page.run()


