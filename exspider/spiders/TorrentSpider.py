import scrapy


class TorrentSpider(scrapy.Spider):
    name = "torrent"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36"

    def __init__(self, user, rule):
        self.username = user['username']
        self.password = user['password']
        self.rule = rule
        self.page = 1

    def start_requests(self):
        return [scrapy.FormRequest(
            "http://forums.e-hentai.org/index.php?act=Login&CODE=01&CookieDate=1",
            meta={'cookiejar': 1},
            formdata={'UserName': self.username,
                      'PassWord': self.password},
            callback=self.first_login,
            dont_filter=True
        )]

    def first_login(self, response):
        return [scrapy.Request(
            "https://exhentai.org/",
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.second_login,
            dont_filter=True
        )]

    def second_login(self, response):
        return [scrapy.Request(
            "https://exhentai.org/?page={0}&f_doujinshi={1}&f_manga={2}&f_artistcg={3}&f_gamecg={4}&f_western={5}&f_non-h={6}&f_imageset={7}&f_cosplay={8}&f_asianporn={9}&f_misc={10}&f_search={11}&f_apply=Apply+Filter&inline_set=dm_t"
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
        articles = response.css('.it5 a::attr(href)').extract()
        next_page_url = response.xpath('//table[@class="ptt"]/tr/td[last()]/a/@href').extract_first()

        for article in articles:
            yield scrapy.Request(article,
                                 callback=self.parse_article,
                                 meta={'cookiejar': response.meta['cookiejar']})

        if next_page_url != None and self.page < (self.rule['end_page'] - self.rule['strat_page'] + 1):
            self.page += 1
            print('Loading Page:' + str(self.page))
            print('next:' + next_page_url)
            yield scrapy.Request(next_page_url,
                                 callback=self.parse,
                                 meta={'cookiejar': response.meta['cookiejar']})

    def parse_article(self, response):
        from scrapy.shell import inspect_response
        inspect_response(response, self)