# 摘要結構表
abstr_structure = {'I':['introduction','background','backgrounds','objective','objectives','purpose','purposes'],
                   'M':['method','methods'],
                   'R':['result','results'],
                   'D':['conclusion','conclusions','discussion','discussions']
                   }

# 正文結構表
body_structure = {'I':['intro'],
                  'M':['methods'],
                  'R':['results'],
                  'D':['discuss','concl']
                  }

# 結構轉換
def structure_mapping(text, structure):
    for key, val in structure.items():      
        if text.strip().replace(':','').lower() in val:
            return key
    return 'None'

# 條件 - 非重複有序項目 -> IMRD
def cond(s):
    s = list(dict.fromkeys(s))
    if s == ['I', 'M', 'R', 'D']:
        return True
    else:
        return False

# 檢查是否_結構化寫作
def check_structure(p):
    s1 = [i.find('text').text for i in p if (i.find('infon[@key="section_type"]').text=='ABSTRACT') and (i.find('infon[@key="type"]').text=='abstract_title_1')]
    s1 = [structure_mapping(i, abstr_structure) for i in s1 ]
    if not cond(s1):
        return False
    s2 = [i.find('infon[@key="section_type"]').text for i in p if (i.find('infon[@key="section_type"]').text in ['INTRO', 'METHODS', 'RESULTS', 'DISCUSS', 'CONCL'])]
    s2 = [structure_mapping(i, body_structure) for i in s2]
    if not cond(s2):
        return False
    return True
