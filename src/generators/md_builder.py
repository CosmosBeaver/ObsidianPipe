"""
    Writes content to a Markdown file.
    
    Args:
        output_path: The full path where the .md file should be saved.
        title: The title of the note (used as a header).
        content: The raw markdown text.
        images: A list of image filenames associated with this note (optional).
"""
import os
def write_markdown(output_path: str, title: str, content: str) -> bool:
    """Writes the final string to a Markdown file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing markdown to {output_path}: {e}")
        return False