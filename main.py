import getpass
import json

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from exspider.spiders.TorrentSpider import TorrentSpider


def main():
    username = input('Username:')
    password = getpass.getpass('Password:')

    with open('config.json') as conf_file:
        rule = json.load(conf_file)

    settings = get_project_settings();

    runner = CrawlerRunner(settings)
    runner.crawl(TorrentSpider,
                 user = {
                     'username': username,
                     'password': password
                 },
                 rule = rule)

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

if __name__ == '__main__':
    main()