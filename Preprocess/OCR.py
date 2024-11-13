import re
import json
import os
from tqdm import tqdm
import fitz
from PIL import Image
import pytesseract

def read_pdf_with_ocr(pdf_path):
  pdf_text = ""
  pdf_doc = fitz.open(pdf_path)
    
  for page_num in range(pdf_doc.page_count):
    page = pdf_doc.load_page(page_num)
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img, lang='chi_tra')
    pdf_text += text
    
  pdf_doc.close()
  return pdf_text

if __name__ == '__main__':
  source_path = 'reference'
  tesseract_cmd = r'C:/Program Files (x86)/Tesseract-OCR/tesseract'
  pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
  
  problematic_path = os.path.join(source_path, 'problematic_pdfs')
  masked_file_ls = os.listdir(problematic_path)
  corpus_problematic_dict = {int(file.replace('.pdf', '')): read_pdf_with_ocr(os.path.join(problematic_path, file)) for file in tqdm(masked_file_ls)}
  with open("problematic_pdfs.json", "w", encoding = "utf-8") as file:
    json.dump(corpus_problematic_dict, file, ensure_ascii = False, indent = 4)
