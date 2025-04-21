import requests
from PIL import Image
import io
from config import API_ENDPOINTS, SPECIALIZED_MODELS, MODEL_CAPABILITIES

def generate_image(prompt, api_key, selected_model_name):
    """
    Generate an image based on the provided prompt
    
    Args:
        prompt (str): The description of the image to generate
        api_key (str): API key for authentication
        selected_model_name (str): Current selected model name
        
    Returns:
        dict: Contains either the generated image or an error message
    """
    # Check if the selected model supports image generation
    if not MODEL_CAPABILITIES.get(selected_model_name, {}).get("Image Generation", False):
        # Switch to a model that supports image generation
        model_id = SPECIALIZED_MODELS["image_generation"]
    else:
        # Get the model ID for the selected model
        from config import AVAILABLE_MODELS
        model_id = AVAILABLE_MODELS[selected_model_name]
    
    try:
        # Prepare the API request
        url = API_ENDPOINTS["image"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            "n": 1,  # Number of images to generate
            "size": "512x512"  # Image resolution
        }
        
        # Send the request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        # Check if image data is in the response
        if "data" in data and len(data["data"]) > 0 and "url" in data["data"][0]:
            # Get the image URL
            image_url = data["data"][0]["url"]
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Create an Image object
            image = Image.open(io.BytesIO(image_response.content))
            
            return {"image": image}
        else:
            return {"error": "No image data in response"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Error communicating with the API: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
