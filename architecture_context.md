# ObsidianPipe - Architecture Context

## Overview
A cross-platform Python pipeline that automates downloading educational content from Google Classroom/Drive and parses them into an Obsidian Markdown vault.

## Phase 1: Google Classroom Sync (`src/classroom_sync.py`)
*   **Authentication:** Uses `google-api-python-client` with relaxed OAuth scopes.
*   **Flow:** Interactive CLI that fetches active courses and available Drive materials.
*   **Features:** 
    *   Loops file selections so users can download multiple batches using space-separated numbers (e.g., `1 3 5`).
    *   Downloads files directly into the `input_directory` defined in `config.json`.
    *   Waits in a `while True` loop until the user types 'done', returning control to `main.py`.

## Phase 2: Obsidian Vault Generation (`src/orchestrator.py` & `src/main.py`)
*   **Control Flow:** `main.py` is the master controller. It runs `classroom_sync.interactive_sync()` first, waits for completion, and then immediately triggers the orchestrator.
*   **Parsing:** The orchestrator reads the freshly downloaded files from the input directory and maps them to Markdown.
*   **Linking Engine:** Utilizes a custom C++ extension for performance linking, with a pure Python regex fallback if the compiled `.dll` or `.so` is missing.

## Future Roadmap
*   **CI/CD:** GitHub Actions pipeline to automatically compile the C++ extensions for Windows and Linux and bundle them with the Python app.
*   **Cloud Architecture:** AWS backend for a product website and telemetry.