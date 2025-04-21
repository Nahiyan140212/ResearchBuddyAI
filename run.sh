#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment based on OS
if [ -f venv/Scripts/activate ]; then
    source venv/Scripts/activate  # Windows
else
    source venv/bin/activate  # Linux/Mac
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Create secrets.toml file if it doesn't exist
if [ ! -f .streamlit/secrets.toml ]; then
    echo "Creating secrets.toml file..."
    echo "[euron]" > .streamlit/secrets.toml
    echo "api_key = \"your_api_key_here\"" >> .streamlit/secrets.toml
    echo "Please update the .streamlit/secrets.toml file with your actual API key"
fi

# Run the Streamlit app
echo "Starting Streamlit app..."
streamlit run app.py
