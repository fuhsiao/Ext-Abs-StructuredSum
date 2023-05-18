'''
Reference Code from:
    https://github.com/pltrdy/extoracle_summarization

    The following code have been modified as required
'''
import multiprocessing
import extoracle.utils


METHODS = {
    "greedy": extoracle.utils.greedy_selection,
    "combination": extoracle.utils.combination_selection,
}


def split_token(segment_sents):
    '''Split sentences into token
    Args:
        segment_sents(list): Tokenized text and sentence broken with ['.', '!', '?']
    Returns:
        sentences(list): list of sentences (= list of list of words)
    '''
    sentences = [[word for word in cur_sent.split()] for cur_sent in segment_sents]
    return sentences


def process_example(example):
    (method,
        src_part,
        tgt_part,
        summary_length,
        length_oracle,
        key,) = example

    src_sentences = split_token(src_part)
    tgt_sentences = split_token(tgt_part)

    if length_oracle:
        summary_length = len(tgt_sentences)

    ids, sents = method(src_sentences, tgt_sentences, summary_length)
    return ids, sents, key


def from_imrd(src, tgt, method, summary_length=None,
               length_oracle=False, n_thread=1):
               
    if method in METHODS:
        method = METHODS[method]
    else:
        raise ValueError("Unknow extoracle method '%s', choices are [%s]"
                         % (method, ", ".join(METHODS.keys())))

    if summary_length is None and not length_oracle:
        raise ValueError(
            "Argument [summary_length, length_oracle] "
            + "cannot be both None/False")
    if summary_length is not None and length_oracle:
        raise ValueError(
            "Arguments [summary_length, length_oracle] are incompatible")

    def example_generator():
        for key in ["I","M","R","D"]:
            src_part, tgt_part = src[key], tgt[key]
            example = (
                method,
                src_part,
                tgt_part,
                summary_length,
                length_oracle,
                key
            )
            yield example
    
    output = {}
    with multiprocessing.Pool(n_thread) as p:
        result_iterator = p.imap(process_example, example_generator())

        for result in result_iterator:
            ids, sents ,key= result
            output[key] = ids
    
    return output





