import scrapy
import json 
import random
from urllib.parse import urlparse
from urllib.parse import unquote

from ..items import Rae2JsonItem as R2J
from ..const import USER_AGENT_LIST, CLASS_NAME_WORD_MEANINGS, CLASS_NAME_LOCUTION_MEANINGS, MARKS
from ..utils.words_utils import clean_words, read_words

class RaespiderdefinitionsSpider(scrapy.Spider):
    name = "raespiderdefinitions"
    allowed_domains = ["dle.rae.es"]
   
    USER_AGENT_LIST = USER_AGENT_LIST
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        all_words = read_words("../data/23-8.txt")
        
        # with open("../data/test.json", "r") as f:
        #     all_words = json.load(f)
        
        #generate list of all word links to scrape base on the list of words provided by raespiderwords.py scrapper
        self.start_urls = ["https://dle.rae.es/{}".format(word) for word in all_words]
   
    #change the user agent in each request randomly
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={'User-Agent': random.choice(self.USER_AGENT_LIST)})
    
    def parse(self, response):
        current_word = self.get_current_word_from_url(response)
        # get definitions
        word_ids = response.xpath('.//article').css('::attr(id)').extract()
        definitions = response.xpath('.//section[@class="c-section" and not(@id)]').extract()

        for definition, word_id in zip(definitions, word_ids): 
            def_items = self.get_word_definition_data(current_word, definition)
            yield {word_id: def_items}

    def get_word_definition_data(self, word, definition):
        #divide by meanings and locutions
        meanings = scrapy.Selector(text=definition).xpath('.//ol[@class="c-definitions"]').extract()

        if len(meanings) == 0:
            redirections = (scrapy.Selector(text=definition).xpath('.//h3/a[@class="a"]')
                .css('::attr(href)').extract())

            for i in range(len(redirections)):
                redirections[i] = redirections[i].lstrip('/?id=')

            return redirections

        
        def_items = {}

        # get meanings
        self.get_meanings(word, meanings[0], def_items)

        # get locutions
        locutions = scrapy.Selector(text=definition).xpath('.//h3[@id]').extract()
        for i in range(1, len(meanings)):
            locution = "".join(scrapy.Selector(text=locutions[i-1]).xpath('.//text()').extract())
            self.get_meanings(locution, meanings[i], def_items, is_locution=True)

        return def_items

    def get_meanings(self, title, definitions, def_items, is_locution=False):
        class_name = CLASS_NAME_LOCUTION_MEANINGS if is_locution else CLASS_NAME_WORD_MEANINGS
        for definition in scrapy.Selector(text=definitions).xpath(f'.//li[@class="{class_name}"]').extract():
            definition_id = scrapy.Selector(text=definition).css('::attr(id)').get()
            def_items[definition_id] = self.extract_item_information(title, definition).to_dict()

    def extract_item_information(self, word, element):
        abbrs, definition = self.get_text_or_references(element)
        synonyms = self.get_synonyms(element)
        return R2J(title=word, definition=definition,
                   synonyms=self.filter_synonyms(synonyms),
                   abbrs=abbrs,
                #deftype="Loc" if is_locution else "Word"
                )

    def filter_abbr(self, abbr_text):
        return [abbr for abbr in abbr_text if abbr in MARKS]
    
    #extracts current word from the url
    def get_current_word_from_url(self, response):
        return unquote(urlparse(response.url).path.lstrip("/"))
    
    def get_text_or_references(self, element):
        elm = scrapy.Selector(text=element).xpath('.//div[@class="c-definitions__item"]/div[1]').get()
        link = scrapy.Selector(text=elm).xpath('.//a').get()

        abbrs = self.filter_abbr(scrapy.Selector(text=elm).css("abbr::text").extract())
        if link:
            meaning = scrapy.Selector(text=link).css('::attr(href)').get().lstrip('/?id=')

            if len(scrapy.Selector(text=link).css('::attr(href)').extract()) > 1:
                raise ValueError("More than one reference found")
            
            return abbrs, meaning
        
        meaning = scrapy.Selector(text=elm).xpath('.//text()[not(ancestor::*[@class])]').extract()

        return abbrs, self.fix_meaning_format(meaning)
    
    def fix_meaning_format(self, meaning):
        '''
        Fix the format of the meaning. Specifically, it fixes the problems
        caused by removing "etc." from the meanings, and strips the meaning.
        '''
        fixed_meaning = [meaning[0]]

        for i in range(1, len(meaning)):
            if meaning[i] == " " and meaning[i-1] == ", ": # ", etc.: "
                fixed_meaning[-1] += ":"
            else:
                fixed_meaning.append(meaning[i])

        if fixed_meaning[-1] == ", ": # ", etc." at the end of the meaning
            fixed_meaning[-1] = "."

        return "".join(fixed_meaning).strip()
        
    def get_synonyms(self, element):
        synonym_div = scrapy.Selector(text=element).xpath('//div[@class="c-word-list"][.//abbr[@title="Sinónimos o afines"]]')
        synonyms = synonym_div.xpath('.//span[@class="sin"]/text()').extract()
        
        return synonyms

    def filter_synonyms(self, synonyms):
        return clean_words(synonyms)
    