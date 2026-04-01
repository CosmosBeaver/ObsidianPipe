import os
from orchestrator import run_pipeline
from datetime import datetime

# Use absolute paths to avoid folder resolution issues
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input_files")
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