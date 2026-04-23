import os
from parsers.document_reader import Reader
from generators import md_builder
import cpp_linker

def run_pipeline(input_dir, vault_dir):
    notes_dir = os.path.join(vault_dir, "Notes")
    attachments_dir = os.path.join(vault_dir, "attachments")
    
    # Ensure Obsidian folders exist
    os.makedirs(notes_dir, exist_ok=True)
    os.makedirs(attachments_dir, exist_ok=True)

    print("\n--- Obsidian Links Configuration ---")
    user_input = input("Enter the words you wish to convert to an Obsidian Link (separated by commas):\n ")
    
    raw_keywords = user_input.split(',')
    master_glossary = [word.strip() for word in raw_keywords if word.strip()]
    
    # master_glossary used for creating links in Obsidian between files,
    # input for cpp_engine
    master_glossary = list(set(master_glossary))
    
    if not master_glossary:
        print("[WARNING] You introduced no words to be turned into links. The text will not be modified.")
    else:
        print(f"Registered {len(master_glossary)} words: {master_glossary} ")
    
    cpp_linker.initialize_search_tree(master_glossary)

    # --- PASS 1: Multiprocessing Extraction ---
    print("\n--- Pass 1: Extracting Documents ---")
    
    doc_reader = Reader(folder_path=input_dir, attachment_dir=attachments_dir)
    raw_results = doc_reader.scanner(input_dir)
    
    parsed_documents = {}

    for filepath, data in raw_results:
        if "error" in data:
            print(f"[FAILED] {os.path.basename(filepath)}: {data['error']}")
            continue
            
        title = data.get("title", os.path.basename(filepath).split('.')[0])
        parsed_documents[title] = data       
        print(f"[SUCCESS] Parsed: {title}")

    # --- PASS 2: Linking & Markdown Generation ---
    print("\n--- Pass 2: Building Obsidian Vault ---")
    for title, doc_data in parsed_documents.items():
        raw_text = doc_data.get('text', "")
        
        linked_text = cpp_linker.inject_obsidian_links(raw_text) # ex comment
        # linked_text = raw_text # Placeholder for C++
        
        out_path = os.path.join(notes_dir, f"{title}.md")
        
        # Write to Markdown
        success = md_builder.write_markdown(out_path, title, linked_text)
        if success:
            print(f"Created Note: {title}.md")

    print("\nVault Generation Complete! Open 'ObsidianVault' in Obsidian.")