# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MangaTorrentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    torrent_url = scrapy.Field()
    cookies = scrapy.Field()
    title = scrapy.Field()
    file_paths = scrapy.Field()
    post_time = scrapy.Field()
