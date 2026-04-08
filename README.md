Obsidian pipe

fisiere TXT DOC DOCX PPTX PDF EXCEL plus arhivate


CE VA FACE APLICATIA:

-va prelua fisiere de tipurile mentionate mai sus dintr un folder “input”
    optimize for RAM allocation!!!
    inputul va fi de forma: cursuri, capitole, prezentari, materiale, teme etc
    (science in particular)

-programul va extrage informatiile din fisiere
    parallel processing

-acesta le va scrie pe Obsidian (va pastra aceeasi formatare cu cea originala),
    formatandu le convenabil 

-Va incerca sa lege cuvinte cheie (definitii, capitole, notiuni comune in teoreme) folosind
"[[...]]" linking-ul nativ Obisidian intre fisiere si in cadrul aceluiasi fisier

-Reverse-engineering formule scrise cu LaTeX pentru a le include in fisierele MD ca text
    interpretabil de Obsidian


File Structure:

ObsidianPipe/
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
├── cpp_engine/               # C++ source code - scans text and turns keywords into native obsidian links
│   ├── CMakeLists.txt        # Build instructions for C++
│   ├── smart_linker.cpp      # Your C++ logic (Aho-Corasick, etc.)
│   └── bindings.cpp          # Pybind11 wrapper code
│
├── requirements.txt          # Python dependencies
└── README.md


-- TO DO
    _Replacing pdfplumber & Tessaract with MinerU_
    indentare originala (indentare noua Obsidian?)
    pptx support
    add timer to terminal wait for processing
    pozele sa fie pe background negru
    fa poza la tabel in loc de a l extrage
    URASTE diacriticele
    pozele ocupa tot randul in loc sa fie scalate la text

--  Idei
        minerU plugin 

