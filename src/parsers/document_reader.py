import os
import json
import textwrap
import multiprocessing
import pdfplumber
from functools import partial
from docx import Document
from tabulate import tabulate
from PIL import Image
import pytesseract
from pytesseract import Output
from langdetect import detect
from datetime import datetime
import subprocess
import mimetypes
import logging
import cv2
import numpy as np
logging.getLogger("pdfminer").setLevel(logging.ERROR)


pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def process_file(func, path):  # Pre-binding self to the handler
    result = func(path)
    return (path, result)

class Reader:
    def __init__(self, folder_path, attachment_dir=None):
        self.folder = folder_path
        self.attachment_dir = attachment_dir
        
        # Ensure attachment directory exists if provided
        if self.attachment_dir:
            os.makedirs(self.attachment_dir, exist_ok=True)
        

    def readtxt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read().split("\n")  # Store lines as a list
            return {"file": file_path, "text": content}
        except Exception as x:
            return {"file": file_path, "error": str(x)}

    def readocx(self, file_path):
        try:
            document = Document(file_path)

            # Wrap paragraphs into lines of 12 words using textwrap
            formatted_text = []
            for para in document.paragraphs:
                cleaned_text = para.text.strip()
                if cleaned_text:
                    wrapped_text = textwrap.fill(cleaned_text, width=80)  # Approx. 12 words per line
                    formatted_text.extend(wrapped_text.split("\n"))  # Store wrapped lines separately

            # Format tables properly
            table_contents = []
            for table in document.tables:
                table_data = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                formatted_table = tabulate(table_data, headers="firstrow", tablefmt="grid")
                table_contents.append(formatted_table.split("\n"))  # Ensure multi-line formatting

            links = {rel_id: rel._target for rel_id, rel in document.part.rels.items() if "hyperlink" in rel.reltype}

            return {
                "file": file_path,
                "text": formatted_text,  # Wrapped paragraphs 
                "tables": table_contents,  # Tables formatted 
                "links": list(links.values())
            }
        except Exception as x:
            return {"file": file_path, "error": str(x)}

    def readpho(self, file_path):
        try:
            img = Image.open(file_path).convert("L")
            
            np_img = np.array(img).astype('uint8')
            
            # binarize the image
            _, thresh = cv2.threshold(np_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            processed_img = cv2.medianBlur(thresh, 3)
            
            custom_config = r'--oem 3 --psm 6'  
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            if detect(text) == "en":
                text = pytesseract.image_to_string(processed_img, config=custom_config, lang="eng")

            ocr_data = pytesseract.image_to_data(processed_img, config=custom_config, output_type=Output.DICT)
            table_rows = []
            for i in range(len(ocr_data["text"])):
                if ocr_data["text"][i].strip():  
                    row = [
                        ocr_data["left"][i],   
                        ocr_data["top"][i],    
                        ocr_data["width"][i],  
                        ocr_data["height"][i], 
                        ocr_data["text"][i],   # Detected Text
                    ]
                    table_rows.append(row)
            
            headers = ["X Position", "Y Position", "Width", "Height", "Text"]
            table_str = tabulate(table_rows, headers=headers, tablefmt="grid")

            return {
                "file": file_path,
                "text": text.split("\n"),
                "tables": table_str
            }

        except Exception as e:
            return {"file": file_path, "error": str(e)}
    
    def is_math_formula(self, text):
        # Common mathematical and Greek symbols found in formulas
        math_symbols = set("∑∫√±≈≠≡≤≥∈∉⊂⊆∪∩∞αβγδεζηθικλμνξοπρστυφχψωΔΓΘΛΞΠΣΦΨΩ∇∂")
        
        # If it contains advanced math symbols, it's almost certainly an equation
        if any(char in math_symbols for char in text):
            return True
            
        # If it has an equals sign and multiple operators, treat it as an equation
        if '=' in text and sum(1 for char in text if char in "+-*/^=") >= 2:
            return True
        return False
    
    def readpdf(self, file_path):
        try:
            all_text = []
            file_title = os.path.basename(file_path).replace(".pdf", "")
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    all_text.append(f"\n## Page {page_num+1}\n")
                    
                    # 1. Read line-by-line to get exact coordinates
                    lines = page.extract_text_lines()
                    
                    if lines:
                        # IT IS A NATIVE PDF
                        for line in lines:
                            text = line["text"]
                            
                            # Check if the line is a formula!
                            if self.is_math_formula(text):
                                # Define the bounding box (adding a 5px padding so we don't cut off tall symbols)
                                pad = 5
                                bbox = (
                                    max(0, line["x0"] - pad), 
                                    max(0, line["top"] - pad), 
                                    min(page.width, line["x1"] + pad), 
                                    min(page.height, line["bottom"] + pad)
                                )
                                
                                try:
                                    # Crop just the formula and save it!
                                    cropped_page = page.within_bbox(bbox)
                                    image_obj = cropped_page.to_image(resolution=300).original
                                    
                                    if getattr(self, 'attachment_dir', None):
                                        img_filename = f"{file_title}_p{page_num+1}_math_{int(line['top'])}.png"
                                        img_path = os.path.join(self.attachment_dir, img_filename)
                                        image_obj.save(img_path)
                                        
                                        # Inject the picture into Markdown instead of the raw text
                                        all_text.append(f"\n![[{img_filename}]]\n")
                                except Exception as e:
                                    # If cropping fails, fallback to the raw text
                                    all_text.append(text)
                            else:
                                # It's normal text, just append it
                                all_text.append(text)
                        
                        # check for embedded image graphs like before
                        for img_idx, img in enumerate(page.images):
                            try:
                                bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                                img_obj = page.within_bbox(bbox).to_image(resolution=300).original
                                if getattr(self, 'attachment_dir', None):
                                    img_name = f"{file_title}_p{page_num+1}_graph_{img_idx}.png"
                                    img_obj.save(os.path.join(self.attachment_dir, img_name))
                                    all_text.append(f"\n![[{img_name}]]\n")
                            except Exception:
                                continue

                    else:
                        # IT IS A SCANNED PDF (No native text lines found)
                        im = page.to_image(resolution=300).original
                        temp_path = f"temp_{file_title}_page_{page_num+1}.png"
                        im.save(temp_path)

                        # Run standard OCR for the text
                        ocr_result = self.readpho(temp_path)
                        all_text.extend(ocr_result.get("text", ["OCR error"]))

                        # Keep the whole scanned page image as a fallback for the math
                        if getattr(self, 'attachment_dir', None):
                            img_filename = f"{file_title}_scanned_p{page_num+1}.png"
                            obsidian_img_path = os.path.join(self.attachment_dir, img_filename)
                            os.rename(temp_path, obsidian_img_path) 
                            all_text.append(f"\n![[{img_filename}]]\n")
                        else:
                            os.remove(temp_path)

                    # 3. Extract Tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            formatted_table = tabulate(table, headers="firstrow", tablefmt="grid")
                            all_text.append(f"\n{formatted_table}\n")

            return {
                "file": file_path,
                "title": file_title,
                "text": "\n".join(all_text)
            }

        except Exception as e:
            return {"file": file_path, "error": str(e)}
        
    def readdoc(self, file_path):
        try:
            # Convert .doc to .docx using antiword
            docx_path = file_path + "x"

            if not os.path.exists(docx_path):
                result = subprocess.run(['antiword', file_path], capture_output=True, text=True)
                text = result.stdout

                doc = Document()
                doc.add_paragraph(f"Note: {file_path} is a legacy .doc file. Only text was extracted.\n")
                doc.add_paragraph(text)
                doc.save(docx_path)

            extracted_content = self.readocx(docx_path)
            os.remove(docx_path)
            return extracted_content

        except Exception as e:
            return {"file": file_path, "error": str(e)}


    def scanner(self, folder,use_multiprocessing=True):  # Scan for files
        file_entries, sub_dirs, tasks = [], [], []
        results = []
        processed_files = set()

        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.is_file() and entry.path not in processed_files:
                    file_entries.append(entry.path)
                    processed_files.add(entry.path)
                elif entry.is_dir():
                    sub_dirs.append(entry.path)  # Separate files from directories

        for file_path in file_entries:
            _, extension = os.path.splitext(file_path)
            handler = file_handlers.get(extension.lower())

            if handler:
                bound_func = partial(handler, self)
                tasks.append((bound_func, file_path))  # Assign appropriate processing function

        try:
            if use_multiprocessing and tasks:
                with multiprocessing.Pool(processes=os.cpu_count()) as pool:
                    results = pool.starmap(process_file, tasks)
            else:
                for task in tasks:
                    results.append(process_file(*task))
        except Exception as e:
            results.append({"error": f"Multiprocessing error: {e}"})

        for sub_dir in sub_dirs:  # Recursively scan subdirectories
            results += self.scanner(sub_dir,use_multiprocessing=use_multiprocessing)

        return results

file_handlers = {
    ".txt": Reader.readtxt,
    ".docx": Reader.readocx,
    ".png": Reader.readpho,
    ".jpeg": Reader.readpho,
    ".jpg": Reader.readpho,
    ".webp": Reader.readpho,
    ".bmp": Reader.readpho,
    ".pdf":Reader.readpdf,
    ".doc":Reader.readdoc,
}  


#    [os.remove(e.path) for e in os.scandir(folder_path)]
#    file remover

            