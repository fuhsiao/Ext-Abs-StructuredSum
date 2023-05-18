from urllib.request import urlopen
from urllib.error import HTTPError
from xml.etree.ElementTree import fromstring
from check_cond import check_structure, structure_mapping, body_structure
import os


# PMCID list
def read_pmcids(path):
    file = open(path)
    pmc_ids = [line.rstrip('\n') for line in file]
    file.close()
    return pmc_ids

# API(PMCID)
def Bioc_API(Id):
    try:
        data = urlopen('https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/%s/ascii'%(Id))
    except HTTPError as e:
        print(Id, 'HTTPError: {}'.format(e.code))
        return False
    else:
        return data.read()

#
def main(rf, od):    
    
    if not os.path.exists(od):      
        os.makedirs(od)
    
    pmcids = read_pmcids(rf)
    for i in pmcids:
        data = Bioc_API(i)
        if not data:
            continue
        root = fromstring(data)
        p = root.findall('.//passage')
        if not check_structure(p):                  # 檢查是否_結構化寫作
            continue
        with open(od + i + '.xml', 'wb') as f:      # 儲存符合條件_XML
            f.write(data)


if __name__ == '__main__':
    
    pmcids_list = 'dataset/pmcids/all.txt'
    output_dir = 'dataset/raw_data/xml/'

    # main(pmcids_list, output_dir)
