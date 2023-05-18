'''
Read sentence json
extract syntactic and semantic features for each sentence
and export it as a parquet file
'''

from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import torch
import spacy
import json
import re
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn.feature_extraction.text')


nlp = spacy.load("en_core_sci_sm")

def get_file(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

# PMC article (sentence json) 
def sent_json(path):
    with open(path) as f:
        sentJson = json.load(f)
    return sentJson

# 句子列表
def sent_lst(sents):
    return [sent['text'] for sent in sents]

# 移除停用詞及標點
def clean_token(doc):
    return [token for token in doc if not (token.is_stop or token.is_punct)]

# 段落之總句數
def add_num_sents_para(sents):
    reset = True
    for index, sent in reversed(list(enumerate(sents))):    
        if reset: ptr = sent['pos_para']
        reset = True if sent['pos_para'] == 1 else False
        sents[index]['ns_para'] = ptr
    return sents

# 位置重要性
def position_imp(cur, ns):
    imp = 1 if cur == 1 else (ns-cur)/ns
    return imp

# 標題詞列表
def title_wlst(txt):
    doc = nlp(txt)
    wlst = [token.text.lower() for token in clean_token(doc)]
    return list(set(wlst))

# 句子之標題詞數量
def title_word_count(doc, wlst):
    titleLen = len(wlst)
    score = 0 if titleLen == 0 else len([token for token in doc if token.text.lower() in wlst])/titleLen
    return score

# 標記詞性之數量
def pos_token(doc, pos_type):
    return len([token for token in doc if token.pos_ == pos_type])

# 自定分詞器
def custom_toknizer(txt):
    doc = nlp(txt)
    words = [token.lemma_.lower() for token in doc if not (token.is_stop or token.is_punct or token.is_digit)]
    return words

# 詞頻-逆向句子頻率 
def Tfisf(lst):
    tf = TfidfVectorizer(tokenizer=custom_toknizer, lowercase=False)
    tfisf_matrix = tf.fit_transform(lst)
    word_count = (tfisf_matrix!=0).sum(1)
    with np.errstate(divide='ignore', invalid='ignore'):
        mean_score = np.where(word_count == 0, 0, np.divide(tfisf_matrix.sum(1), word_count)).flatten()
    return mean_score

# 餘弦相似度
def similarity(lst, ptm):
    model = SentenceTransformer(ptm)
    embeddings = model.encode(lst, convert_to_tensor=True)
    cosine = util.cos_sim(embeddings, embeddings)
    cosine = cosine.sum(1)-1
    cosine = torch.divide(cosine, torch.max(cosine)).numpy() # .cpu().numpy()
    return cosine

# 特徵萃取
def feature_extraction(title, section, sents): 
    lst = sent_lst(sents)
    tfisf = Tfisf(lst)
    cosine = [similarity(lst, "sentence-transformers/all-MiniLM-L6-v2"),
              similarity(lst, "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"),
              similarity(lst, "pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb")
              ]
    # Number of sentences
    ns = len(sents)
    sents = add_num_sents_para(sents)
    # Extracting the features of each sentences
    arr = np.empty((0,12))
    for index, sent in enumerate(sents):
        doc = nlp(sent["text"])
        doc = clean_token(doc)
         
        label = sent["label"]
        F1 = len(doc)                                           # Sentence Length (undone) -> len / longest sentence len
        F2 = position_imp(sent["pos"], ns)                      # Sentence Position
        F3 = position_imp(sent["pos_para"], sent["ns_para"])    # Sentence Position (in paragraph)
        F4 = title_word_count(doc, title)                       # Title Word
        F5 = 0 if F1 == 0 else pos_token(doc, "PROPN")/F1       # Proper Noun
        F6 = 0 if F1 == 0 else pos_token(doc, "NUM")/F1         # Numerical Token
        F7 = tfisf[index]                                       # Term Frequency-Inverse Sentence Frequency
        F8, F9, F10 = [x[index] for x in cosine]                # Cosine Similarity

        feat = np.array([[section, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, label]])
        arr = np.append(arr, feat, axis=0)
    # F1 (cont.)
    maxLen = np.amax(arr[:,1])
    arr[:,1] = arr[:,1]/maxLen 
    return arr
    
# 文章 IMRD - 句子特徵
def feature_from_imrd(body, title):
    paper = np.empty((0,12))
    for index, key in enumerate(['I', 'M', 'R', 'D'], start = 1):
        paper = np.append(paper, feature_extraction(title, index, body[key]), axis = 0)
    df = pd.DataFrame(paper, columns = ['section','F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'label'])
    return set_dtypes(df)

# 設置欄位類型
def set_dtypes(df):
    df = df.astype({'section': 'int8', 'label': 'bool',
                    'F1': 'float32', 'F2': 'float32', 'F3': 'float32', 'F4': 'float32', 'F5': 'float32',
                    'F6': 'float32', 'F7': 'float32', 'F8': 'float32', 'F9': 'float32', 'F10': 'float32'})
    return df

#
def main(rd, od):
    
    if not os.path.exists(od):      
        os.makedirs(od)

    for file in get_file(rd):
        pmcid = file.split('.')[0]
        sentJson = sent_json('%s%s'%(rd, file))
        title = title_wlst(sentJson['title'])
        body = sentJson['body']
        result = feature_from_imrd(body, title)
        result.to_parquet('%s%s.parquet'%(od, pmcid))



if __name__ == '__main__':
    
    input_dir = 'dataset/sentence_json/'
    output_dir = 'dataset/sentence_features/'
    
    # main(input_dir, output_dir)
