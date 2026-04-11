import os
from orchestrator import run_pipeline
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input_files")

#mihai modifica si tu ca mi e lene sa implementez altceva inafara de hardcodare
OUTPUT_DIR = r"C:\Users\colco\Documents\GitHub\ObsidianPipe\test_output"

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
    a=2
    main()
    end=datetime.now()
    print(f"time: {end-start}")