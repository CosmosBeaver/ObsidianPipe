import os
import argparse
from datetime import datetime
import transformers.models.vision_encoder_decoder.modeling_vision_encoder_decoder as ved
from orchestrator import run_pipeline

input_dir = "a"
output_dir = "b"

def parse_config():
    parser = argparse.ArgumentParser(description="Obsidian Vault Generator")
    
    #define the arguments
    parser.add_argument(
        '--input',
        type=str,
        help="Path to the input directory"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="Path to the output directory"
    )
    
    args = parser.parse_args()
    
    # Priority 1: CLI arguments
    # Priority 2: Environment variables (Great for Docker)
    # Priority 3: Fallback defaults
    input_dir = args.input or os.getenv('INPUT_DIR') or '/ObsidianPipe/input_files'
    output_dir = args.output or os.getenv('OUTPUT_DIR') or '/ObsidianPipe/test_output'
    
    return input_dir, output_dir

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

def main(input_dir, output_dir):
    print("========================================")
    print(" Starting Obsidian Vault Generation...  ")
    print("========================================")
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    # Orchestrator
    run_pipeline(input_dir, output_dir)

if __name__ == "__main__":
    start=datetime.now()
    
    # Grab the arguments from the terminal or Docker environment
    dynamic_input, dynamic_output = parse_config()
    
    # Feed those arguments into the main function
    main(dynamic_input, dynamic_output)
    
    end = datetime.now()
    print(f"time: {end-start}")