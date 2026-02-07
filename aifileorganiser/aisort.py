import os
import shutil
import logging
import docx
import PyPDF2
from ollama import Client
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
ollama_client = Client(host='http://localhost:11434')

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def sanitize_folder_name(name):
    """Sanitize folder name to be filesystem-friendly."""
    if not name:
        return ""
    # Take only the first line to avoid newlines
    name = name.split('\n')[0].strip()
    # Remove invalid characters, keep only alphanumeric, underscores, and single spaces
    name = re.sub(r'[^\w\s]', '', name)
    # Replace multiple spaces with a single underscore
    name = re.sub(r'\s+', '_', name)
    # Limit to 1-3 words
    words = name.split('_')
    if len(words) > 3:
        name = '_'.join(words[:3])
    # Limit to 50 characters
    name = name[:50]
    # Ensure non-empty and valid
    if not name or name.isspace():
        return ""
    return name

def extract_text_from_file(filepath):
    """Extract text from supported file types, optimized for efficiency."""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        logging.debug(f"Unsupported file type: {filepath}")
        return ""
    
    try:
        if ext == '.pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ' '.join([page.extract_text() or '' for page in reader.pages[:3]])
                return text[:2000]
        elif ext == '.docx':
            doc = docx.Document(filepath)
            text = ' '.join([para.text for para in doc.paragraphs if para.text.strip()])
            return text[:2000]
        elif ext == '.txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                return text[:2000]
    except Exception as e:
        logging.warning(f"Error reading {filepath}: {e}")
        return ""
    return ""

def classify_file_content_with_ollama(content, filename):
    """Classify file content and filename using Gemma, returning a folder name or empty string."""
    prompt = f"""You are an expert file organizer. Based on the filename and content provided, suggest a concise, filesystem-friendly folder name (1-3 words, only letters, numbers, and underscores, no spaces or special characters, max 50 characters) that best represents the file's topic or purpose.

- Use the filename as a strong indicator of the topic (e.g., 'Quantum_Physics.pdf' suggests 'Quantum_Physics').
- Analyze the content to refine or confirm the folder name.
- Return ONLY the folder name, with words separated by underscores (e.g., 'Artificial_Intelligence').
- Do NOT include any explanation, newlines, or extra text.
- If the content is ambiguous, insufficient, or unreadable, return an empty string '' to keep the file in its current folder.
- Do NOT use generic terms like 'Other' or 'Uncategorised'.

Examples:
- Filename: 'AI_Intro.pdf', Content: Discusses machine learning -> Artificial_Intelligence
- Filename: 'Poetry.docx', Content: Poems by Shakespeare -> Poetry
- Filename: 'Report.txt', Content: Empty or unreadable -> ''

Filename: {filename}
Content (first 1000 characters): {content[:1000]}

Folder name:"""
    
    try:
        response = ollama_client.chat(model="gemma", messages=[
            {"role": "user", "content": prompt}
        ])
        folder_name = response['message']['content'].strip()
        logging.debug(f"Raw AI response for {filename}: '{folder_name}'")
        
        # Sanitize and validate folder name
        folder_name = sanitize_folder_name(folder_name)
        if folder_name:
            logging.debug(f"Sanitized folder name for {filename}: '{folder_name}'")
            return folder_name
        logging.debug(f"Invalid or empty folder name for {filename}, keeping in place")
        return ""
    except Exception as e:
        logging.error(f"AI classification failed for {filename}: {e}")
        return ""

def move_file_to_category(filepath, folder_name, base_dir):
    """Move file to the specified folder, handling conflicts."""
    if not folder_name:
        logging.info(f"Keeping {filepath} in original folder (no folder name assigned)")
        return
    
    target_dir = os.path.join(base_dir, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, os.path.basename(filepath))
    
    # Handle file name conflicts
    base, ext = os.path.splitext(target_path)
    counter = 1
    while os.path.exists(target_path):
        target_path = f"{base}_{counter}{ext}"
        counter += 1
    
    try:
        shutil.move(filepath, target_path)
        logging.info(f"✅ Moved '{os.path.basename(filepath)}' to '{folder_name}'")
    except Exception as e:
        logging.warning(f"Failed to move {filepath} to {folder_name}: {e}")

def sort_by_content(folder_path):
    """Sort files in the folder based on content and filename, keeping uncategorizable files in place."""
    if not os.path.isdir(folder_path):
        logging.error(f"Invalid folder path: {folder_path}")
        return
    
    logging.info(f"Sorting files in: {folder_path}")
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue
        
        # Check if file type is supported
        if os.path.splitext(filename)[1].lower() not in SUPPORTED_EXTENSIONS:
            logging.info(f"Skipping unsupported file: {filename}")
            continue
        
        content = extract_text_from_file(filepath)
        logging.debug(f"Extracted content from {filename}: '{content[:100]}'")
        
        # Classify file
        folder_name = classify_file_content_with_ollama(content, filename)
        
        # Move file only if a valid folder name is assigned
        if folder_name:
            move_file_to_category(filepath, folder_name, folder_path)
        else:
            logging.info(f"Keeping '{filename}' in original folder (no folder name assigned)")
    
    logging.info("✅ Sorting completed.")