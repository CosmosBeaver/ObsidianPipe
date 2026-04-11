import os
from parsers.document_reader import Reader
from generators import md_builder
import cpp_linker
# Uncomment when C++ is ready

def run_pipeline(input_dir, vault_dir):
    notes_dir = os.path.join(vault_dir, "Notes")
    attachments_dir = os.path.join(vault_dir, "attachments")
    
    # Ensure Obsidian folders exist
    os.makedirs(notes_dir, exist_ok=True)
    os.makedirs(attachments_dir, exist_ok=True)

    # --- PASS 1: Multiprocessing Extraction ---
    print("\n--- Pass 1: Extracting Documents ---")
    
    doc_reader = Reader(folder_path=input_dir, attachment_dir=attachments_dir)
    raw_results = doc_reader.scanner(input_dir)
    
    # master_glossary used for creating links in Obsidian between files,
    # input for cpp_engine
    master_glossary = {}
    parsed_documents = {}
     

    for filepath, data in raw_results:
        if "error" in data:
            print(f"[FAILED] {os.path.basename(filepath)}: {data['error']}")
            continue
            
        title = data.get("title", os.path.basename(filepath).split('.')[0])
        parsed_documents[title] = data
        
        if "keywords" in data:
            for kw in data["keywords"]:
                if kw not in master_glossary:
                    master_glossary[kw] = title
            
        print(f"[SUCCESS] Parsed: {title}")

    # --- INITIALIZE C++ ENGINE ---
    print(f"\nInitializing C++ Smart Linker with {len(master_glossary)} terms...") #ex comment
    cpp_linker.initialize_search_tree(master_glossary) # ex comment

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