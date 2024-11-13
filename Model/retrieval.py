import re
import json
import os
from tqdm import tqdm
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

if __name__ == '__main__':
    with open("dataset/preliminary/questions_preliminary.json", "rb") as f:
        qs_ref = json.load(f)
    
    with open("dataset/preliminary/ground_truths_example.json", "rb") as f:
        ground_truths = json.load(f)
    
    with open("insurance.json", "r", encoding = "utf-8") as f:
        corpus_dict_insurance = json.load(f)
    corpus_dict_insurance = {int(key): value for key, value in corpus_dict_insurance.items()}
    
    with open("finance.json", "r", encoding = "utf-8") as f:
        corpus_dict_finance = json.load(f)
    corpus_dict_finance = {int(key): value for key, value in corpus_dict_finance.items()}
    
    with open("problematic_pdfs.json", "r", encoding = "utf-8") as f:
        problematic_pdfs = json.load(f)
    problematic_pdfs = {int(key): value for key, value in problematic_pdfs.items()}
    
    corpus_dict_finance.update(problematic_pdfs)
    
    with open("reference/faq/pid_map_content.json", "rb") as f:
        key_to_source_dict = json.load(f)
        key_to_source_dict = {int(key): value for key, value in key_to_source_dict.items()}
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')
    model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3').to(device)
    model.eval()
    
    max_length = 512
    answer_dict = {'answers': []}
    
    for q_dict in qs_ref['questions']:
        query = q_dict['query']
    
        if q_dict['category'] == 'insurance':
            corpus_dict = [corpus_dict_insurance[int(f)] for f in q_dict['source']]
        elif q_dict['category'] == 'finance':
            corpus_dict = [corpus_dict_finance[int(f)] for f in q_dict['source']]
        elif q_dict['category'] == 'faq':
            corpus_dict_faq = {key: str(value) for key, value in key_to_source_dict.items() if key in q_dict['source']}
            corpus_dict = [corpus_dict_faq[int(f)] for f in q_dict['source']]
    
        with torch.no_grad():
            maximum = -float('inf')
            retrieved_doc = None
    
            for idx, doc in zip(q_dict['source'], corpus_dict):
                doc_segments = [doc[i:i + max_length] for i in range(0, len(doc), max_length)]
    
                for segment in doc_segments:
                    pairs = [[query, segment]]
    
                    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=max_length).to(device)
                    similarity = model(**inputs, return_dict=True).logits.view(-1).item()
    
                    if similarity > maximum:
                        maximum = similarity
                        retrieved_doc = idx
    
            answer_dict['answers'].append({"qid": q_dict['qid'], "retrieve": retrieved_doc})
            print('%d %d' % (q_dict['qid'], retrieved_doc))
    
    with open("dataset/preliminary/pred_retrieve.json", 'w', encoding='utf8') as f:
      json.dump(answer_dict, f, ensure_ascii=False, indent=4)