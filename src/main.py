import transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder as ved
import json
import sys
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

import classroom_sync

def main():
    
    print("\n========================================")
    print("  PHASE 1: Google Classroom Sync        ")
    print("========================================")
    
    classroom_sync.interactive_sync()
    
    print("\n========================================")
    print("  PHASE 2: Obsidian Vault Generation    ")
    print("========================================")
    
    settings = load_config()
    
    # Extract paths safely 
    vault_directory = Path(settings.get("obsidian_vault_path", ""))
    input_dir = Path(settings.get("input_directory", "")) 
    
    # If the input directory is relative make it absolute based on the root folder
    if not input_dir.is_absolute():
        input_dir = get_project_root() / input_dir

    # Check and create the Input directory if missing
    if not input_dir.exists():
        print(f"Warning: Input directory not found at {input_dir}. Creating it now...")
        input_dir.mkdir(parents=True, exist_ok=True)

    #  Check and create the Obsidian Vault directory if missing
    if not vault_directory.exists():
        print(f"Warning: The vault path {vault_directory} does not exist. Creating it now...")
        vault_directory.mkdir(parents=True, exist_ok=True)

    #  Pass the resolved pathlib objects to your Orchestrator
    run_pipeline(input_dir, vault_directory)

if __name__ == "__main__":
    start = datetime.now()
    main()
    end = datetime.now()
    print(f"Execution time: {end - start}")