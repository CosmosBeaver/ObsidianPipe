import os

class Reader:
    def __init__(self, folder_path, attachment_dir=None):
        self.folder = folder_path
        self.attachment_dir = attachment_dir
        
        # Ensure attachment directory exists if provided
        if self.attachment_dir:
            os.makedirs(self.attachment_dir, exist_ok=True)
            
            
#  This file exposes the specific parser functions so they are easy to import
# from .pdf_parser import extract_pdf
# from .docx_parser import extract_docx
# from .pptx_parser import extract_pptx

#  Now, in  orchestrator, you can just do:
#  from parsers import extract_pdf, extract_docx