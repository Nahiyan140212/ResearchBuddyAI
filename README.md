# ResearchBuddy AI

A Streamlit-based chatbot application that allows users to interact with various AI models, upload files for analysis, and generate images.

## Features

- Chat with multiple AI models (OpenAI, Google Gemini, Meta Llama, DeepSeek, Qwen, Mistral)
- Upload and analyze files (TXT, PDF, CSV, XLSX)
- Generate images with compatible models
- Customizable parameters (temperature, max tokens)
- Automatic model switching based on task requirements

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuring Streamlit Secrets

The application uses Streamlit secrets to store the API key. Create a `.streamlit/secrets.toml` file with the following content:

```toml
[euron]
api_key = "your-api-key-here"
```

For local development, create this file in your project directory. For Streamlit Cloud deployment, add the secrets through the Streamlit Cloud dashboard.

## Running the Application

Run the application using:

```
streamlit run app.py
```

Or use the provided shell script:

```
bash run.sh
```

## Application Structure

- `app.py` - Main Streamlit application
- `config.py` - Configuration for models and capabilities
- `api_utils.py` - API connection utilities
- `chat_handler.py` - Functions for handling chat messages
- `file_handler.py` - Functions for processing uploaded files
- `image_handler.py` - Functions for image generation
- `utils.py` - Utility functions for the application
- `requirements.txt` - Required Python packages
- `run.sh` - Shell script to set up and run the application

## Usage

1. Select an AI model from the sidebar
2. Adjust temperature and max tokens if needed
3. Upload files for analysis if desired
4. Chat with the assistant using the input field
5. Request image generation using the image section

## Required API

This application uses the Euron.one API for model access. You'll need an API key from Euron to use this application.

## Deploying to Streamlit Cloud

1. Push your code to a GitHub repository
2. Connect your repository to Streamlit Cloud
3. Add your API key to the Streamlit Cloud secrets
4. Deploy the application

## License

This project is licensed under the MIT License - see the LICENSE file for details.
