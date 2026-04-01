import os
"""
    Writes content to a Markdown file.
    
    Args:
        output_path: The full path where the .md file should be saved.
        title: The title of the note (used as a header).
        content: The raw markdown text.
        images: A list of image filenames associated with this note (optional).
"""
def write_markdown(output_path: str, title: str, content: str, images: list = None) -> bool:
   
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write a frontmatter/title header
            f.write(f"# {title}\n\n")
            
            # Write the main content
            f.write(content)
            f.write("\n\n")
            
            # Optionally, if you want a footer showing attached images that weren't embedded inline
            if images:
                f.write("---\n**Attachments:**\n")
                for img in images:
                    f.write(f"![[{img}]]\n")
                    
        return True
    except Exception as e:
        print(f"Error writing markdown to {output_path}: {e}")
        return False