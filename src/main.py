import os
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

def load_config():
    # __file__ gets the path of the current script (e.g., src/main.py)
    # .parent.parent goes up to the root folder where config.json lives
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "config.json"
    
    if not config_path.exists():
        print(f"CRITICAL ERROR: {config_path.name} not found!")
        print("Please copy config.example.json, rename it to config.json, and fill in your local paths.")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

settings = load_config()
vault_directory = Path(settings.get("obsidian_vault_path"))
input_dir=Path(settings.get("downloaded_files_path"))

if not vault_directory.exists():
    print(f"Warning: The vault path {vault_directory} does not exist. Creating it now...")
    vault_directory.mkdir(parents=True, exist_ok=True)

# 4. Example: Saving a file downloaded from Classroom
##file_from_classroom = "Course_Syllabus.md"
##save_destination = vault_directory / file_from_classroom
##print(f"File will be saved to: {save_destination}")


#mihai modifica si tu ca mi e lene sa implementez altceva inafara de hardcodare
def main():
    print("========================================")
    print(" Starting Obsidian Vault Generation...  ")
    print("========================================")
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    # Orchestrator
    run_pipeline(input_dir, vault_directory)

if __name__ == "__main__":
    start=datetime.now()
    main()
    end=datetime.now()
    print(f"time: {end-start}")