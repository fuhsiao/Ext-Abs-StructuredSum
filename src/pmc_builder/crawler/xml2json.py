from check_cond import abstr_structure, body_structure, structure_mapping
import xml.etree.ElementTree as ET
import json
import os


# XML folder
def get_file(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

# XML root node
def get_root(xml):
    return ET.parse(xml).getroot()

# 標題
def get_title(p):
    title = ''
    for i in p:
        if (i.find("infon[@key='section_type']").text == 'TITLE'):
            title = i.find('text').text
            break
    return title

# 摘要
def get_abstract(p):
    abstract = {'I':[],'M':[],'R':[],'D':[]}
    for i in p:
        if (i.find("infon[@key='section_type']").text == 'ABSTRACT'):
            type = i.find("infon[@key='type']").text
            text = i.find('text').text
            if type == 'abstract_title_1':
                s = structure_mapping(text, abstr_structure)
            elif type == 'abstract':
                abstract[s].append(text)
    return abstract

# 正文
def get_body(p):
    body = {'I':[],'M':[],'R':[],'D':[]}
    start = end = False
    for i in p:
        s = structure_mapping(i.find("infon[@key='section_type']").text, body_structure)

        if (s == 'I') and (not start):               # first "I" part and not start -> set start True
            start = True
        elif (s == 'D') and (not end) and (start):   # first "D" part and not end -> set end True (if not started don't do this)
            end = True
        elif (s not in ['D','None']) and (end):      # after end = True, break if not "D" part or "None" part (e.g. figure)
            break
        
        if (s in ['I','M','R','D']) and (i.find("infon[@key='type']").text == 'paragraph') and start:
            text = i.find('text').text
            body[s].append(text)
    return body

# 轉換_JSON
def Xml2Json(pmcid, p):
    paper = {}
    paper['id'] = pmcid
    paper['title'] = get_title(p)
    paper['abstract'] = get_abstract(p)
    paper['body'] = get_body(p)
    return paper

#
def main(rd, od):
    
    if not os.path.exists(od):      
        os.makedirs(od)

    for file in get_file(rd):
        r = get_root(rd + file)
        p = r.findall('.//passage')
        pmcid = file.split('.')[0]
        paper = Xml2Json(pmcid, p)
        with open(od + pmcid + '.json', 'w') as f:
            f.write(json.dumps(paper))


if __name__ == '__main__':
    
    input_dir = 'dataset/raw_data/xml/'
    output_dir = 'dataset/raw_data/json/'
    
    # main('xml/','json/')
