Obsidian pipe

fisiere PDF DOCX DOC EXCEL PPTX plus arhivate 

[text](https://docs.google.com/document/d/1YTL5-UpWAgekY9-pVhkj84IXCnRbX_D6hcMgXLmBtLE/edit?tab=t.0)

obsidian_converter/
│
├── input_files/              # Put your raw PDFs, PPTXs here
├── ObsidianVault/            # The output directory
│   ├── attachments/          # Extracted images go here
│   └── Notes/                # Generated .md files go here
│
├── src/                      # Python source code
│   ├── main.py               # Entry point
│   ├── parsers/              # Submodule for extracting data
│   │   ├── __init__.py
│   │   └── document_reader.py
│   ├── generators/           # Submodule for writing Markdown
│   │   └── md_builder.py
│   └── orchestrator.py       # Manages the 2-pass processing flow
│
├── cpp_engine/               # C++ source code
│   ├── CMakeLists.txt        # Build instructions for C++
│   ├── smart_linker.cpp      # Your C++ logic (Aho-Corasick, etc.)
│   └── bindings.cpp          # Pybind11 wrapper code
│
├── requirements.txt          # Python dependencies
└── README.md


-- TO DO
    pozele sa fie pe background negru
    fa poza la tabel in loc de a l extrage
    cum sa se lege de path-ul OCR-ului fara absoulte path


