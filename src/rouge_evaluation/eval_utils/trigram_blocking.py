import nltk

class TrigramBlock:
    def __init__(self):
        self.trigrams = set()

    def check_overlap(self, text):
        tokens = self._preprocess(text)
        trigrams = set(self._get_trigrams(tokens))
        overlap = bool(self.trigrams & trigrams)
        self.trigrams |= trigrams
        return overlap

    def _preprocess(self, text):
        text = text.lower()
        text = ''.join([c for c in text if c.isalpha() or c.isspace()])
        tokens = nltk.word_tokenize(text)
        return tokens

    def _get_trigrams(self, tokens):
        trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)]
        return trigrams