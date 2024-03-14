import scrapy

class DataItem(scrapy.Item):
    title = scrapy.Field()
    desc = scrapy.Field()
    times = scrapy.Field()
    type = scrapy.Field()
