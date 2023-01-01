# 携程网安徽旅游景点信息爬虫

import urllib.request
import urllib.parse
from lxml import etree
import pymongo
import re

from lxml.etree import tostring

'''携程网安徽旅游景点地区列表爬虫'''


class CtripPlaceCrawler:

    def __init__(self):
        self.conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.db = self.conn['sight_qa_db']
        self.col = self.db.get_collection('place_data')

    def get_html(self, url):
        """根据url，请求html"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')
        return html

    def crawler_main(self):
        """测试"""
        for page in range(1, 9):
            try:
                places_url = 'https://you.ctrip.com/countrysightlist/anhui100068/p%s.html'%page
                # print(places_url)
                self.places_crawler(places_url)
                # print(str(page), places_url)
            except Exception as e:
                print(e, page)
        return

    def places_crawler(self, url):

        """
        地方列表解析
        """
        html = self.get_html(url)
        selector = etree.HTML(html)
        places = selector.xpath('//div[@class="list_mod1"]')

        for place in places:
            # print(tostring(place))
            place_name = place.xpath('div[@class="cityimg"]//span/text()')[0]
            place_img_url = place.xpath('div[@class="cityimg"]/a/img/@src')[0]
            sight_list_url = "https://you.ctrip.com" + place.xpath('dl/dd[last()]/a/@href')[0]
            print(place_name, place_img_url, sight_list_url)

            if place_name:
                place_data = {'place_name': place_name, 'place_img_url': place_img_url,
                              'sight_list_url': sight_list_url}
                self.col.insert_one(place_data)


handler = CtripPlaceCrawler()
handler.crawler_main()
