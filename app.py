import streamlit as st
import os
from dotenv import load_dotenv
from config import AVAILABLE_MODELS, MODEL_CAPABILITIES
from chat_handler import handle_chat_message
from file_handler import process_uploaded_file
from image_handler import generate_image
from utils import initialize_session_state

# Load environment variables
load_dotenv()

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Multi-Model AI Assistant", layout="wide")
    
    st.title("🤖 Multi-Model AI Assistant")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for model selection and settings
    with st.sidebar:
        st.header("Model Settings")
        
        # Model selection dropdown
        selected_model = st.selectbox(
            "Select AI Model",
            options=list(AVAILABLE_MODELS.keys()),
            index=0,
            key="model_selection"
        )
        
        st.caption(f"Model ID: {AVAILABLE_MODELS[selected_model]}")
        
        # Display model capabilities
        st.subheader("Model Capabilities")
        capabilities = MODEL_CAPABILITIES.get(selected_model, {})
        for capability, supported in capabilities.items():
            st.checkbox(capability, value=supported, disabled=True)
        
        # API key input (hidden)
        api_key = st.text_input("API Key", type="password", value=os.getenv("API_KEY", ""))
        if api_key:
            st.session_state.api_key = api_key
        
        # Temperature slider
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        st.session_state.temperature = temperature
        
        # Max tokens slider
        max_tokens = st.slider("Max Tokens", min_value=100, max_value=4000, value=1000, step=100)
        st.session_state.max_tokens = max_tokens
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
            st.experimental_rerun()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # File upload section
        st.subheader("File Upload")
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "xlsx"])
        if uploaded_file:
            file_details = process_uploaded_file(uploaded_file)
            st.session_state.uploaded_file_content = file_details["content"]
            st.session_state.uploaded_file_name = file_details["name"]
            st.success(f"File uploaded: {file_details['name']}")
        
        # Image generation section
        st.subheader("Image Generation")
        image_prompt = st.text_input("Image Description")
        if st.button("Generate Image") and image_prompt:
            with st.spinner("Generating image..."):
                image_result = generate_image(
                    image_prompt, 
                    st.session_state.api_key, 
                    selected_model
                )
                if "image" in image_result:
                    st.image(image_result["image"], caption=image_prompt)
                else:
                    st.error(image_result["error"])
    
    with col1:
        # Chat interface
        st.subheader("Chat")
        
        # Display uploaded file info if any
        if st.session_state.uploaded_file_name:
            st.info(f"Uploaded file: {st.session_state.uploaded_file_name}")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input for new message
        user_input = st.chat_input("Ask something...")
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    message_placeholder = st.empty()
                    response = handle_chat_message(
                        user_input,
                        st.session_state.messages,
                        selected_model,
                        AVAILABLE_MODELS[selected_model],
                        st.session_state.api_key,
                        st.session_state.temperature,
                        st.session_state.max_tokens,
                        st.session_state.uploaded_file_content
                    )
                    message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
