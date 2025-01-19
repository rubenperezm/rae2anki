from rae2json.rae2json.utils.words_utils import is_valid_word
from collections import defaultdict

class CSVCreator:
    def __init__(self, definitions):
        self.definitions = definitions
        self.exception_words = set()
        self.merged_definitions = {}
        self.memo_ref = {}

        self.create_csv()

    def create_csv(self):
        print('Creating Questions...')
        self.create_questions()
        print(f'{len(self.merged_definitions)} meanings retrieved ({len(self.exception_words)} exceptions).')

        print('Merging Answers...')
        self.merge_answers() # Some meanings are repeated but are not considered synonyms in the webpage
        print(f'{len(self.merged_definitions)} questions created.')
        
    def create_questions(self):
        for word_id, definition in self.definitions.items():
            if 'redirections' in definition:
                self.add_if_valid(self.exception_words, definition['title'])
                continue
            
            for meaning_id in definition:
                self.upsert_meaning(word_id, meaning_id)

    def merge_answers(self):
        questions = defaultdict(set)

        for meaning in self.merged_definitions.values():
            questions[meaning['meaning']].update(meaning['answers'])

        for question in questions:
            questions[question] = list(questions[question])

        self.merged_definitions = questions            

    def upsert_meaning(self, word_id, meaning_id, synonym=None):
        if meaning_id not in self.definitions[word_id]:
            return None
        
        if meaning_id in self.memo_ref:
            final_ref = self.memo_ref[meaning_id]
        
        else:
            meaning = self.definitions[word_id][meaning_id]

            self.memo_ref[meaning_id] = None # Avoid infinite loops
            
            if self.is_full_reference(meaning['meaning']):
                word_reference, meaning_reference = self.get_full_reference(meaning['meaning'])
                final_ref = self.upsert_meaning(
                    word_reference, meaning_reference, meaning['title'])

            elif self.is_partial_reference(meaning['meaning']):
                meaning_reference = self.get_partial_reference(meaning['meaning'])
                final_ref = self.upsert_meaning(
                    word_id, meaning_reference, meaning['title'])
                
            else:
                self.merged_definitions[meaning_id] = self.parse_meaning(meaning)
                final_ref = meaning_id

            self.memo_ref[meaning_id] = final_ref

        self._update_collections(final_ref, synonym)
        
        return final_ref

    def _update_collections(self, final_ref, synonym):
        if final_ref is not None:
            self.add_if_valid(self.merged_definitions[final_ref]['answers'], synonym)
        else:
            self.add_if_valid(self.exception_words, synonym)
        
    def parse_meaning(self, meaning):
        parsed_meaning = {
            'meaning': meaning['meaning'],
            'answers': set(meaning['synonyms']),
        }

        self.add_if_valid(parsed_meaning['answers'], meaning['title'])

        return parsed_meaning
    
    def add_if_valid(self, collection, element):
        if element and is_valid_word(element):
            collection.add(element)

    def is_full_reference(self, meaning):
        return len(meaning) == 15 and meaning[7] == '#'

    def is_partial_reference(self, meaning):
        return len(meaning) == 8 and meaning[0] == '#'

    def get_full_reference(self, meaning):
        word_reference = meaning[:7]
        meaning_reference = meaning[8:]

        return word_reference, meaning_reference

    def get_partial_reference(self, meaning):
        meaning_reference = meaning[1:]
        return meaning_reference
    