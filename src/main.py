import os
import transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder as ved

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input_files")

#mihai modifica si tu ca mi e lene sa implementez altceva inafara de hardcodare
OUTPUT_DIR = os.path.join(BASE_DIR, "ObsidianVault")
def main():
    print("========================================")
    print(" Starting Obsidian Vault Generation...  ")
    print("========================================")
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory not found at {INPUT_DIR}")
        return

    # Orchestrator
    run_pipeline(INPUT_DIR, OUTPUT_DIR)

if __name__ == "__main__":
    start=datetime.now()
    main()
    end=datetime.now()
    print(f"time: {end-start}")