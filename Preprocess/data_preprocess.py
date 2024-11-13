import re
import json
import os
from tqdm import tqdm
import pdfplumber # 用於從PDF文件中提取文字的工具
import tabula # 用於finance的報表資料

# 載入參考資料，返回一個字典，key為檔案名稱，value為PDF檔內容的文本
def load_data(source_path, category):
  masked_file_ls = os.listdir(source_path)  # 獲取資料夾中的檔案列表
  corpus_dict = {int(file.replace('.pdf', '')): read_pdf(os.path.join(source_path, file), category) for file in tqdm(masked_file_ls)}  # 讀取每個PDF文件的文本，並以檔案名作為鍵，文本內容作為值存入字典
  return corpus_dict

# 將使用tabula得到的表格，以[column name] [row name] [table value]的格式轉換成字串
def table_to_string(page):
  table_str = ''
  page = page.values
  for i in range(1, len(page)): # 迴圈遍歷表格每一列
    for j in range(1, len(page[0])): # 迴圈遍歷表格每一欄
      table_str += f'{page[0][j]} {page[i][0]} {page[i][j]} '
  return table_str

# 讀取單個PDF文件並返回其文本內容
def read_pdf(pdf_loc, category, page_infos: list = None):
  pdf = pdfplumber.open(pdf_loc)  # 打開指定的PDF文件

  # 如果指定了頁面範圍，則只提取該範圍的頁面，否則提取所有頁面
  pages = pdf.pages[page_infos[0]:page_infos[1]] if page_infos else pdf.pages
  pdf_text = ''
  for _, page in enumerate(pages):  # 迴圈遍歷每一頁
    text = page.extract_text()  # 提取頁面的文本內容
    if text:
      pdf_text += text
  pdf.close()  # 關閉PDF文件

  # 如果讀的是finance的PDF，則多加入使用tabula處理得到的字串
  if category == 'finance':
    pages = tabula.read_pdf(pdf_loc, pages = 'all', multiple_tables = True) # 讀取所有頁面
    pdf_table = ''
    for _, page in enumerate(pages): # 迴圈遍歷每一頁
      pdf_table += table_to_string(page)
      
    pdf_text += pdf_table # 將使用pdfplumber處理得到的字串和使用tabula處理得到的字串合併

    return pdf_text  # 返回萃取出的文本

if __name__ == '__main__':
  source_path = 'reference'
  
  source_path_insurance = os.path.join(source_path, 'insurance')  # 設定參考資料路徑
  corpus_dict_insurance = load_data(source_path_insurance, 'insurance')
  # 將corpus_dict_insurance結果存為insurance.json，可供重複使用
  with open('insurance.json', 'w', encoding='utf-8') as file:
    json.dump(corpus_dict_insurance, file, ensure_ascii = False, indent = 4)
        
  source_path_finance = os.path.join(source_path, 'finance')  # 設定參考資料路徑
  corpus_dict_finance = load_data(source_path_finance, 'finance')
  # 將corpus_dict_finance結果存為finance.json，可供重複使用
  with open('finance.json', 'w', encoding='utf-8') as file:
    json.dump(corpus_dict_finance, file, ensure_ascii = False, indent = 4)
