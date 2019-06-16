# -*- coding: utf-8 -*-
import scrapy
import re
from lxml import etree
from ..items import HotCommentItem, HotSongItem
from scrapy.linkextractors import LinkExtractor
import urllib

class CommentsSpider(scrapy.Spider):
    name = 'comments'
    allowed_domains = ['music.163.com']
    start_urls = ['https://music.163.com/#/discover/playlist/?',
                  'https://music.163.com/#/song?id=1345848098']
    params = {
        'order': 'hot',
        'cat': '全部',
        'limit': 35,
        'offset': 105
    }

    # 网易云热门歌单url（一页35个）
    def start_requests(self):
        url = self.start_urls[0] +'?'+ urllib.parse.urlencode(self.params)
        yield scrapy.Request(url=url, callback=self.discover_parse)

    # 提取歌单url
    def discover_parse(self, response):
        pattern = '/playlist\?id=\d*$'
        le = LinkExtractor(allow=pattern)
        links = le.extract_links(response)
        for link in links:
            url = link.url
            yield scrapy.Request(url=url, callback=self.playlist_parse)

    # 提取歌单中歌曲url
    def playlist_parse(self, response):
        pattern = '/song\?id=\d*$'
        le = LinkExtractor(allow=pattern)
        links = le.extract_links(response)
        for link in links:
            url = link.url
            yield scrapy.Request(url=url, meta={'song': True}, callback=self.parse)

    # 提取歌曲中的信息
    def parse(self, response):
        hot_song = HotSongItem()
        hot_comment = HotCommentItem()
        # 歌单中的歌曲
        name = response.xpath("//em[@class='f-ff2']/text()").extract_first()
        comment_num = response.xpath("//span[@id='cnt_comment_count']/text()").extract_first()
        singer = response.xpath("//p[@class='des s-fc4']//span/@title").extract_first()
        hot_song['name'] = name             # 歌名
        hot_song['comments'] = comment_num  # 评论数
        hot_song['singer'] = singer         # 歌手
        yield hot_song
        # 热门评论（大于等于十万）
        comment_list = response.xpath("//div[@class='cmmts j-flag']/div").extract()
        for comment in comment_list:
            html = etree.HTML(comment)
            likes = html.xpath(".//a[@data-type='like']/text()")
            number = re.match('\s*\((.*)万\)', likes[0] if len(likes)>0 else '')
            if number:
                content = html.xpath(".//div[@class='cnt f-brk']/text()")
                hot_comment['name'] = name                  # 歌名
                hot_comment['content'] = content[0][1:]     # 评论内容
                hot_comment['like_num'] = number.group(1)   # 点赞数/万
                yield hot_comment
        # 热门歌单翻页
        if self.params['offset'] < 350:
            self.params['offset'] = self.params['offset'] + 35
            url = self.start_urls[0] + '?' + urllib.parse.urlencode(self.params)
            print(url)
            yield scrapy.Request(url=url, callback=self.start_requests)