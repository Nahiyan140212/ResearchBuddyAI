import requests
import base64
import io
from config import SPECIALIZED_MODELS, MODEL_CAPABILITIES
from api_utils import call_euron_api

def handle_chat_message(user_input, message_history, selected_model_name, model_id, api_key, temperature, max_tokens, file_content=None, image=None):
    """
    Handles sending chat messages to the API and processing responses
    
    Args:
        user_input (str): The user's input message
        message_history (list): List of previous message objects
        selected_model_name (str): Display name of the selected model
        model_id (str): ID of the model to use
        api_key (str): API key for authentication (legacy parameter, now uses secrets)
        temperature (float): Temperature parameter for response generation
        max_tokens (int): Maximum tokens for response
        file_content (str, optional): Content of uploaded file if any
        image (PIL.Image, optional): Uploaded image if any
        
    Returns:
        str: The AI's response
    """
    # Check if we need to switch models based on content or image presence
    if file_content and "code" in file_content.lower():
        if not MODEL_CAPABILITIES.get(selected_model_name, {}).get("Code Generation", False):
            model_id = SPECIALIZED_MODELS["code_analysis"]
    
    if image and not MODEL_CAPABILITIES.get(selected_model_name, {}).get("Image Analysis", False):
        model_id = SPECIALIZED_MODELS["image_analysis"]
    
    # Create the messages array for the API
    messages = []
    
    # Add system message if there's a file to analyze
    if file_content:
        messages.append({
            "role": "system",
            "content": f"The user has uploaded a file with the following content. Please help analyze or respond to queries about it:\n\n{file_content}"
        })
    
    # Handle image if present
    if image:
        # Need to convert PIL Image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Add image message in a format suitable for models that accept images
        # This format is based on ChatGPT's vision format, adapt as needed for other APIs
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "Here is an image the user uploaded:"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_str}"
                    }
                }
            ]
        })
    
    # Add message history (limited to last 10 messages to avoid token limits)
    # Skip the system message if it exists
    start_idx = 1 if messages and messages[0]["role"] == "system" else 0
    for msg in message_history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current user input if not already in message history
    if message_history and message_history[-1]["role"] != "user":
        messages.append({
            "role": "user",
            "content": user_input
        })
    
    try:
        # Call the Euron API using our utility function
        response_data = call_euron_api(
            messages=messages,
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Check for errors in the response
        if "error" in response_data:
            return f"Error: {response_data['error']}"
        
        # Extract the assistant's message from the response
        if "choices" in response_data and len(response_data["choices"]) > 0:
            assistant_message = response_data["choices"][0]["message"]["content"]
            return assistant_message
        else:
            return "Sorry, I couldn't generate a response. Please try again."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"
