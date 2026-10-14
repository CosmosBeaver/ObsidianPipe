import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
CPP_DIR = ROOT_DIR / "cpp_engine"
BUILD_DIR = CPP_DIR / "build"

def run_cmd(cmd, cwd=ROOT_DIR, check=True):
    print(f"\n[EXEC] {' '.join(map(str, cmd))}")
    return subprocess.run(cmd, cwd=cwd, check=check)

def step_1_install_python_deps():
    print("\n====================================================")
    print(" [1/4] Installing Python Dependencies")
    print("====================================================")
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    req_file = ROOT_DIR / "requirements.txt"
    if req_file.exists():
        run_cmd([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
        # Fix OpenCV collision caused by having contrib, standard, and headless in requirements.txt
        print("\n[INFO] Ensuring clean OpenCV installation...")
        run_cmd([
            sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-deps",
            "opencv-contrib-python==4.10.0.84"
        ], check=False)

def step_2_download_ai_weights():
    print("\n====================================================")
    print(" [2/4] Downloading MinerU & OCR AI Weights")
    print("====================================================")
    try:
        from huggingface_hub import snapshot_download
        
        models_dir = ROOT_DIR / "models"
        models_dir.mkdir(exist_ok=True)

        print("[INFO] Downloading PDF-Extract-Kit-1.0 weights (Layout, MFD, MFR, Table)...")
        model_path = snapshot_download(
            repo_id="opendatalab/PDF-Extract-Kit-1.0",
            local_dir=str(models_dir / "PDF-Extract-Kit-1.0"),
            local_dir_use_symlinks=False
        )

        # Configure ~/magic-pdf.json so magic-pdf knows where the weights live
        home_config = Path.home() / "magic-pdf.json"
        magic_pdf_config = {
            "bucket_info": {},
            "models-dir": str(Path(model_path) / "models").replace("\\", "/"),
            "device-mode": "cpu",  # Change to "cuda" if GPU is available
            "layout-config": {"model": "doclayout_yolo"},
            "formula-config": {
                "mfd_model": "yolo_v8_mfd",
                "mfr_model": "unimernet_small",
                "enable": True
            },
            "table-config": {
                "model": "rapid_table",
                "enable": True,
                "max_time": 400
            }
        }
        
        with open(home_config, "w", encoding="utf-8") as f:
            json.dump(magic_pdf_config, f, indent=4)
        print(f"[OK] Configured MinerU weights at: {home_config}")

    except Exception as e:
        print(f"[WARNING] Automatic AI weight download encountered an issue: {e}")
        print("[INFO] Weights will be downloaded on first run if needed.")

def step_3_build_cpp_engine():
    print("\n====================================================")
    print(" [3/4] Compiling C++ Linker Engine (pybind11)")
    print("====================================================")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        pybind11_cmake_dir = subprocess.check_output(
            [sys.executable, "-m", "pybind11", "--cmakedir"], text=True
        ).strip()

        run_cmd(["cmake", "..", f"-Dpybind11_DIR={pybind11_cmake_dir}"], cwd=BUILD_DIR)
        run_cmd(["cmake", "--build", ".", "--config", "Release"], cwd=BUILD_DIR)
        print("[OK] C++ engine compiled and placed in src/!")
    except Exception as e:
        print("\n[WARNING] Could not compile the C++ extension (C++ Build Tools may be missing).")
        print("[INFO] ObsidianPipe will automatically use the pure-Python regex fallback.")
        print(f"[DEBUG] Details: {e}")

def step_4_initialize_workspace():
    print("\n====================================================")
    print(" [4/4] Initializing Workspace & Configuration")
    print("====================================================")
    for folder in ["input_files", "data/input", "ObsidianVault"]:
        (ROOT_DIR / folder).mkdir(parents=True, exist_ok=True)

    config_example = ROOT_DIR / "config.example.json"
    config_target = ROOT_DIR / "config.json"
    if config_example.exists() and not config_target.exists():
        shutil.copy2(config_example, config_target)
        print("[OK] Created config.json from config.example.json.")
    else:
        print("[INFO] config.json already exists.")

if __name__ == "__main__":
    step_1_install_python_deps()
    step_2_download_ai_weights()
    step_3_build_cpp_engine()
    step_4_initialize_workspace()
    print("\n====================================================")
    print(" [SUCCESS] ObsidianPipe is ready! Use run.bat to start.")
    print("====================================================")