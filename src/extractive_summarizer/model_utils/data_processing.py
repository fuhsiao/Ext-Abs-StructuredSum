import pandas as pd

# 讀取資料 - 特徵/標籤
def prepare_data(df, tgt, balance=False):
    # remove rows with nan 
    df = df.dropna(axis=0, how='any')
    # balance binaryClass 
    if balance:
        counts = df[tgt].value_counts()
        major = counts.index[0]
        minor = counts.index[1]
        df_major = df[df[tgt] == major].sample(counts.min(), random_state=42)
        df_minor = df[df[tgt] == minor]
        df = pd.concat([df_major, df_minor], axis=0)
    # split feature and label
    df = df.sample(frac=1, random_state=42)
    df = df.reset_index(drop=True)
    # df = df.drop(columns=block) if block else df
    x = df.drop(columns=[tgt])
    y = df[tgt]
    return x, y

# 讀取 訓練/測試集
def get_dataset(train_set, test_set, cols, tgt):
    cols.append(tgt)
    train = pd.read_parquet(train_set, columns=cols)
    test = pd.read_parquet(test_set, columns=cols)
    x_train, y_train = prepare_data(train, tgt, balance=True)
    x_test, y_test = prepare_data(test, tgt)
    return x_train, y_train, x_test, y_test
