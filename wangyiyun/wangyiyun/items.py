# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HotSongItem(Item):
    table = 'hot_song'
    name = Field()
    comments = Field()
    singer = Field()


class HotCommentItem(Item):
    table = 'hot_comment'
    name = Field()
    content = Field()
    like_num = Field()
