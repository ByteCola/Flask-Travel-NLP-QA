# 携程网安徽旅游景点信息爬虫

import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re

from lxml.etree import tostring, Element

'''携程网安徽旅游景点地区列表爬虫'''


class SightCrawler:
    def __init__(self):
        self.conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.db = self.conn['sight_qa_db']
        self.col = self.db['sight_data']
        self.place_col = self.db['place_data']

    '''根据url，请求html'''

    def get_html(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')
        return html

    '''测试'''

    def crawler_main(self):
        places_data = self.place_col.find()
        for place in places_data:
            place_name = place['place_name']
            sight_list_url_prefix = place['sight_list_url'][0:-5]
            for page in range(1, 20):
                try:
                    sight_list_url = sight_list_url_prefix + '/s0-p%s.html' % page
                    self.sight_list_crawler(place=place_name, url=sight_list_url)
                except Exception as e:
                    print(e, page)
        return

    '''景点列表解析'''

    def sight_list_crawler(self, place, url):

        html = self.get_html(url)
        selector = etree.HTML(html)
        sight_list = selector.xpath('//div[@class="list_mod2"]')

        # print(tostring(sight_list))
        for sight in sight_list:
            try:
                sight_url = sight.xpath('div[@class="rdetailbox"]/dl/dt/a/@href')[0]
                sight_address = sight.xpath('div[@class="rdetailbox"]/dl/dd[@class="ellipsis"]/text()')[0]
                sight_name = sight.xpath('div[@class="rdetailbox"]/dl/dt/a/@title')[0]
                if place in sight_address:
                    print(sight_url)
                    sight_data = self.sight_crawler(place, sight_url)
                    self.col.insert_one(sight_data)
                else:
                    print('{0}景区的地址为{1}不在{2}地区，不抓取此数据，防止数据错乱'.format(sight_name, sight_address, place))
            except [Exception]:
                continue
                print("继续执行")

    '''景点数据解析'''

    def sight_crawler(self, place, url):

        html = self.get_html(url)
        selector = etree.HTML(html)
        name = selector.xpath('//div[@class="title"]/h1/text()')[0]

        print("the sight name is " + name)
        level = '0'

        level_box = selector.xpath('//div[@class="titleTips"]/span/text()')
        if len(level_box) > 0:
            level = level_box[0]
        print("the sight's level is " + level)
        base_info = selector.xpath('//div[@class="baseInfoContent"]//p[@class="baseInfoText"]/text()')

        address = base_info[0]
        print("the sight's address is " + address)
        telephone = ''
        if len(base_info) > 1:
            telephone = base_info[1]
        print("the sight's telephone is " + telephone)
        detail_info = selector.xpath('//div[@class="detailModule normalModule"]')[0]

        description = detail_info.xpath('div[@class="moduleContent"][1]/div/div')[0]

        # print("the sight's description is " + str(tostring(description).decode("utf-8")))
        print("the sight's description is " + etree.tostring(description, encoding="utf-8", pretty_print=True).decode(
            "utf-8"))
        opentime = detail_info.xpath('div[@class="moduleContent"][2]/text()')[0]
        print("the sight's opentime is " + opentime)
        tips = etree.Element('div')
        print(tips)
        # tips_box = detail_info.xpath('div[@class="moduleContent"][4]/div')
        # print(len(tips_box))
        # if len(tips_box) > 0:
        #     tips = tips_box[0]
        # print("the sight's tips is " + str(tostring(tips)))

        # print(name,level,address,telephone)
        # print(description,opentime,tips)

        sight_data = {}
        sight_data['name'] = name
        sight_data['level'] = level
        sight_data['address'] = address
        sight_data['telephone'] = telephone
        sight_data['description'] = etree.tostring(description, encoding="utf-8", pretty_print=True).decode("utf-8")
        sight_data['opentime'] = opentime
        sight_data['tips'] = etree.tostring(tips, encoding="utf-8", pretty_print=True).decode("utf-8")
        sight_data['place'] = place
        sight_data['url'] = url

        return sight_data


handler = SightCrawler()
handler.crawler_main()
