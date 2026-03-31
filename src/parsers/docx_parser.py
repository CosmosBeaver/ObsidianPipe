import os
import docx

def extract_content(docx_path: str, attachment_dir: str) -> dict:
    """
    Extracts content from a .docx file and converts it to a structured dictionary.
    This function does NOT write any files, it only extracts data.

    Args:
        docx_path: Path to the input .docx file.
        attachment_dir: Path to save any extracted images (not yet implemented).

    Returns:
        A dictionary containing the title, text content, and keywords.
        Example: {'title': 'My Doc', 'text': '...', 'keywords': {'Header1', 'Important'}, 'images': []}
    """
    print(f"Parsing DOCX: {docx_path}")
    try:
        doc = docx.Document(docx_path)
        md_output = []
        keywords = set()

        # Use filename as title, without extension
        title = os.path.splitext(os.path.basename(docx_path))[0]

        for p in doc.paragraphs:
            # Handle headings
            if p.style.name.startswith('Heading'):
                try:
                    level = int(p.style.name[-1])
                    prefix = '#' * level
                    md_output.append(f"\n{prefix} {p.text}\n")
                    if p.text:
                        keywords.add(p.text)
                    continue
                except (ValueError, IndexError):
                    pass # Not a standard 'Heading 1', 'Heading 2', etc.

            # Handle regular paragraphs and formatting
            para_text = ""
            for run in p.runs:
                text = run.text
                if run.bold:
                    text = f"**{text}**"
                    if text: keywords.add(run.text) # Add unformatted bold text to keywords
                if run.italic:
                    text = f"*{text}*"
                para_text += text
            md_output.append(para_text)

        full_text = "\n\n".join(md_output)
        return {"title": title, "text": full_text, "keywords": keywords, "images": []}

    except Exception as e:
        print(f"Error parsing DOCX file {docx_path}: {e}")
        return None
