# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import logging
import json

from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


class ExspiderPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        # print(item)
        yield scrapy.Request(item['torrent_url'],
                              meta={
                                  'cookiejar': item['cookies'],
                                  'title': item['title']
                              }
                             )

    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        print(results)
        if not file_paths:
            raise DropItem("Item contains no Files")
        item['file_paths'] = file_paths
        return item

    def file_path(self, request, response=None, info=None):
        title = request.meta['title']
        file_guid = title + '.' + request.url.split('/')[-1].split('?')[0].split('.')[1]
        filename = u'{0}'.format(file_guid)
        return filename