import streamlit as st
from interviewapp.config import Settings
from interviewapp.llm_client import LLMClient,LLMGenerationOption
from interviewapp.safeguard import SafeGuard

class InterviewApp:
    """Streamlit UI with two pages: Chat and Settings.

    Usage:
        app = create_app()   # cached: built once, shared by every rerun
        app.init_state()     # call once per run, before any page is drawn
        st.navigation([st.Page(app.render_chat_page), st.Page(app.render_settings_page)]).run()
    """

    def __init__(self, settings: Settings,llmclient:LLMClient,safe_guard:SafeGuard):
        """settings: the option lists shown on the Settings page.
        llmclient: used to send the conversation to the model.
        safe_guard: checks each user message for prompt injection before it is sent."""
        self._settings=settings
        self._llmclient=llmclient
        self._safe_guard=safe_guard

    def init_state(self):
        """Create default settings and an empty chat history in st.session_state.

        Safe to call on every rerun: existing values are left untouched.
        """
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
        """Draw the Settings page (registered with st.Page).

        Each choice is saved straight into st.session_state.llm_settings.
        Picking a different agent clears the chat history.
        """
        st.title("Settings")
        current = st.session_state.llm_settings
        app_settings = self._settings

        current["model"] = st.selectbox(
            "Select Model",
            app_settings.models,
            index=app_settings.models.index(current["model"]),
        )
        selected_agent = st.selectbox(
            "Select Agent Type",
            app_settings.agent_type,
            index=app_settings.agent_type.index(current["agent"]),
        )
        # A different agent starts a fresh conversation
        if selected_agent != current["agent"]:
            current["agent"] = selected_agent
            self.clear_chat()
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
        """Return the saved settings as an LLMGenerationOption, ready to pass to ask_llm."""
        current = st.session_state.llm_settings
        return LLMGenerationOption(
            current["model"],
            current["agent"],
            float(current["temperature"]),
            current["reasoning_effort"],
            int(current["max_tokens"]),
            current["response_format"]
        )
        

    def render_chat_page(self):
        """Draw the Chat page (registered with st.Page, default page).

        Shows the agent name, the current settings, a New chat button, and the chat.
        """
        llmoptions = self.get_llm_options()
        st.title(llmoptions.agent)
        st.caption(
            f"Model: {llmoptions.model} · Temperature: {llmoptions.temperature} · "
            f"Reasoning: {llmoptions.reasoning_effort} · Max tokens: {llmoptions.max_tokens} · "
            f"Format: {llmoptions.response_format}"
        )
        st.button(
            "New chat",
            icon=":material/add_comment:",
            on_click=self.clear_chat,
        )
        self.handle_input(llmoptions)

    def clear_chat(self):
        """Delete the chat history. Used by the New chat button and when the agent changes."""
        st.session_state.messages = []

    def render_content(self, content):
        """Show one message: plain text as-is, JSON-mode replies formatted as markdown."""
        if isinstance(content, str):
            st.markdown(content)
        else:
            st.markdown(content.to_markdown())

    def render_message_history(self):
        """Redraw every saved message. Needed because Streamlit reruns the whole script on each interaction."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                self.render_content(message["content"])

    def handle_input(self,llmoptions:LLMGenerationOption):
        """Show the history and the chat box; when the user sends a message, get and show the reply.

        llmoptions: the settings to use for this request (from get_llm_options).
        Both the user message and a successful reply are added to st.session_state.messages.
        """
        self.render_message_history()
        # Accept user input
        prompt = st.chat_input(placeholder="Type your message...")
        if not prompt:
            return
        # Display user message in chat message container
        with st.chat_message("user"):
            try:
                is_injection = self._safe_guard.is_injection(prompt)
            except Exception as e:
                # If the check can't run, don't send the message unchecked
                st.error(f"Couldn't check your message, so it wasn't sent: {e}")
                return
            if is_injection:
                st.error("Prompt injection detected! Please rephrase your message.")
                return
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                response=self._llmclient.ask_llm(llmoptions,st.session_state.messages)
            except Exception as e:
                # Don't save failed replies, or every later request would resend them
                st.error(f"Request failed: {e}")
                return
            self.render_content(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


@st.cache_resource
def create_app():
    """Build the app once and reuse it on every rerun, instead of a new OpenAI client per click.

    Per-user data lives in st.session_state, so sharing this object is safe.
    """
    settings=Settings()
    return InterviewApp(settings,LLMClient(settings),SafeGuard(settings.api_key))


if __name__ == "__main__":
    # Without a key the OpenAI client can't be created, so stop with a clear message
    if not Settings.api_key:
        st.error(
            "OPENROUTER_API_KEY is not set. Set the environment variable to your "
            "OpenRouter API key, then restart the app."
        )
        st.stop()

    myapp=create_app()
    myapp.init_state()

    page = st.navigation([
        st.Page(myapp.render_chat_page, title="Chat", icon=":material/chat:", url_path="chat", default=True),
        st.Page(myapp.render_settings_page, title="Settings", icon=":material/settings:", url_path="settings"),
    ])
    page.run()


