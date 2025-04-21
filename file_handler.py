import pandas as pd
import io
import base64
import streamlit as st
import os
from PIL import Image

def process_uploaded_file(uploaded_file):
    """
    Process the uploaded file and extract its content
    
    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        
    Returns:
        dict: A dictionary containing file details and content
    """
    file_details = {
        "name": uploaded_file.name,
        "size": uploaded_file.size,
        "type": uploaded_file.type,
        "content": None,
        "is_image": False,
        "image": None
    }
    
    try:
        # Check file type and extract content accordingly
        if uploaded_file.type == "text/plain":
            # Handle text files
            content = uploaded_file.getvalue().decode("utf-8")
            file_details["content"] = content
            
        elif uploaded_file.type == "application/pdf":
            # Handle PDF files
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
                pdf_text = ""
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_text += page.extract_text() + "\n\n"
                
                file_details["content"] = pdf_text if pdf_text.strip() else "No extractable text found in PDF."
            except ImportError:
                file_details["content"] = "PDF content extraction. Please install PyPDF2 library."
            
        elif "csv" in uploaded_file.type:
            # Handle CSV files
            df = pd.read_csv(uploaded_file)
            buffer = io.StringIO()
            df.info(buf=buffer)
            stats = buffer.getvalue()
            
            # Create a summary of the CSV content
            summary = f"CSV File Summary:\n\n"
            summary += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
            summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
            summary += f"Data Types:\n{stats}\n\n"
            summary += f"Sample Data (first 5 rows):\n{df.head().to_string()}"
            
            file_details["content"] = summary
            
        elif "xlsx" in uploaded_file.type or "xls" in uploaded_file.type:
            # Handle Excel files
            df = pd.read_excel(uploaded_file)
            buffer = io.StringIO()
            df.info(buf=buffer)
            stats = buffer.getvalue()
            
            # Create a summary of the Excel content
            summary = f"Excel File Summary:\n\n"
            summary += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
            summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
            summary += f"Data Types:\n{stats}\n\n"
            summary += f"Sample Data (first 5 rows):\n{df.head().to_string()}"
            
            file_details["content"] = summary
            
        # Handle image files
        elif uploaded_file.type.startswith('image/'):
            # Process image file
            image = Image.open(uploaded_file)
            
            # Create a description of the image
            width, height = image.size
            format_type = image.format
            mode = image.mode
            
            image_info = f"Image File Information:\n\n"
            image_info += f"Filename: {uploaded_file.name}\n"
            image_info += f"Format: {format_type}\n"
            image_info += f"Mode: {mode}\n"
            image_info += f"Dimensions: {width} x {height} pixels\n"
            
            file_details["content"] = image_info
            file_details["is_image"] = True
            file_details["image"] = image
            
        else:
            # For unsupported file types
            file_details["content"] = f"Unsupported file type: {uploaded_file.type}"
    
    except Exception as e:
        file_details["content"] = f"Error processing file: {str(e)}"
    
    return file_details

def get_file_download_link(content, filename, mime_type):
    """
    Generates a download link for processed file content
    
    Args:
        content: The file content to be downloaded
        filename: The name for the downloaded file
        mime_type: The MIME type of the file
        
    Returns:
        str: HTML link for downloading the file
    """
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def encode_image(image_path):
    """
    Base64 encode an image file for sending to vision-capable models
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Base64 encoded image string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
