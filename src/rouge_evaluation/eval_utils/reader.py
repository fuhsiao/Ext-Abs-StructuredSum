import json


# get train/test - pmcids
def read_pmcids(path):
    file = open(path)
    pmcids = [line.rstrip('\n') for line in file]
    file.close()
    return pmcids

# get paper's sentJson 
def sent_json(path):
    with open(path) as f:
        sentJson = json.load(f)
    return sentJson

# Convert sentence objects
def convert_sentence_obj(sents, section='IMRD', label=False):
    '''
    Args:
        sents(list of dict): sentJson['abstract'] or sentJson['body']
        label(bool): retrieve the body of the sentence marked with True
    Returns:
        res(list of dict): list of sentences dict
    '''
    res = [{'section': key,
            'text': sent['text'].strip()} 
            for key in section for sent in sents[key] if not label or sent['label']==1]
    return res

# Take the first three sentences from each section 
def convert_lead_sentence_obj(sents, section='IMRD'):
    '''
    Args:
        sents(list of dict): sentJson['body']
    Returns:
        res(list of dict): list of sentences dict
    '''
    res = [{'section': key,
            'text': sent['text'].strip()}
            for key in section for sent in sents[key] if sent['pos'] <=3]
    return res
