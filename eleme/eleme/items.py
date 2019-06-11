# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ShopItem(Item):
    shop_name = Field()
    recent_order_num = Field()
    reduction = Field()
    deliver_fee = Field()
    start_fee = Field()
    activity_foods = Field()
    normal_foods = Field()
