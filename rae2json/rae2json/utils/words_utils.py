import re
import json

# - Words that contain hyphens or whitespaces
# - Words that start with K, Ñ, Q, W, X, or Y and do not contain Ñ, Q, X, or Y
unasked_words = re.compile(r'[ \-(‒́)]|^[KÑQWXY][^ÑQXY]*$', re.IGNORECASE)

def read_words(txt_filename):
    '''
    Read words from a file. Remove the newline character at the end of each line.
    '''

    with open(txt_filename, 'r') as f:
        return [line.strip() for line in f]
    
def read_definitions(json_filename):
    '''
    Read definitions from a file.
    '''
    with open(json_filename, 'r') as f:
        return json.load(f)
    
def write_words(words, filename):
    '''
    Write words to a file.
    '''

    with open(filename, 'w') as f:
        for word in words:
            f.write(word + '\n')

def clean_words(words, base_word=None):
    '''
    Remove words with whitespaces or hyphens.

    Args:
        words: list of words to clean
        base_word: if provided, returns only words that belong to the same deck
    '''
    return [word for word in words if not unasked_words.search(word) and 
            (base_word is None or check_same_deck(word, base_word))]

def is_valid_word(word, base_word=None):
    '''
    Check if a word is valid.
    If a base word is provided, check if the word belongs to the same deck.
    '''
    return not unasked_words.search(word) and \
        (base_word is None or check_same_deck(word, base_word))
        
def check_same_deck(word1, word2):
    return starts_with_same_letter(word1, word2) or \
            any(letter in word1 and letter in word2 
                for letter in ['ñ', 'q', 'y', 'z'])

def starts_with_same_letter(word1, word2):
    word1, word2 = word1.lower(), word2.lower()

    return word1[0] == word2[0] or \
    (word1[0] in 'aá' and word2[0] in 'aá') or \
    (word1[0] in 'eé' and word2[0] in 'eé') or \
    (word1[0] in 'ií' and word2[0] in 'ií') or \
    (word1[0] in 'oó' and word2[0] in 'oó') or \
    (word1[0] in 'uú' and word2[0] in 'uú')

def get_letter(letter):
    if letter == 'Á': return 'A'
    if letter == 'É': return 'E'
    if letter == 'Í': return 'I'
    if letter == 'Ó': return 'O'
    if letter == 'Ú': return 'U'
    return letter