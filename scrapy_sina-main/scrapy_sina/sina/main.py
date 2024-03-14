from scrapy import cmdline
cmdline.execute('scrapy crawl sina2 -a page=200 -a flag=0'.split())
