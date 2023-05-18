'''
Merge parquet files according to the pmcid of train/test
(used to train extractive summarizer)
'''

import os
import pandas as pd


def read_pmcids(path):
    file = open(path)
    pmcids = [line.rstrip('\n') for line in file]
    file.close()
    return pmcids

def read_df(path):
    df = pd.read_parquet(path)
    return df

def main(rf, rd, od, fileName):
    pmcids = read_pmcids(rf)
    result = []
    for i in pmcids:
        df = read_df("%s%s.parquet"%(rd,i))
        result.append(df)
    result = pd.concat(result, axis=0, ignore_index=True)
    result.to_parquet('%s%s.parquet'%(od, fileName))
    print(result.info())



if __name__ == "__main__":
    
    input_file = 'dataset/pmcids/train.txt' # or test.txt
    input_dir = 'dataset/sentence_features/'
    output_dir = 'dataset/to_extractive/'
    file_name = 'train'
    
    # main(input_file, input_dir, output_dir, file_name)

