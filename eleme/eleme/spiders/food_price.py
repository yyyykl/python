# -*- coding: utf-8 -*-
import scrapy
import json
import re
from pprint import pprint
from ..items import ShopItem

class FoodPrice(scrapy.Spider):
    name = "food"  # spider名字
    latitude = 31.930451  # 纬度（根据位置修改）
    longtitude = 118.88199  # 经度
    offset = 0  # 页数
    geohash = "wtst9hz0r5kx"  # 未知作用，不知道是不是固定的
    allowed_domains = ["ele.me"]  # 允许访问域名
    start_urls = [
        "https://www.ele.me/restapi/shopping/restaurants?"
        "extras%5B%5D=activities&geohash={3}&latitude={0}"
        "&limit=30&longitude={1}&offset={2}&terminal=web".format(
            latitude, longtitude, offset, geohash
        )
    ]

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0], meta={"cookiejar": "chrome"}, dont_filter=True
        )

    def parse(self, response):
        restaurants = json.loads(response.text)  # 将response的内容转化为json格式
        # 对每个店铺信息进行分析提取
        for item in restaurants:
            try:
                # 店名
                name = item["name"]
                # 满减（因为吃土少年很穷所以只用得起第一个满减）
                if item["activities"]:
                    discount = item["activities"][0]["description"]
                    cheapest = re.match("(满\d+?减\d+?)", discount)  # 用正则表达式提取满减信息
                    reduction = cheapest.group() if cheapest else "这家店很扣"
                else:
                    reduction = "这家店很扣"
                # 月售
                recent_order_num = item['recent_order_num']
                # 配送费
                deliver_fee = item["piecewise_agent_fee"]["rules"][0]["fee"]
                # 起送费
                start_fee = item["piecewise_agent_fee"]["rules"][0]["price"]
                # 店铺id
                id = item["id"]
                shop_url = (
                    "https://www.ele.me/restapi/shopping/v2/menu?restaurant_id=" + id + "&terminal=web"
                )
                # 调用店铺商品信息API
                yield scrapy.Request(
                    shop_url,
                    meta={
                        "cookiejar": "chrome",
                        "name": name,
                        "reduction": reduction,
                        "deliver_fee": deliver_fee,
                        "start_fee": start_fee,
                        "recent_order_num": recent_order_num,
                    },
                    callback=self.shop_parse,
                )
            except IndexError as e:
                self.logger.debug(e, item)
        if self.offset < 90:
            self.offset += 30  # 页数加30
            next_url = (
                "https://www.ele.me/restapi/shopping/restaurants?"
                "extras%5B%5D=activities&geohash={3}&latitude={0}"
                "&limit=30&longitude={1}&offset={2}&terminal=web".format(
                    self.latitude, self.longtitude, self.offset, self.geohash
                )
            )
            # 查看下30个店铺
            yield scrapy.Request(
                next_url, meta={"cookiejar": "chrome"}, callback=self.parse
            )

    def shop_parse(self, response):
        shop = ShopItem()
        items = json.loads(response.text)
        meta = response.meta
        shop['shop_name'] = meta['name']
        shop['recent_order_num'] = meta['recent_order_num']
        shop['reduction'] = meta['reduction']
        shop['deliver_fee'] = meta['deliver_fee']
        shop['start_fee'] = meta['start_fee']
        # 优惠商品列表
        activity_foods = []
        # 普通商品列表
        normal_foods = []
        # 菜单中每个菜品
        for menu in items:
            # 菜品中每个菜
            for food in menu['foods']:
                food_name = food['name']
                lowest_price = food['lowest_price']
                if lowest_price != 0:
                    for index in range(len(food['specfoods'])):
                        if food['specfoods'][index]['price'] == lowest_price:
                            # 打包费
                            packing_fee = food['specfoods'][index]['packing_fee']
                            # 是否是打折商品
                            if food['activity']:
                                original_price = food['specfoods'][index]['original_price']
                                # 折扣 = 折后价/原价（保留两位小数）
                                discount = round(lowest_price/original_price, 2)
                                # 价格 = 折后价+打包费
                                activity_foods.append({
                                    'name': food_name,
                                    'price': lowest_price+packing_fee,
                                    'discount': discount
                                })
                            else:
                                # 价格 = 折后价+打包费
                                normal_foods.append({
                                    'name': food_name,
                                    'price': lowest_price + packing_fee,
                                })
        shop['activity_foods'] = activity_foods
        shop['normal_foods'] = normal_foods
        yield shop
