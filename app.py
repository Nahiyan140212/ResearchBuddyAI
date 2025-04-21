import streamlit as st
import os
from config import AVAILABLE_MODELS, MODEL_CAPABILITIES, DEFAULT_MODEL
from chat_handler import handle_chat_message
from file_handler import process_uploaded_file
from image_handler import generate_image
from utils import initialize_session_state
from api_utils import get_euron_api_key
import io
from PIL import Image

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
        
        # Check if API key is available
        api_key = get_euron_api_key()
        if not api_key:
            st.warning("API key not found in secrets. Please add it to your .streamlit/secrets.toml file.")
            st.code("""
            # Example secrets.toml file
            [euron]
            api_key = "your-api-key-here"
            """)
        else:
            st.success("API key found in secrets.")
        
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
            st.session_state.uploaded_image = None
            st.experimental_rerun()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # File upload section
        st.subheader("File Upload")
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "csv", "xlsx", "jpg", "jpeg", "png"])
        if uploaded_file:
            file_details = process_uploaded_file(uploaded_file)
            st.session_state.uploaded_file_content = file_details["content"]
            st.session_state.uploaded_file_name = file_details["name"]
            
            # If it's an image, store it separately and display it
            if file_details["is_image"]:
                st.session_state.uploaded_image = file_details["image"]
                st.image(file_details["image"], caption=file_details["name"], use_column_width=True)
                st.info("Image uploaded! You can now ask questions about this image.")
            else:
                st.success(f"File uploaded: {file_details['name']}")
        
        # Image generation section
        st.subheader("Image Generation")
        image_prompt = st.text_input("Image Description")
        if st.button("Generate Image") and image_prompt:
            with st.spinner("Generating image..."):
                image_result = generate_image(
                    image_prompt, 
                    api_key,  # This parameter is now ignored but kept for compatibility
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
                    
                    # Check if an image is uploaded and the selected model supports image analysis
                    has_image = st.session_state.uploaded_image is not None
                    model_supports_images = MODEL_CAPABILITIES.get(selected_model, {}).get("Image Analysis", False)
                    
                    # If image is uploaded and model doesn't support images, add a warning
                    if has_image and not model_supports_images:
                        st.warning(f"Note: {selected_model} doesn't fully support image analysis. For best results with images, try using Google Gemini 2.5 Pro Exp.")
                    
                    response = handle_chat_message(
                        user_input,
                        st.session_state.messages,
                        selected_model,
                        AVAILABLE_MODELS[selected_model],
                        api_key,  # This parameter is now ignored but kept for compatibility
                        st.session_state.temperature,
                        st.session_state.max_tokens,
                        st.session_state.uploaded_file_content,
                        st.session_state.uploaded_image if has_image else None
                    )
                    message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
