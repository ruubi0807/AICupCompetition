# File Description
* `data_preprocess.py`: 如果是insurance參考資料，則維持原本的讀取方式得到字串；如果是finance參考資料，則除了使用原本的讀取方式得到字串外，會再額外使用tabula讀取參考資料，將原本的字串與使用tabula得到的字串合併，faq一樣維持原本的讀取方式。  
* `OCR.py`: 讀取finance中需要透過OCR讀取圖像文字的參考資料，整理成字串，並輸出成`problematic_pdfs.json`，以便重複使用。  
安裝OCR所需套件可參考`Reference`內的兩篇文章。  

# Reference
* https://blog.csdn.net/Castlehe/article/details/118751833  
* https://blog.csdn.net/weixin_43508499/article/details/108745574  
