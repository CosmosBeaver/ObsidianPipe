from generators import md_builder
from orchestrator import get_files, parse_file
import os
# This is the C++ module compiled using pybind11
#import cpp_linker 

INPUT_DIR = "input_docs"
OUTPUT_DIR = "ObsidianVault/Notes"
ATTACHMENT_DIR = "ObsidianVault/attachments"

def main():
    print("Starting Obsidian Vault Generation...")
    files_to_process = get_files(INPUT_DIR)
    if not files_to_process:
        print(f"No files found in '{INPUT_DIR}'. Exiting.")
        return
    
    # --- PASS 1: Extraction & Indexing ---
    print("Pass 1: Parsing documents...")
    parsed_documents = {}
    master_glossary = set() # Store important terms (e.g., headers, bolded text)
    
    for file in files_to_process:
        # extract_content returns a dict: {'title': str, 'text': str, 'keywords': set, 'images': list}
        doc_data = parse_file(file) 
        if doc_data:
            parsed_documents[doc_data['title']] = doc_data
            master_glossary.update(doc_data['keywords'])
    
    # Initialize your C++ Engine with the terms we want to link
    
    # print("Initializing C++ Smart Linker...")
    # cpp_linker.build_search_tree(list(master_glossary))
    
    # --- PASS 2: Linking & Writing ---
    print("Pass 2: Injecting links and writing Markdown...")
    for title, doc_data in parsed_documents.items():
        raw_text = doc_data['text']
        
        # Use C++ to heavily process the string and inject Obsidian links: [[Keyword]]
        # linked_text = cpp_linker.inject_obsidian_links(raw_text)
        linked_text = raw_text # Placeholder until C++ is integrated
        # Generate final MD file
        output_path = os.path.join(OUTPUT_DIR, f"{title}.md")
        md_builder.write_markdown(output_path, title, linked_text, doc_data.get('images', []))

    print("Vault generation complete!")

if __name__ == "__main__":
    main()