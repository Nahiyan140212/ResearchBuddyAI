import streamlit as st

def initialize_session_state():
    """
    Initialize Streamlit session state variables if they don't exist
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 1000
    
    if "uploaded_file_content" not in st.session_state:
        st.session_state.uploaded_file_content = None
    
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None

def format_message(message):
    """
    Format message content for display
    
    Args:
        message (dict): Message object with role and content
        
    Returns:
        str: Formatted message content
    """
    return message["content"]

def create_system_prompt(context=None):
    """
    Create a system prompt based on context if needed
    
    Args:
        context (dict, optional): Context information
        
    Returns:
        str: System prompt
    """
    base_prompt = "You are a helpful AI assistant."
    
    if context:
        if "file_content" in context and context["file_content"]:
            base_prompt += f"\n\nThe user has uploaded a file with the following content: {context['file_content']}"
    
    return base_prompt
