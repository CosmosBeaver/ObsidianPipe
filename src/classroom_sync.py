import os
import io
import sys
import json
from pathlib import Path

# Bypass the strict scope checking:
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent

def authenticate_google():
    """Handles OAuth 2.0 authentication."""
    creds = None
    base_dir = get_project_root()
    token_path = base_dir / "token.json"
    credentials_path = base_dir / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                print(f"CRITICAL: {credentials_path.name} not found in root!")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_input_directory() -> Path:
    """Reads config.json to find the input directory."""
    config_path = get_project_root() / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
        
    input_dir = Path(settings.get("input_directory", "data/input"))
    if not input_dir.is_absolute():
        input_dir = get_project_root() / input_dir
    input_dir.mkdir(parents=True, exist_ok=True)
    return input_dir

def download_file(drive_service, file_id, file_name, save_dir):
    """Downloads a single file from Google Drive."""
    request = drive_service.files().get_media(fileId=file_id)
    file_path = save_dir / file_name
    
    print(f"Downloading {file_name}...")
    fh = io.FileIO(file_path, mode='wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    print(f"Saved to {file_path}")

def interactive_sync():
    """Main CLI menu to select classes and download materials."""
    creds = authenticate_google()
    classroom_service = build('classroom', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    print("\nFetching active courses...")
    results = classroom_service.courses().list(courseStates=['ACTIVE']).execute()
    courses = results.get('courses', [])

    if not courses:
        print("No active courses found.")
        return

    # --- MAIN APPLICATION LOOP ---
    while True:
        # 1. Select a Class
        print("\n==============================")
        print("      AVAILABLE CLASSES       ")
        print("==============================")
        for i, course in enumerate(courses):
            print(f"[{i}] {course.get('name')}")
            
        selected_course = None
        while True:
            user_input = input("\nEnter class number, 'back', or 'exit': ").strip().lower()
            
            if user_input == 'exit':
                print("Exiting Classroom Sync. Goodbye!")
                return
            if user_input == 'back':
                print("[i] You are already at the main menu.")
                continue

            try:
                course_idx = int(user_input)
                if 0 <= course_idx < len(courses):
                    selected_course = courses[course_idx]
                    course_id = selected_course['id']
                    break
                else:
                    print(f"[!] Invalid selection. Please enter a number between 0 and {len(courses) - 1}.")
            except ValueError:
                print("[!] Invalid input. Please enter a valid number, 'back', or 'exit'.")

        # 2. Fetch Materials for that Class
        print(f"\nFetching materials for '{selected_course.get('name')}'...")
        materials_results = classroom_service.courses().courseWorkMaterials().list(courseId=course_id).execute()
        materials = materials_results.get('courseWorkMaterial', [])
        
        downloadable_files = []
        for item in materials:
            for material in item.get('materials', []):
                if 'driveFile' in material:
                    drive_file = material['driveFile']['driveFile']
                    downloadable_files.append({
                        'id': drive_file['id'],
                        'title': drive_file['title']
                    })

        if not downloadable_files:
            print("\n[i] No Drive materials found for this class.")
            input("Press Enter to return to the class list...")
            continue  # Skips the rest of the loop and goes back to AVAILABLE CLASSES

        # 3. Select Files to Download
        print(f"\n--- Materials for {selected_course.get('name')} ---")
        for i, f in enumerate(downloadable_files):
            print(f"[{i}] {f['title']}")

        go_back_to_main = False
        to_download = []

        while True:
            selection = input("\nEnter file numbers (e.g., 0, 2), 'all', 'back', or 'exit': ").strip().lower()
            
            if selection == 'exit':
                print("Exiting Classroom Sync. Goodbye!")
                return
            if selection == 'back':
                go_back_to_main = True
                break
                
            if selection == 'all':
                to_download = downloadable_files
                break
                
            raw_indices = selection.split(',')
            valid = True
            indices = []
            
            for x in raw_indices:
                x = x.strip()
                if not x:
                    continue 
                    
                if x.isdigit():
                    idx = int(x)
                    if 0 <= idx < len(downloadable_files):
                        indices.append(idx)
                    else:
                        print(f"[!] Index {idx} is out of bounds. Try again.")
                        valid = False
                        break
                else:
                    print(f"[!] '{x}' is not a valid number. Try again.")
                    valid = False
                    break
                    
            if valid and indices:
                unique_indices = list(set(indices))
                to_download = [downloadable_files[i] for i in unique_indices]
                break
            elif valid and not indices:
                print("[!] You didn't enter any numbers. Please try again.")

        if go_back_to_main:
            continue  # Skips download process, goes back to AVAILABLE CLASSES

        # 4. Download them to the config directory
        save_dir = get_input_directory()
        print(f"\nSaving files to: {save_dir}")
        
        for f in to_download:
            try:
                download_file(drive_service, f['id'], f['title'], save_dir)
            except Exception as e:
                print(f"Failed to download {f['title']}: {e}")
                
        print("\n[SUCCESS] Downloads complete!")
        input("Press Enter to return to the class list...")

if __name__ == '__main__':
    interactive_sync()