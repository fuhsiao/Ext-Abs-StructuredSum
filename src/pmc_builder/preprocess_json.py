'''
Convert article json to sentence unit json
Add the following attributes to the sentences of each section
(1) sentence position (2) position in paragraph (3) abstract sentence label
'''

import spacy
import json
import re
import os
import extoracle


nlp = spacy.load("en_core_sci_sm")

def get_file(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

# PMC article (json)
def raw_json(path):
    with open(path) as f:
        rawJson = json.load(f)
    return rawJson

# 移除_非必要括弧
def rm_parenthese_with_useless_token(text):
    return re.sub(r'\s*\(\s*(?:table|fig|http|www)[^()]*\)', '', text, flags = re.I)  # re.I 不區分大小寫

# 斷句
def sents_segment(p, pos_para = False):
    sents = []
    sents_break = [".", "?", "!"]
    start = para_i = pre_para_i =  0
    conn = False
    for i in p:
        i = rm_parenthese_with_useless_token(i).strip() # 避免末端空白判斷為 token 而無法 sents_break
        doc = nlp(i)
        for sent in doc.sents:
            if any(t in sents_break for t in sent[-1].text): # 部分句尾詞如 3h. 無法分詞, 因此包含 sents_break 即可  
                para_i +=1          
                text = "".join(t.text_with_ws for t in doc[start:sent.end])                         # 原始字串
                tokenize_text = " ".join(t.text for t in doc[start:sent.end])                       # 分詞字串
                sentence = {"text":text, "tokenize_text":tokenize_text, "pos":pre_para_i+para_i}    # 建立句子物件
                if pos_para: sentence['pos_para'] = para_i                                          # pos 句子位置, pos_para 句子於每段位置
                sents.append(sentence)
                start = sent.end
                conn = False
            else:      
                start = start if conn else sent.start   # sent.end 非斷句字符 紀錄此句 start, 直到斷句前不更改 start 位置
                conn = True
        pre_para_i += para_i
        start = para_i =  0
    return sents


section = ['I','M','R','D']

# 轉換至 sentence json
def sent2Json(paper):
    title = paper['title']
    sentJson = {'title':title, 'abstract':{}, 'body':{}}
    for i in section:
        sentJson['abstract'][i] = sents_segment(paper['abstract'][i])
        sentJson['body'][i] = sents_segment(paper['body'][i], True)
    return sentJson

# 分詞之句子 - input as ext-oracle(source & target)
def sentences_token(sentJson):
    src, tgt = {}, {}
    for i in section:
        src[i] = [sent['tokenize_text'] for sent in sentJson['body'][i]]
        tgt[i] = [sent['tokenize_text'] for sent in sentJson['abstract'][i]]
    return src, tgt

# 異常排除 - IMRD null 
def exception_detect(sentJson):
    result = [len(sentJson[i][j]) for i in ['abstract','body'] for j in section]
    if 0 in result: return True
    return False

#
def main(rd, od, label = False):
    
    if not os.path.exists(od):      
        os.makedirs(od)

    # 摘要句標籤
    def add_label(i):
        for j, sent in enumerate(sentJson['body'][i]):
            pos = sent['pos'] - 1
            sentJson['body'][i][j]['label'] = 1 if pos in ext_sentence[i] else 0

    for file in get_file(rd):
        rawJson = raw_json(rd + file)
        sentJson = sent2Json(rawJson)
        # 例外處理
        if exception_detect(sentJson):
            print(rawJson['id'])
            continue
        # 計算 oracle 摘要句標籤
        if label:
            src, tgt = sentences_token(sentJson)
            ext_sentence = extoracle.from_imrd(src, tgt, 'greedy', length_oracle = True)
            for i in section:
                add_label(i)
        
        paper = json.dumps(sentJson)
        with open(od + rawJson['id'] + '.json', 'w') as f:
            f.write(paper)


if __name__ == '__main__':
    
    input_dir = 'dataset/raw_data/json/'
    output_dir = 'dataset/sentence_json/'
    add_label = True
    
    # main(input_dir, output_dir, lable = add_label)
