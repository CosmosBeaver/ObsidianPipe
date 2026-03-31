from parsers import pdf_parser, docx_parser
import os

ATTACHMENT_DIR = "ObsidianVault/attachments"


def get_files(directory):
    """Scans a directory and returns a list of all valid file paths to process."""
    file_paths = []
    valid_extensions = {'.pdf', '.docx', '.pptx', '.txt'}
    print(f"Scanning for files in '{os.path.abspath(directory)}'...")
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in valid_extensions:
                file_paths.append(os.path.join(root, file))
    return file_paths

def parse_file(filepath):
    """Routes the file to the correct parser based on extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return pdf_parser.extract_content(filepath, ATTACHMENT_DIR)
    elif ext == '.docx':
        return docx_parser.extract_content(filepath, ATTACHMENT_DIR)
    # ... handle other file types ...
    else:
        print(f"Warning: No parser available for file type {ext}. Skipping {filepath}")
        return None