from config import SPECIALIZED_MODELS, MODEL_CAPABILITIES
from api_utils import call_euron_api

def handle_chat_message(user_input, message_history, selected_model_name, model_id, api_key, temperature, max_tokens, file_content=None):
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
        
    Returns:
        str: The AI's response
    """
    # Check if we need to switch models based on content
    if file_content and "code" in file_content.lower():
        if not MODEL_CAPABILITIES.get(selected_model_name, {}).get("Code Generation", False):
            model_id = SPECIALIZED_MODELS["code_analysis"]
    
    # Create the messages array for the API
    messages = []
    
    # First add system message if there's a file to analyze
    if file_content:
        messages.append({
            "role": "system",
            "content": f"The user has uploaded a file with the following content. Please help analyze or respond to queries about it:\n\n{file_content}"
        })
    
    # Add message history (limited to last 10 messages to avoid token limits)
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
