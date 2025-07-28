AI File Organizer

Overview

The AI File Organizer is a Python-based application that automatically sorts files in a specified folder into categorized subfolders based on their content and filename. It leverages the Gemma language model (via the Ollama API) to intelligently analyze file content and suggest meaningful folder names. The project supports PDF, DOCX, and TXT files, and ensures that uncategorizable files remain in their original folder, avoiding the creation of an "uncategorised" folder. This tool is ideal for organizing documents in personal or professional settings, demonstrating skills in Python, natural language processing (NLP), file handling, and AI integration.

Features





Content-Based Sorting: Extracts text from files (PDF, DOCX, TXT) and uses the Gemma model to suggest context-appropriate folder names.



Filename Consideration: Prioritizes filenames as a strong indicator for categorization (e.g., AI_Intro.pdf might be sorted into Artificial_Intelligence).



Filesystem-Friendly: Sanitizes folder names to ensure compatibility with Windows and other operating systems (e.g., removes invalid characters, limits length).



No Default Folder for Uncategorizable Files: Files that cannot be categorized remain in their original folder, as per user requirements.



Efficient Processing: Limits text extraction to the first three pages of PDFs and caps text at 2000 characters for performance.



Error Handling: Robustly handles file reading errors, invalid model responses, and filename conflicts in target folders.



Logging: Provides detailed logs for debugging and tracking the sorting process.

Technologies Used





Python: Core programming language for the application.



Libraries:





PyPDF2: For extracting text from PDF files.



python-docx: For extracting text from DOCX files.



ollama: For interacting with the Gemma language model.



os, shutil: For file and folder operations.



logging: For detailed logging of operations.



re: For sanitizing folder names.



AI Model: Gemma (via Ollama API) for content analysis and folder name suggestion.

Prerequisites





Python 3.8 or higher



Ollama server running locally with the Gemma model (http://localhost:11434)



Required Python packages:





PyPDF2



python-docx



ollama
