import re
import json
import os
from tqdm import tqdm
import fitz # 用於提取PDF裡的圖像
from PIL import Image
import pytesseract # 用於讀取圖像裡的文字

def read_pdf_with_ocr(pdf_path):
  pdf_text = ""
  pdf_doc = fitz.open(pdf_path)
    
  for page_num in range(pdf_doc.page_count): # 迴圈遍歷每一頁
    page = pdf_doc.load_page(page_num)
    pix = page.get_pixmap(dpi = 300) # 將頁面轉為位圖（pixmap）格式，並設定解析度
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples) # 將位圖的數據轉換為PIL的Image物件
    text = pytesseract.image_to_string(img, lang = 'chi_tra') # 使用pytesseract對圖像進行OCR辨識
    pdf_text += text
    
  pdf_doc.close()
  return pdf_text

if __name__ == '__main__':
  source_path = 'reference'
  tesseract_cmd = r'C:/Program Files (x86)/Tesseract-OCR/tesseract' # 將tesseract_cmd路徑改為tesseract安裝路徑
  pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
  
  problematic_path = os.path.join(source_path, 'problematic_pdfs')  # 設定參考資料路徑
  corpus_dict_problematic = {int(file.replace('.pdf', '')): read_pdf_with_ocr(os.path.join(problematic_path, file)) for file in tqdm(os.listdir(problematic_path))}
  # 將corpus_dict_problematic結果存為problematic_pdfs.json，可供重複使用
  with open("problematic_pdfs.json", "w", encoding = "utf-8") as file:
    json.dump(corpus_dict_problematic, file, ensure_ascii = False, indent = 4)
