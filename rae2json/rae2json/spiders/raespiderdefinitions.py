import scrapy
import json 
import random
from urllib.parse import urlparse
from urllib.parse import unquote

from ..items import Rae2JsonItem as R2J
from ..utils.words_utils import clean_words, read_words, is_valid_word
from ..const import (
    USER_AGENT_LIST, 
    CLASS_NAME_WORD_MEANINGS, 
    CLASS_NAME_LOCUTION_MEANINGS,
    CONTEXT_MARKS,
    WORD_MARKS
)

class RaespiderdefinitionsSpider(scrapy.Spider):
    name = "raespiderdefinitions"
    allowed_domains = ["dle.rae.es"]
   
    USER_AGENT_LIST = USER_AGENT_LIST
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        input_file = kwargs.get("INPUT_FILE", None)
        all_words = read_words(input_file)
        
        self.start_urls = ["https://dle.rae.es/{}".format(word) for word in all_words]
   
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={'User-Agent': random.choice(self.USER_AGENT_LIST)})
    
    def parse(self, response):
        current_word = self.get_current_word_from_url(response)

        # get all definitions from the page
        word_ids = response.css('article::attr(id)').extract()
        definitions = response.xpath('.//section[@class="c-section" and not(@id)]').extract()

        for definition, word_id in zip(definitions, word_ids): 
            def_items = self.get_word_definition_data(current_word, definition)
            yield {word_id: def_items}

    def get_current_word_from_url(self, response):
        '''
        Get the word from the url.
        '''
        return unquote(urlparse(response.url).path.lstrip("/"))

    def get_word_definition_data(self, word, definition):
        '''
        Get the information of a definition.
        '''

        definition_entries = scrapy.Selector(text=definition) \
            .xpath('.//ol[@class="c-definitions"] | .//h3[preceding-sibling::*[1][self::h3[@id]]]').extract()

        # Words without definitions, but appear within locutions in other entries 
        if len(definition_entries) == 0:
            return self.get_redirections(word, definition)

        def_items = {}

        # Get locutions
        locutions = scrapy.Selector(text=definition).xpath('.//h3[@id]').extract()

        # Get meanings
        
        shift = 0
        if len(definition_entries) == len(locutions) + 1:
            self.get_meanings(word, definition_entries[0], def_items)
            shift = 1
            
        for i in range(len(locutions)):
            locution = "".join(scrapy.Selector(text=locutions[i]).xpath('.//text()').extract())
            locution_id = scrapy.Selector(text=locutions[i]).css('::attr(id)').get()
            self.get_meanings(locution, definition_entries[i+shift], def_items, is_locution=True, locution_id = locution_id)

        return def_items

    def get_redirections(self, word, definition):
        '''
        Get the redirections of a word that does not have a definition.
        '''
        redirections = (scrapy.Selector(text=definition).xpath('.//h3/a[@class="a"]')
                .css('::attr(href)').extract())

        for i in range(len(redirections)):
            redirections[i] = redirections[i].lstrip('/?id=')

        return {"title": word, "redirections": redirections}

    def get_meanings(self, title, meanings, def_items, is_locution=False, locution_id=None):
        '''
        Get the meaning of a given word or locution.
        '''
        class_name = CLASS_NAME_LOCUTION_MEANINGS if is_locution else CLASS_NAME_WORD_MEANINGS

        if meanings_list := scrapy.Selector(text=meanings).xpath(f'.//li[starts-with(@class, "{class_name}")]').extract():
            for meaning in meanings_list:
                meaning_id = scrapy.Selector(text=meaning).css('::attr(id)').get()
                def_items[meaning_id] = self.extract_item_information(title, meaning).to_dict()
        elif not locution_id:
            raise ValueError("No meanings found for word: {}".format(title))
        else:
            def_items[locution_id] = R2J(
                title=title,
                abbrs="", 
                meaning=scrapy.Selector(text=meanings).css('::attr(href)').get().lstrip('/?id='),
                synonyms=[]).to_dict(
            )
            


    def extract_item_information(self, title, definition):
        '''
        Create an object with the information of the word.
        '''
        abbrs, meaning = self.get_abbrs_and_meaning(definition)
        synonyms = self.get_synonyms(definition, title)

        return R2J(title=title, abbrs=abbrs, meaning=meaning, synonyms=synonyms)
    
    def get_abbrs_and_meaning(self, element):
        '''
        Get all the information provided in the meaning 
        (useful abbrs and the meaning itself).
        '''
        elm = scrapy.Selector(text=element).xpath('.//div[@class="c-definitions__item"]/div[1]').get()

        context_abbrs, word_abbrs = self.get_abbrs(elm)

        if link := scrapy.Selector(text=elm).xpath('.//a[not(preceding-sibling::*[@data-id])]').get(): # Reference to another meaning
            meaning = scrapy.Selector(text=link).css('::attr(href)').get().lstrip('/?id=')
            return word_abbrs, meaning
        else:
            meaning = [context_abbrs] if context_abbrs else []
            meaning.extend(scrapy.Selector(text=elm).xpath('.//text()[not(ancestor::*[@class]) or ancestor::*[@class="u" or @class="a"]]').extract())
            return word_abbrs, self.fix_meaning_format(meaning)
    
    def get_abbrs(self, element):
        '''
        Get the abbreviations of the word from the meaning.
        '''
        return self.filter_and_classify_abbrs(scrapy.Selector(text=element).css("abbr::text").extract())

    def filter_and_classify_abbrs(self, abbr_text):
        '''
        Classify the abbrs in the text as context abbrs or word abbrs.
        See const.py file to see the lists of abbreviations.
        '''
        context_abbrs, word_abbrs = [], []

        for abbr in abbr_text:
            if abbr in CONTEXT_MARKS:
                context_abbrs.append(abbr)
            elif abbr in WORD_MARKS:
                word_abbrs.append(abbr)

        return " ".join(context_abbrs), " ".join(word_abbrs)

    def fix_meaning_format(self, meaning):
        '''
        Fix the format of the meaning. Specifically, it fixes the problems
        caused by removing "etc." from the meanings, and strips the meaning.
        '''
        fixed_meaning = [meaning[0]]

        for i in range(1, len(meaning)):
            if meaning[i] == " " and meaning[i-1] == " ":
                continue
            elif meaning[i] == " " and meaning[i-1] == ", ": # ", etc.: "
                fixed_meaning[-1] += ":"
            else:
                fixed_meaning.append(meaning[i])

        if fixed_meaning[-1] == ", ": # ", etc." at the end of the meaning
            fixed_meaning[-1] = "."

        return "".join(fixed_meaning).strip()
        
    def get_synonyms(self, element, word):
        '''
        Get the synonyms of the word from the meaning.
        '''
        if not is_valid_word(word):
            return []
        
        synonym_div = scrapy.Selector(text=element).xpath('//div[@class="c-word-list"][.//abbr[@title="Sinónimos o afines"]]')
        synonyms = synonym_div.xpath('.//span[@class="sin"]/text()').extract()
        
        return self.filter_synonyms(synonyms, word)

    def filter_synonyms(self, synonyms, word):
        '''
        Filter the synoynms that are not valid in Pasapalabra.
        '''
        return clean_words(synonyms, word)