import scrapy
import re
import ast
import pprint

from datetime import datetime
from exspider.items import MangaTorrentItem

class TorrentSpider(scrapy.Spider):
    name = "exspider"

    def __init__(self, user, rule):
        self.username = user['username']
        self.password = user['password']
        self.rule = rule
        self.page = 1
        self.last_date = rule['last_date']
        self.new_date = self.last_date



    def start_requests(self):
        print("Sending Login Information...")
        return [scrapy.FormRequest(
            "https://forums.e-hentai.org/index.php?act=Login&CODE=01",
            meta={'cookiejar': 1},
            formdata={'UserName': self.username,
                      'PassWord': self.password,
                      'CookieDate': '1'},
            callback=self.first_login,
            dont_filter=True
        )]

    def first_login(self, response):
        print("Redirecting to ExHentai using cookies....")
        return [scrapy.Request(
            "https://exhentai.org/",
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.second_login,
            dont_filter=True
        )]

    def second_login(self, response):
        print("Requeting aticle list by query condition....")

        return [scrapy.Request(
            "https://exhentai.org/?page={0}&f_doujinshi={1}&f_manga={2}&f_artistcg={3}&f_gamecg={4}&f_western={5}&f_non-h={6}&f_imageset={7}&f_cosplay={8}&f_asianporn={9}&f_misc={10}&f_search={11}&f_apply=Apply+Filter&inline_set=dm_l"
            .format(self.rule['start_page'] - 1,
                    self.rule['doujinshi'],
                    self.rule['manga'],
                    self.rule['artist_cg'],
                    self.rule['game_cg'],
                    self.rule['western'],
                    self.rule['non_h'],
                    self.rule['image_set'],
                    self.rule['cosplay'],
                    self.rule['asian_porn'],
                    self.rule['misc'],
                    self.rule['keyword']),
            meta={'cookiejar': response.meta['cookiejar']}
        )]

    def parse(self, response):
        print("Parsing artical list page..")
        articles = response.css('.it5 a::attr(href)').extract()
        next_page_url = response.xpath('//table[@class="ptt"]/tr/td[last()]/a/@href').extract_first()
        # print(articles)

        for article in articles:
            print(article)
            yield scrapy.Request(article,
                                 callback=self.parse_article,
                                 meta={'cookiejar': response.meta['cookiejar']})

        if next_page_url != None and self.page < (self.rule['end_page'] - self.rule['start_page'] + 1):
            self.page += 1
            print('Loading Page:' + str(self.page))


            print('next:' + next_page_url)
            yield scrapy.Request(next_page_url,
                                 callback=self.parse,
                                 meta={'cookiejar': response.meta['cookiejar']})



    def parse_article(self, response):

        posted_str = response.xpath('//*[@id="gdd"]/table/tr[1]/td[last()]/text()').extract_first()
        posted_date = datetime.strptime(posted_str, "%Y-%m-%d %H:%M")
        last_date = datetime.strptime(self.last_date, "%Y-%m-%d %H:%M")
        if posted_date < last_date:
            print(posted_str + posted_date + ':' + last_date)
            return

        torrent_header = response.xpath('//*[@id="gd5"]/p[3]/a/text()').extract_first()
        thre = re.compile(r'\((.*?)\)')
        torrent_num = ast.literal_eval(thre.search(torrent_header).group(1).strip())

        if torrent_num < 0:
            print(posted_str + posted_date + ':' + '0')
            return

        if posted_date > datetime.strptime(self.new_date, "%Y-%m-%d %H:%M"):
            self.new_date = posted_date.strftime("%Y-%m-%d %H:%M")

        torrent_url = response.xpath('//*[@id="gd5"]/p[3]/a/@onclick').extract_first()
        # print(torrent_url)
        urlre = re.compile(r'\'(.*?)\'')
        torrent_popup_window_url = urlre.search(torrent_url).group(1).strip()
        posted_str = posted_date.strftime("%Y-%m-%d-%H-%M")


        yield scrapy.Request(torrent_popup_window_url,
                             callback=self.parse_torrent_window,
                             meta={'cookiejar': response.meta['cookiejar'],
                                   'post_time':posted_str})

    def parse_torrent_window(self, response):
        print("Parsing torrent window")
        torrent_table_list = response.xpath('//table')

        max_seed_url = ""
        max_seed_num = -1
        max_seed_title = ""

        for index, torrent_table in enumerate(torrent_table_list):
            seeds_num = ast.literal_eval(torrent_table.xpath('//tr[1]/td[5]/text()').extract_first().strip())
            torrent_url_raw = torrent_table.xpath('//tr[3]/td[1]/a/@onclick').extract_first()
            title = torrent_table.xpath('//tr[3]/td[1]/a/text()').extract_first()
            urlre = re.compile(r'\'(.*?)\'')
            torrent_file_url = urlre.search(torrent_url_raw).group(1).strip()

            # print(seeds_num)
            # print(torrent_file_url)
            # print(title)

            if seeds_num > max_seed_num:
                max_seed_num = seeds_num
                max_seed_url = torrent_file_url
                max_seed_title = title

        item = MangaTorrentItem()
        item['torrent_url'] = max_seed_url
        item['cookies'] = response.meta['cookiejar']
        item['title'] = max_seed_title
        item['post_time'] = response.meta['post_time']

        print(item['torrent_url'] )

        yield item
