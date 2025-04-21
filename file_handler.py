import pandas as pd
import io
import base64
import streamlit as st

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
        "content": None
    }
    
    try:
        # Check file type and extract content accordingly
        if uploaded_file.type == "text/plain":
            # Handle text files
            content = uploaded_file.getvalue().decode("utf-8")
            file_details["content"] = content
            
        elif uploaded_file.type == "application/pdf":
            # For PDF files, we'd typically use PyPDF2 or similar
            # Since we don't have that in requirements, we'll return a placeholder
            file_details["content"] = "PDF content extraction. In production, use PyPDF2 or similar library."
            
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
