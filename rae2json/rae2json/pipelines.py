# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter

class Rae2JsonPipeline:
    def __init__(self, output_file):
        self.output_file = output_file
        self.file = None
        self.data = {}

    @classmethod
    def from_crawler(cls, crawler):
        output_file = crawler.settings.get('OUTPUT_FILE', 'output.json')
        return cls(output_file)
    
    def open_spider(self):
        self.file = open(self.output_file, 'w', encoding='utf-8')

    def close_spider(self):
        json.dump(self.data, self.file, ensure_ascii=False)
        self.file.close()

    def process_item(self, item):
        self.data.update(item)
        return item
