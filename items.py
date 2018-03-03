# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CoinpairarbitrageOtcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #pass
    
	otc_user_name = scrapy.Field()
	otc_user_trade_count = scrapy.Field()
	otc_user_currency_price = scrapy.Field()
	otc_user_currency = scrapy.Field()
	otc_type = scrapy.Field()
	current_time = scrapy.Field()
	final_profit = scrapy.Field()

class CoinpairarbitrageBBItem(scrapy.Item):
	current_time = scrapy.Field()
	bb_type = scrapy.Field()
	bb_price = scrapy.Field()
	final_profit = scrapy.Field()
