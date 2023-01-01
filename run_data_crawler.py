from carwler.crawler_ctrip_place import CtripPlaceCrawler
from carwler.crawler_ctrip_sight import SightCrawler

if __name__ == '__main__':

    print("爬取携程网数据并存储至mongodb数据库中")

    ctrip_place_crawler = CtripPlaceCrawler()
    ctrip_place_crawler.crawler_main()

    sight_crawler = SightCrawler()
    sight_crawler.crawler_main()

