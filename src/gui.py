import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import json
from pathlib import Path

# Import pipeline dependencies
import classroom_sync
from orchestrator import run_pipeline

try:
    import cpp_linker  # type: ignore
    HAS_CPP_ENGINE = True
except ImportError:
    HAS_CPP_ENGINE = False


class RedirectText:
    """Redirects stdout prints into a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, string):
        self.output.insert(tk.END, string)
        self.output.see(tk.END)

    def flush(self):
        pass


class ObsidianPipeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ObsidianPipe - Dynamic Linker & Sync")
        self.root.geometry("850x900")
        
        self.creds = None
        self.courses = []
        self.materials = []
        self.active_keywords = set()  # In-memory dynamic glossary
        
        self.build_ui()
        self.load_config_paths()
        
        sys.stdout = RedirectText(self.console_text)
        
        if not HAS_CPP_ENGINE:
            print("[WARNING] C++ Engine (cpp_linker) not detected. Dynamic linking will be unavailable.")

    def build_ui(self):
        # Create Notebook (Tabs) for clean workflow separation
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        tab_pipeline = ttk.Frame(notebook)
        tab_keywords = ttk.Frame(notebook)
        
        notebook.add(tab_pipeline, text="1. Classroom & Extraction")
        notebook.add(tab_keywords, text="2. Dynamic Keyword Linker")

        # ==========================================
        # TAB 1: PIPELINE & CONFIG
        # ==========================================
        config_frame = ttk.LabelFrame(tab_pipeline, text="Paths & Storage")
        config_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(config_frame, text="Input Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.input_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(config_frame, text="Browse", command=lambda: self.browse_dir(self.input_var)).grid(row=0, column=2, padx=5)

        ttk.Label(config_frame, text="Obsidian Vault:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.vault_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.vault_var, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(config_frame, text="Browse", command=lambda: self.browse_dir(self.vault_var)).grid(row=1, column=2, padx=5)
        ttk.Button(config_frame, text="Save Paths", command=self.save_config_paths).grid(row=2, column=1, pady=5)

        sync_frame = ttk.LabelFrame(tab_pipeline, text="Google Classroom Sync")
        sync_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.auth_btn = ttk.Button(sync_frame, text="Authenticate with Google", command=self.authenticate)
        self.auth_btn.pack(pady=5)

        self.course_combo = ttk.Combobox(sync_frame, state="disabled")
        self.course_combo.pack(fill="x", padx=10, pady=5)
        self.course_combo.bind("<<ComboboxSelected>>", self.on_course_select)

        self.materials_listbox = tk.Listbox(sync_frame, selectmode=tk.MULTIPLE, height=6)
        self.materials_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(sync_frame, text="Download Selected Files", command=self.download_materials).pack(pady=5)
        
        ttk.Button(
            tab_pipeline, 
            text="Transform into Obsidian notes", 
            command=self.start_pipeline_thread
        ).pack(fill="x", padx=10, pady=10)

        # ==========================================
        # TAB 2: DYNAMIC KEYWORD LINKER
        # ==========================================
        keyword_input_frame = ttk.LabelFrame(tab_keywords, text="Add Keywords / Academic Terms")
        keyword_input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            keyword_input_frame, 
            text="Enter words or comma-separated phrases:"
        ).pack(anchor="w", padx=5, pady=2)

        input_row = ttk.Frame(keyword_input_frame)
        input_row.pack(fill="x", padx=5, pady=5)

        self.keyword_entry = ttk.Entry(input_row)
        self.keyword_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.keyword_entry.bind("<Return>", lambda event: self.add_keywords())

        ttk.Button(input_row, text="Add Term(s)", command=self.add_keywords).pack(side="left", padx=2)
        ttk.Button(input_row, text="Clear All", command=self.clear_keywords).pack(side="left", padx=2)

        # Keyword tag list
        glossary_frame = ttk.LabelFrame(tab_keywords, text="Active Master Glossary")
        glossary_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.keywords_listbox = tk.Listbox(glossary_frame, selectmode=tk.SINGLE, height=7)
        self.keywords_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        kw_scroll = ttk.Scrollbar(glossary_frame, orient="vertical", command=self.keywords_listbox.yview)
        kw_scroll.pack(side="left", fill="y", pady=5)
        self.keywords_listbox.config(yscrollcommand=kw_scroll.set)

        ttk.Button(glossary_frame, text="Remove Selected", command=self.remove_keyword).pack(side="left", padx=5, anchor="n", pady=5)

        # Note selection frame
        notes_frame = ttk.LabelFrame(tab_keywords, text="Target Markdown Notes")
        notes_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Separate path finder
        linker_path_ctrl = ttk.Frame(notes_frame)
        linker_path_ctrl.pack(fill="x", padx=5, pady=5)
        ttk.Label(linker_path_ctrl, text="Notes Folder:").pack(side="left")
        self.linker_path_var = tk.StringVar()
        self.linker_path_var.trace_add("write", lambda *args: self.refresh_vault_notes())
        ttk.Entry(linker_path_ctrl, textvariable=self.linker_path_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(linker_path_ctrl, text="Browse", command=lambda: self.browse_dir(self.linker_path_var)).pack(side="left")

        notes_ctrl = ttk.Frame(notes_frame)
        notes_ctrl.pack(fill="x", padx=5, pady=3)

        self.all_notes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            notes_ctrl, 
            text="Apply to ALL Notes in Vault", 
            variable=self.all_notes_var, 
            command=self.toggle_notes_selection
        ).pack(side="left")

        ttk.Button(notes_ctrl, text="Refresh Vault Notes", command=self.refresh_vault_notes).pack(side="right")

        self.notes_listbox = tk.Listbox(notes_frame, selectmode=tk.MULTIPLE, height=6)
        self.notes_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.notes_listbox.config(state="disabled")

        ttk.Button(
            tab_keywords, 
            text="Go!", 
            command=self.start_linking_thread
        ).pack(fill="x", padx=10, pady=10)

        # ==========================================
        # CONSOLE OUTPUT (Shared across tabs)
        # ==========================================
        console_frame = ttk.LabelFrame(self.root, text="Terminal Logs")
        console_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.console_text = tk.Text(console_frame, wrap="word", height=10, bg="#1e1e1e", fg="#4af626")
        self.console_text.pack(fill="both", expand=True, padx=5, pady=5)

    # --- Configuration Methods ---
    def browse_dir(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
            self.refresh_vault_notes()

    def load_config_paths(self):
        config_path = classroom_sync.get_project_root() / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.input_var.set(data.get("input_directory", ""))
                self.vault_var.set(data.get("obsidian_vault_path", ""))
                self.linker_path_var.set(data.get("linker_notes_path", ""))
            self.refresh_vault_notes()

    def save_config_paths(self):
        config_path = classroom_sync.get_project_root() / "config.json"
        data = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        data["input_directory"] = self.input_var.get()
        data["obsidian_vault_path"] = self.vault_var.get()
        data["linker_notes_path"] = self.linker_path_var.get()
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("[GUI] Paths saved successfully.")
        self.refresh_vault_notes()

    # --- Classroom Sync Methods ---
    def authenticate(self):
        print("[GUI] Authenticating with Google Classroom...")
        threading.Thread(target=self._auth_thread, daemon=True).start()

    def _auth_thread(self):
        self.creds = classroom_sync.authenticate_google()
        if self.creds:
            self.courses = classroom_sync.get_active_courses(self.creds)
            names = [c.get("name", "Unknown") for c in self.courses]
            self.root.after(0, lambda: self._update_course_combo(names))

    def _update_course_combo(self, names):
        self.course_combo["values"] = names
        self.course_combo["state"] = "readonly"
        self.auth_btn.config(text="Authenticated \u2713", state="disabled")
        print(f"[GUI] Successfully loaded {len(names)} active courses.")

    def on_course_select(self, event):
        idx = self.course_combo.current()
        course_id = self.courses[idx]["id"]
        threading.Thread(target=self._fetch_materials_thread, args=(course_id,), daemon=True).start()

    def _fetch_materials_thread(self, course_id):
        self.materials = classroom_sync.get_course_materials(self.creds, course_id)
        self.root.after(0, self._update_materials_list)

    def _update_materials_list(self):
        self.materials_listbox.delete(0, tk.END)
        for m in self.materials:
            self.materials_listbox.insert(tk.END, m["title"])

    def download_materials(self):
        selected_indices = self.materials_listbox.curselection()
        if not selected_indices:
            print("[WARNING] No files selected for download.")
            return

        selected_files = [self.materials[i] for i in selected_indices]
        save_dir = Path(self.input_var.get())
        if not save_dir.is_absolute():
            save_dir = classroom_sync.get_project_root() / save_dir

        threading.Thread(target=self._download_thread, args=(selected_files, save_dir), daemon=True).start()

    def _download_thread(self, files, save_dir):
        save_dir.mkdir(parents=True, exist_ok=True)
        classroom_sync.download_selected_files(self.creds, files, save_dir)
        print("[GUI] File download complete.")

    def start_pipeline_thread(self):
        input_dir = self.input_var.get()
        vault_dir = self.vault_var.get()
        if not input_dir or not vault_dir:
            print("[ERROR] Configure both Input and Vault paths first.")
            return

        threading.Thread(
            target=lambda: run_pipeline(input_dir, vault_dir, prompt_keywords=False),
            daemon=True
        ).start()

    # --- Dynamic Keyword & Linking Methods ---
    def add_keywords(self):
        raw_text = self.keyword_entry.get().strip()
        if not raw_text:
            return

        terms = [t.strip() for t in raw_text.split(",") if t.strip()]
        for term in terms:
            if term not in self.active_keywords:
                self.active_keywords.add(term)
                self.keywords_listbox.insert(tk.END, term)

        self.keyword_entry.delete(0, tk.END)
        print(f"[KEYWORDS] Added: {terms}. Total active: {len(self.active_keywords)}")

    def remove_keyword(self):
        selection = self.keywords_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        term = self.keywords_listbox.get(idx)
        self.active_keywords.remove(term)
        self.keywords_listbox.delete(idx)
        print(f"[KEYWORDS] Removed: '{term}'. Remaining: {len(self.active_keywords)}")

    def clear_keywords(self):
        self.active_keywords.clear()
        self.keywords_listbox.delete(0, tk.END)
        print("[KEYWORDS] Cleared all keywords.")

    def toggle_notes_selection(self):
        if self.all_notes_var.get():
            self.notes_listbox.config(state="disabled")
        else:
            self.notes_listbox.config(state="normal")

    def refresh_vault_notes(self):
        target_path = self.linker_path_var.get()
        if not target_path:
            return

        notes_dir = Path(target_path)
        self.notes_listbox.config(state="normal")
        self.notes_listbox.delete(0, tk.END)

        if notes_dir.exists() and notes_dir.is_dir():
            files = list(notes_dir.glob("*.md"))
            for f in sorted(files, key=lambda x: x.name):
                self.notes_listbox.insert(tk.END, f.name)
            print(f"[GUI] Found {len(files)} markdown notes in {notes_dir.name}.")
        
        if self.all_notes_var.get():
            self.notes_listbox.config(state="disabled")

    def start_linking_thread(self):
        if not HAS_CPP_ENGINE:
            print("[CRITICAL ERROR] C++ engine is not available.")
            return

        if not self.active_keywords:
            print("[WARNING] Keyword glossary is empty. Add keywords before running the linker.")
            return

        notes_dir = Path(self.linker_path_var.get())
        if not notes_dir.exists() or not notes_dir.is_dir():
            print(f"[ERROR] Invalid directory: {notes_dir}")
            return

        # Determine target files
        all_files = list(notes_dir.glob("*.md"))
        if self.all_notes_var.get():
            target_files = all_files
        else:
            selected_indices = self.notes_listbox.curselection()
            if not selected_indices:
                print("[WARNING] No notes selected. Check 'Apply to ALL Notes' or select specific files.")
                return
            target_names = {self.notes_listbox.get(i) for i in selected_indices}
            target_files = [f for f in all_files if f.name in target_names]

        threading.Thread(
            target=self._dynamic_linking_worker, 
            args=(list(self.active_keywords), target_files), 
            daemon=True
        ).start()

    def _dynamic_linking_worker(self, glossary, target_files):
        print(f"\n--- Initializing C++ Engine with {len(glossary)} Dynamic Keywords ---")
        try:
            cpp_linker.initialize_search_tree(glossary)
        except Exception as e:
            print(f"[ERROR] Failed to initialize C++ search tree: {e}")
            return

        updated_count = 0
        for file_path in target_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    original_text = f.read()

                linked_text = cpp_linker.inject_obsidian_links(original_text)

                if original_text != linked_text:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(linked_text)
                    print(f"[SUCCESS] Linked keywords in: {file_path.name}")
                    updated_count += 1
                else:
                    print(f"[INFO] No matches in: {file_path.name}")
            except Exception as e:
                print(f"[ERROR] Failed processing {file_path.name}: {e}")

        print(f"\n[DONE] Finished dynamic linking. Updated {updated_count}/{len(target_files)} notes.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ObsidianPipeGUI(root)
    root.mainloop()