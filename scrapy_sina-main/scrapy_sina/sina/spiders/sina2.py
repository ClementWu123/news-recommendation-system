import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By

from sina.items import DataItem
import datetime
import re


def parse_namedetail(response):
    selector = Selector(response)
    desc = selector.xpath("//div[@class='article']/p/text()").extract()
    item = response.meta['name']
    desc = list(map(str.strip, desc))
    item['desc'] = ''.join(desc)
    print(item)
    yield item


class Sina2Spider(scrapy.Spider):
    name = 'sina2'

    # allowed_domains = ['sina.com.cn']

    def __init__(self, page=None, flag=None, *args, **kwargs):
        super(Sina2Spider, self).__init__(*args, **kwargs)
        self.page = int(page)
        self.flag = int(flag)
        self.start_urls = ['https://news.sina.com.cn/china/', 'https://ent.sina.com.cn/zongyi/',
                           'https://ent.sina.com.cn/film/', 'https://yue.sina.com.cn/', 'https://ent.sina.com.cn/tv/',
                           'https://ent.sina.com.cn/xiju/']
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('headless')
        self.option.add_argument('no=sandbox')
        self.option.add_argument('--blink-setting=imagesEnable=false')

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        self.option.page_load_strategy = 'eager'
        driver = webdriver.Chrome(options=self.option)
        driver.set_page_load_timeout(30)
        driver.get(response.url)
        for j in range(self.page):
            try:
                while not driver.find_element(By.XPATH, "//div[@class='feed-card-page']").text:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                title = driver.find_elements(By.XPATH, "//div[@class='feed-card-item']/h2/a[@target='_blank']")
                time = driver.find_elements(By.XPATH,
                                        "//div[@class='feed-card-item']/h2/../div[@class='feed-card-a feed-card-clearfix']"
                                        "/div[@class='feed-card-time']")
            except:
                continue

            for i in range(len(title)):
                item = DataItem()
                if response.url == "https://news.sina.com.cn/china/":
                    item['type'] = 'news'

                if response.url == "https://ent.sina.com.cn/zongyi/":
                    item['type'] = 'entertainment'

                if response.url == "https://ent.sina.com.cn/film/":
                    item['type'] = 'film'

                if response.url == "https://yue.sina.com.cn/":
                    item['type'] = 'music'

                if response.url == "https://ent.sina.com.cn/tv/":
                    item['type'] = 'tv'

                if response.url == "https://ent.sina.com.cn/xiju/":
                    item['type'] = 'opera'

                eachtitle = title[i].text
                item['title'] = eachtitle
                item['desc'] = ''
                eachtime = time[i].text

                href = title[i].get_attribute('href')

                today = datetime.datetime.now()
                eachtime = eachtime.replace('今天', str(today.month) + '月' + str(today.day) + '日')

                if '分钟前' in eachtime:
                    minute = int(eachtime.split('分钟前')[0])
                    t = datetime.datetime.now() - datetime.timedelta(minutes=minute)
                    t2 = datetime.datetime(year=t.year, month=t.month, day=t.day, hour=t.hour, minute=t.minute)
                else:
                    if '年' not in eachtime:
                        eachtime = str(today.year) + '年' + eachtime
                    t1 = re.split('[年月日:]', eachtime)
                    t2 = datetime.datetime(year=int(t1[0]), month=int(t1[1]), day=int(t1[2]), hour=int(t1[3]),
                                           minute=int(t1[4]))
                item['times'] = t2

                if self.flag == 1:
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
                    if item['times'].strftime("%Y-%m-%d") < yesterday:
                        driver.close()
                        break
                    if yesterday <= item['times'].strftime("%Y-%m-%d") < today:
                        print(str(item['times']))
                        yield Request(url=response.urljoin(href), meta={'name': item}, callback=parse_namedetail)
                else:
                    try:
                        yield Request(url=response.urljoin(href), meta={'name': item}, callback=parse_namedetail)
                    except:
                        continue

            try:
                driver.find_elements(By.XPATH, "//div[@class='feed-card-page']/span[@class='pagebox_next']/a")[
                    0].click()
            except:
                break
