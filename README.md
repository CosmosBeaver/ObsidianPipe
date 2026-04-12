# Overview

ObsidianPipe is an automated knowledge extraction and linking pipeline designed specifically to streamline university exam preparation.

Students in rigorous academic fields (Mathematics, Physics, Chemistry, etc.) often struggle with studying from fragmented resources—lectures, scanned documents, and PDFs downloaded from Google Classroom or Microsoft Teams. Consolidating these scattered materials into a unified, searchable knowledge base is a highly manual and time-consuming process.

ObsidianPipe solves this by ingesting raw educational materials, utilizing AI-driven optical character recognition and layout analysis to extract text, mathematical formulas, and images, and automatically generating a structured, interconnected Obsidian Vault.

Suported languages are Romanian and English

# Architecture & How It Works

The pipeline operates in a two-pass system, combining the accuracy of modern AI with the performance of compiled C++:

- **Pass 1: Document Parsing & Extraction (Python / MinerU)** 
The application scans the `input_files` directory. Utilizing MinerU (and underlying models like PaddleOCR), it performs layout analysis and Math Formula Recognition (MFR) on complex scientific documents. It extracts the raw text, isolates and saves contextual images, and applies post-processing (such as Romanian diacritic correction and markdown formatting).

- **Pass 2: Vault Generation & Linking (C++ / Python)** 
To handle rapid text processing and cross-referencing, the pipeline utilizes a custom C++ engine exposed to Python via `pybind11`. The engine analyzes the extracted content to establish a master glossary. It then constructs local Markdown files and injects Obsidian wikilinks, packaging everything into a cohesive Obsidian Vault.

# Installation & Setup

## Prerequisites

- Python 3.12 (Highly recommended to ensure compatibility with specific AI model dependencies)
- C++ Build Tools (e.g., Visual Studio Build Tools on Windows, GCC/Clang on Linux/macOS)

Clone the repository and set up a Python virtual environment:
```
git clone https://github.com/cosmosbeaver/ObsidianPipe.git
cd ObsidianPipe

python -m venv venv_mineru

# On Windows:
venv_mineru\Scripts\activate
# On Linux/macOS:
source venv_mineru/bin/activate
```

Ensure pip is updated and install the required pipeline dependencies:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The pipeline relies on a compiled C++ module (`cpp_linker.pyd` or `.so`) to perform fast text linking. You must compile this before running the application:
```
#For Windows (PowerShell):

cd cpp_engine
mkdir build
cd build
$PYBIND_DIR = python -c "import pybind11; print(pybind11.get_cmake_dir())"
cmake .. -Dpybind11_DIR="$PYBIND_DIR"
cmake --build . --config Release
cd ../..

```
```
#For Linux / macOS (Bash):

cd cpp_engine
mkdir build
cd build
cmake .. -Dpybind11_DIR=$(python -c "import pybind11; print(pybind11.get_cmake_dir())")
cmake --build . --config Release
cd ../..
```
*Note: A successful build will automatically place the compiled binary into the `src/` directory.*

## Usage

1. **Provide Input Materials:** Place your source PDFs and documents into the `input_files/` directory at the root of the project.
 
2. **Execute the Pipeline:**
 
   `python src/main.py`

1. **Access Your Knowledge Base:** Once the terminal indicates the vault generation is complete, open the Obsidian application. Select **"Open folder as vault"** and target the newly created `ObsidianVault/` folder in the project root.

## Roadmap & Future Development

This application is currently a Work In Progress. Upcoming features include:

- **Dynamic Vault Targeting:** User interface elements to explicitly choose the target vault and output folder locations.

- **Semantic Cross-Linking:** Advanced parsing to automatically detect, index, and link highly reused academic terminology—specifically targeting definitions, lemmas, and theorems (e.g., terms prefaced by "Teorema", "Lema", "Definiție") both internally within a document and externally across the entire vault.