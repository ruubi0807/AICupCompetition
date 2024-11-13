import re
import json
import os
from tqdm import tqdm
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

if __name__ == '__main__':
    with open("dataset/preliminary/questions_preliminary.json", "rb") as f: # 讀取問題檔案
        qs_ref = json.load(f)
    
    with open("dataset/preliminary/ground_truths_example.json", "rb") as f:
        ground_truths = json.load(f)
    
    with open("insurance.json", "r", encoding = "utf-8") as f: # 讀取從data_preprocess.py得到的insurance參考資料
        corpus_dict_insurance = json.load(f)
    corpus_dict_insurance = {int(key): value for key, value in corpus_dict_insurance.items()}
    
    with open("finance.json", "r", encoding = "utf-8") as f: # 讀取從data_preprocess.py得到的finance參考資料
        corpus_dict_finance = json.load(f)
    corpus_dict_finance = {int(key): value for key, value in corpus_dict_finance.items()}
    
    with open("problematic_pdfs.json", "r", encoding = "utf-8") as f: # 讀取從OCR.py得到的finance參考資料（參考文件內的文字為圖像的PDF）
        problematic_pdfs = json.load(f)
    problematic_pdfs = {int(key): value for key, value in problematic_pdfs.items()}
    
    corpus_dict_finance.update(problematic_pdfs) # 將problematic_pdfs合併到corpus_dict_finance內
    
    with open("reference/faq/pid_map_content.json", "rb") as f:
        key_to_source_dict = json.load(f) # 讀取參考資料文件
        key_to_source_dict = {int(key): value for key, value in key_to_source_dict.items()}
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 使用BAAI/bge-reranker-v2-m3的tokenizer和model
    tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')
    model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3').to(device)
    model.eval()
    
    max_length = 512 # 設置tokenizer的最大長度
    answer_dict = {'answers': []} # 初始化字典
    
    for q_dict in qs_ref['questions']: # 遍歷問題檔案內所有的問題
        query = q_dict['query']
    
        if q_dict['category'] == 'insurance':
            corpus_dict = [corpus_dict_insurance[int(f)] for f in q_dict['source']]
        elif q_dict['category'] == 'finance':
            corpus_dict = [corpus_dict_finance[int(f)] for f in q_dict['source']]
        elif q_dict['category'] == 'faq':
            corpus_dict_faq = {key: str(value) for key, value in key_to_source_dict.items() if key in q_dict['source']}
            corpus_dict = [corpus_dict_faq[int(f)] for f in q_dict['source']]
    
        with torch.no_grad():
            maximum = -float('inf') # 儲存相似度最大的文件段落
            retrieved_doc = None # 儲存與query相似度最大的文件編號
    
            for idx, doc in zip(q_dict['source'], corpus_dict): # 遍歷所有的候選文件
                doc_segments = [doc[i:i + max_length] for i in range(0, len(doc), max_length)] # 將文件依照tokenizer的最大長度分割成好幾個段落
    
                for segment in doc_segments:
                    pairs = [[query, segment]]
    
                    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=max_length).to(device) # 使用tokenizer對問題和文件段落進行編碼
                    similarity = model(**inputs, return_dict=True).logits.view(-1).item() # 獲得問題和文件段落的相似度
    
                    if similarity > maximum: # 紀錄所有文件中和問題相似度最高的文件編號
                        maximum = similarity
                        retrieved_doc = idx
    
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved_doc})
            print('%d %d' % (q_dict['qid'], retrieved_doc))
    
    # 將答案字典保存為json文件
    with open("dataset/preliminary/pred_retrieve.json", 'w', encoding='utf8') as f:
      json.dump(answer_dict, f, ensure_ascii=False, indent=4) # 儲存檔案，確保格式和非ASCII字符
