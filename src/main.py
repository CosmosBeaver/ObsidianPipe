import transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder as ved
import json
import sys
import os
from pathlib import Path

# --- SURGICAL RUNTIME PATCH FOR MINERU ---
# This intercepts the model during execution and drops the 'cache_position' 
# argument before it reaches MinerU's outdated decoder, preventing the crash.
orig_ved_forward = ved.VisionEncoderDecoderModel.forward

def patched_ved_forward(self, *args, **kwargs):
    if hasattr(self, 'decoder') and not hasattr(self.decoder, '_is_patched_for_cache'):
        orig_decoder_forward = self.decoder.forward
        def new_decoder_forward(*d_args, **d_kwargs):
            d_kwargs.pop('cache_position', None)  # Kill the offending argument
            return orig_decoder_forward(*d_args, **d_kwargs)
        self.decoder.forward = new_decoder_forward
        self.decoder._is_patched_for_cache = True
        
    return orig_ved_forward(self, *args, **kwargs)

ved.VisionEncoderDecoderModel.forward = patched_ved_forward
# -----------------------------------------


from orchestrator import run_pipeline
from datetime import datetime
import classroom_sync

def get_project_root() -> Path:
    """Returns the absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent

def load_config() -> dict:
    """Loads the config.json file from the project root."""
    config_path = get_project_root() / "config.json"
    
    if not config_path.exists():
        print(f"CRITICAL ERROR: {config_path.name} not found!")
        print("Please copy config.example.json, rename it to config.json, and fill in your local paths.")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

def introduce_keywords_menu(vault_directory: Path):
    """
    Menu to select specific markown files and inject keywords using the cpp_engine
    """
    notes_dir = vault_directory / "Notes"
    
    # Error handling: Ensure the directory exists
    if not notes_dir.exists():
        print(f"\n[ERROR] Notes directory not found at {notes_dir}")
        print(f"Please run Option [1] first to generate the Obsidian Vault")
        return
    
    # Fetch all markdown files
    files = list(notes_dir.glob("*.md"))
    if not files:
        print(f"\n[WARNING] No markdown files found in the Notes directory to process")
        return
    
    print("\n========================================")
    print("        SELECT FILES FOR KEYWORDS       ")
    print("========================================")
    for idx, file in enumerate(files, start=1):
        print(f"[{idx}] {file.name}")
    print("========================================")
    
    # User input for file selection (comma-separated or 'all')
    selection = input("\nSelect files by number (comma-separated, or type 'all'): ").strip()
    selected_files = []
    
    if selection.lower() == 'all':
        selected_files = files
    else:
        try:
            # Parse user input securely, ignoring empty spaces
            indices = [int(x.strip()) for x in selection.split(',') if x.strip()]
            for i in indices:
                if 1 <= i <= len(files):
                    selected_files.append(files[i-1])
                else:
                    print(f"[WARNING] Index {i} is out of bounds and will be skipped")
        except ValueError:
            print("[ERROR] Invalid input. Please enter numbers separated by commas")
            return
    
    if not selected_files:
        print("[WARNING] No valid files were selected. Returning to main menu.")
        return
    
    # Input the keywords
    user_input = input("\nEnter the words you wish to convert to an Obsidian Link (separated by commas):\n")
    raw_keywords = [w.strip() for w in user_input.split(',') if w.strip()]
    master_glossary = list(set(raw_keywords))
    
    if not master_glossary:
        print("[WARNING] No keywords introduced. Returning to main menu.")
        return
    
    # Attempt to load the C++ engine and process the files
    try:
        import cpp_linker
        print(f"\n[INFO] Initializing C++ Engine with {len(master_glossary)} keywords...")
        cpp_linker.initialize_search_tree(master_glossary)
        
        print("\n--- Pass: Updating Obsidian Links ---")
        for file_path in selected_files:
            try:
                # Read original markdown
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
                # Performance optimization: C++ engine handles the string matching
                linked_text = cpp_linker.inject_obsidian_links(text)
                
                # Only write back to disk if modification were actually made
                if text != linked_text:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(linked_text)
                    print(f"[SUCCESS] Updated links in: {file_path.name}")
                else:
                    print(f"[INFO] No keyword matches found in: {file_path.name}")
                    
            except Exception as e:
                print(f"[ERROR] Failed processing {file_path.name}: {e}")
        
    except ImportError:
        print("\n[CRITICAL ERROR] C++ Engine (cpp_linker) is not available.")
        print("Please ensure it is compiled properly using CMake before running this option.")
                    

def main():
    settings = load_config()
    
    # Extract paths safely 
    vault_directory = Path(settings.get("obsidian_vault_path", ""))
    input_dir = Path(settings.get("input_directory", ""))
    
    # If the input directory is relative make it absolute based on the root folder
    if not input_dir.is_absolute():
        input_dir = get_project_root() / input_dir
        
    # Main CLI Loop
    while True:
        print("\n========================================")
        print("          OBSIDIAN PIPE SYSTEM          ")
        print("========================================")
        print("[1] Choose files to generate as an Obsidian Note (Run Main Program)")
        print("[2] Introduce Keywords to Specific Files")
        print("[3] Exit")
        print("========================================")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            start = datetime.now()
    
            print("\n========================================")
            print("  PHASE 1: Google Classroom Sync        ")
            print("========================================")
            classroom_sync.interactive_sync()
    
            print("\n========================================")
            print("  PHASE 2: Obsidian Vault Generation    ")
            print("========================================")
            
            # Check and create the Input directory if missing
            if not input_dir.exists():
                print(f"Warning: Input directory not found at {input_dir}. Creating it now...")
                input_dir.mkdir(parents=True, exist_ok=True)
                
            #  Check and create the Obsidian Vault directory if missing
            if not vault_directory.exists():
                print(f"Warning: The vault path {vault_directory} does not exist. Creating it now...")
                vault_directory.mkdir(parents=True, exist_ok=True)

            # Pass the resolved pathlib objects to your Orchestrator
            # Note: We tell it not to prompt for keywords interactively here if you prefer Option 2 to handle it exclusively
            run_pipeline(input_dir, vault_directory, prompt_keywords=False)
            
            end = datetime.now()
            print(f"\nExecution time : {end - start}")
            
        elif choice == '2':
            introduce_keywords_menu(vault_directory)
            
        elif choice == '3':
            print("\nExiting program. Goodbye!")
            sys.exit(0)
            
        else:
            print("\n[ERROR] Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()