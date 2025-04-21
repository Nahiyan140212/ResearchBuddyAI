import streamlit as st
import requests
from config import API_ENDPOINTS

def get_euron_api_key():
    """
    Get the Euron API key from Streamlit secrets
    
    Returns:
        str: API key
    """
    try:
        return st.secrets["euron"]["api_key"]
    except KeyError:
        # Fall back to session state if not in secrets
        if "api_key" in st.session_state and st.session_state.api_key:
            return st.session_state.api_key
        return None

def call_euron_api(messages, model_id, temperature=0.5, max_tokens=2000):
    """
    Call the Euron API for chat completions
    
    Args:
        messages (list): List of message objects
        model_id (str): ID of the model to use
        temperature (float): Temperature parameter
        max_tokens (int): Maximum tokens for response
        
    Returns:
        dict: API response
    """
    api_key = get_euron_api_key()
    
    if not api_key:
        return {"error": "API key not found. Please add it to Streamlit secrets or enter it in the sidebar."}
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "messages": messages,
        "model": model_id,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(API_ENDPOINTS["chat"], headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def call_image_api(prompt, model_id):
    """
    Call the Euron API for image generation
    
    Args:
        prompt (str): Image description
        model_id (str): ID of the model to use
        
    Returns:
        dict: API response
    """
    api_key = get_euron_api_key()
    
    if not api_key:
        return {"error": "API key not found. Please add it to Streamlit secrets or enter it in the sidebar."}
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model_id,
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }
    
    try:
        response = requests.post(API_ENDPOINTS["image"], headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
