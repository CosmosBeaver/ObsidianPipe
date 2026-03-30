from obdocx import docx_to_obsidian

if __name__ == "__main__":
    # Temporary file paths, for testing
    MY_DOCX_FILE = r"C:\Users\Mihai\Documents\obtest.docx"
    MY_OBSIDIAN_VAULT = r"C:\Users\Mihai\Documents\Obsidian Vault"
    NOTE_TITLE = "My Migrated Docx Note"
    
    docx_to_obsidian(MY_DOCX_FILE, MY_OBSIDIAN_VAULT, NOTE_TITLE)
    