# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Rae2JsonItem(scrapy.Item):
    title = scrapy.Field()
    abbrs = scrapy.Field(serializer=list)
    meaning = scrapy.Field()
    #deftype = scrapy.Field()
    synonyms = scrapy.Field(serializer=list)

    def to_dict(self):
        return {
            "title": self["title"],
            "abbrs": self["abbrs"],
            "meaning": self["meaning"],
            #"deftype": self["deftype"],
            "synonyms": self["synonyms"]
        }
