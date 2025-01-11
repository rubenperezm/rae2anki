import re

# - Words that contain hyphens or whitespaces
# - Words that start with K, Ñ, Q, W, X, or Y and do not contain Ñ, Q, X, or Y
unasked_words = re.compile(r'[- ]|^[KÑQWXY][^ÑQXY]*$', re.IGNORECASE)

def read_words(filename):
    '''
    Read words from a file. Remove the newline character at the end of each line.
    '''

    with open(filename, 'r') as f:
        return [line.strip() for line in f]
    
def write_words(words, filename):
    '''
    Write words to a file.
    '''

    with open(filename, 'w') as f:
        f.writelines(words)

def clean_words(words, start=None):
    '''
    Remove words with whitespaces or hyphens.

    Args:
        words: list of words to clean
        start: if provided, returns only words that start with the given string
    '''
    return [word for word in words if not unasked_words.search(word) and 
            (start is None or word.startswith(start))]