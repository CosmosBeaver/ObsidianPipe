import os
from .parsers.document_reader import Reader  # Import your script here!
from generators import md_builder
#import cpp_linker 

def run_pipeline(input_dir, output_vault_dir):
    notes_dir = os.path.join(output_vault_dir, "Notes")
    attachments_dir = os.path.join(output_vault_dir, "attachments")
    
    # --- PASS 1: Extraction via Multiprocessing ---
    print("Pass 1: Running your multiprocessing extractor...")
    
    # Initialize your awesome Reader class
    extractor = Reader(folder_path=input_dir, attachment_dir=attachments_dir)
    
    # This runs your scanner, which returns a list of tuples: (filepath, data_dict)
    raw_results = extractor.scanner(input_dir)
    
    parsed_data_store = {}
    master_glossary = set()

    for result in raw_results:
        filepath = result[0]
        data = result[1]
        
        if "error" in data:
            print(f"Failed to parse {filepath}: {data['error']}")
            continue
            
        # Store the successful extractions
        title = data.get("title", os.path.basename(filepath))
        parsed_data_store[title] = data
        
        # If we extract keywords later, add them to glossary
        if "keywords" in data:
            master_glossary.update(data["keywords"])

    '''
    # --- C++ INITIALIZATION ---
    print(f"Initializing C++ Smart Linker with {len(master_glossary)} terms...")
    cpp_linker.initialize_search_tree(list(master_glossary))

    # --- PASS 2: Link and Write ---
    print("Pass 2: Building Obsidian .md files...")
    for title, data in parsed_data_store.items():
        
        raw_text = data.get('text', "")
        
        # Delegate heavy string processing to C++
        linked_text = cpp_linker.inject_links(raw_text)
        
        # Write the final .md file
        out_path = os.path.join(notes_dir, f"{title}.md")
        md_builder.write_markdown(out_path, title, linked_text)

    print("Obsidian Vault Generation Complete!")
    '''