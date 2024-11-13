# Directory Structure
    ```
.  
│── Preprocess  
│     ├── data_preprocess.py  
│     ├── OCR.py  
│     └── README.md  
│── Model  
│     ├── retrieval.py  
│     └── README.md  
│── requirements.txt  
│── README.md  
    ```

# File Description
* `data_preprocess.py`: 讀取insurance和finance參考資料，整理成字串，並輸出`insurance.json`和`finance.json`，以便重複使用。
* `OCR.py`: 讀取finance中需要透過OCR讀取圖像文字的參考資料，整理成字串，並輸出成`problematic_pdfs.json`，以便重複使用。
* `retrieval.py`: 讀取`data_preprocess.py`和`OCR.py`輸出的json檔，使用reranker模型，透過比對問題和文件的相似度，決定最終問題的答案。

# Google Colab
You can also run the model on the colab.  
https://drive.google.com/file/d/1dKg6J5sti1mZQWVl0p6mbBrhmdW_fVZS/view?usp=drive_link  
For running the code on the colab, all the files you need can be found here.  
https://drive.google.com/drive/folders/1ldJFFT3itTTQI7BkrjkGFdvocAR-92qm?usp=drive_link  
