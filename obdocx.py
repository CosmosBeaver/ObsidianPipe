import os
import docx
from docx.shared import RGBColor

def docx_to_obsidian(docx_file_path, obsidian_vault_path, new_note_name):
  """
  Reads a .docx file and saves its text as a Markdown file in an Obsidian vault.
  """
  
  # 1. Read the .docx file directly
  print(f"Reading {docx_file_path}...")
  
  try:
    # Load the document using python-docx
    doc = docx.Document(docx_file_path)
    full_md_output = []
    
    # Extract text from all paragraphs
    for paragraph in doc.paragraphs:
      para_text = ""
      for run in paragraph.runs:
        text = run.text
        if not text or text.isspace():  # Skip empty or whitespace-only runs
          continue
        
        # Handle bold and italic (Markdown style)
        if run.bold:
          text = f"**{text}**"
        if run.italic:
          text = f"_{text}_"
          
        # Handle color and size (HTML style for Obsidian)
        style_parts = []
        
        # Font size (Converted from half-points to pixels/em)
        if run.font.size:
          # run.font.size.pt gives the size in points
          style_parts.append(f"font-size:{run.font.size.pt}pt")
        
        # Font color
        if run.font.color and run.font.color.rgb:
          style_parts.append(f"color:#{run.font.color.rgb}")
          
        if style_parts:
          style_str = "; ".join(style_parts)
          text = f'<span style="{style_str}">{text}</span>'
        
        para_text += text

      full_md_output.append(para_text)
      
    full_content = "\n\n".join(full_md_output)
    
    # File saving logic
    
    md_file_path = os.path.join(obsidian_vault_path, f"{new_note_name}.md")
    with open(md_file_path, 'w', encoding='utf-8') as f:
      f.write(full_content)
    
    print("Success! Note added to Obsidian.")
    
  except Exception as e:
    print(f"Error writing to Obsidian : {e}")
