import requests
from PIL import Image
import io
from config import SPECIALIZED_MODELS, MODEL_CAPABILITIES
from api_utils import call_image_api

def generate_image(prompt, api_key, selected_model_name):
    """
    Generate an image based on the provided prompt
    
    Args:
        prompt (str): The description of the image to generate
        api_key (str): API key for authentication (legacy parameter, now uses secrets)
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
        # Call the image API using our utility function
        response_data = call_image_api(prompt=prompt, model_id=model_id)
        
        # Check for errors in the response
        if "error" in response_data:
            return {"error": response_data["error"]}
        
        # Check if image data is in the response
        if "data" in response_data and len(response_data["data"]) > 0 and "url" in response_data["data"][0]:
            # Get the image URL
            image_url = response_data["data"][0]["url"]
            
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
