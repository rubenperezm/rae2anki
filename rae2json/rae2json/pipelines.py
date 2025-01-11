# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter

class Rae2JsonPipeline:
    def open_spider(self, spider):
        output_file = spider.settings.get('OUTPUT_FILE', 'output.json')
        self.file = open(output_file, 'w', encoding='utf-8')
        self.data = {}

    def close_spider(self, spider):
        json.dump(self.data, self.file, ensure_ascii=False)
        self.file.close()

    def process_item(self, item, spider):
        self.data.update(item)
        return item
