import pickle
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# extractive summarizer
def load_ExtModel(path):
    return pickle.load(open(path, 'rb'))

# abstractive summarizer
def load_AbstrModel(path):
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(path, trust_remote_code=True, pass_global_tokens_to_decoder=True)
    return tokenizer, model
