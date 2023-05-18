import pandas as pd
from datasets import Dataset

# Dataframe 轉換 Dataset format
def convert_to_Dataset(file):
    df = pd.read_parquet(file)
    dataset = Dataset.from_pandas(df)
    return dataset

# 匯入 train, test - Dataset format
def load_raw_data(train_file, test_file, val_size=0.1):
    train = convert_to_Dataset(train_file)
    test = convert_to_Dataset(test_file)
    raw_data = train.train_test_split(test_size=val_size, seed=42)
    raw_data['validation'] = raw_data.pop('test')
    raw_data['test'] = test
    return raw_data