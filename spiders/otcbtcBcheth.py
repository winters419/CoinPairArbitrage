# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.selector import Selector
from CoinPairArbitrage.items import CoinpairarbitrageOtcItem
from CoinPairArbitrage.items import CoinpairarbitrageBBItem
from datetime import datetime
from scrapy.spiders import Spider
from decimal import Decimal

class OtcbtcBchethSpider(Spider):
    name = 'otcbtcBcheth'
    allowed_domains = ['otcbtc.com']
    start_urls = [
	'https://otcbtc.com/sell_offers?currency=bch&fiat_currency=cny&payment_type=all&sort_by=most_trust',
	'https://otcbtc.com/buy_offers?currency=eth&fiat_currency=cny&payment_type=all&sort_by=most_trust',
        'https://bb.otcbtc.com/exchange/markets/bcheth'
	]
    custom_settings = {
        'ITEM_PIPELINES': {
            'CoinPairArbitrage.pipelines.pipelinesOtcbtcBcheth.CoinpairarbitrageOtcbtcBchethPipeline': 400
        }
    }
    profit_compute_dict = {}

    def parse_otc_item(self, response, otc_currency):
        otc_type_match = re.search(r'.+?com/(.+?)_offers', response.url)
        otc_type_str=otc_type_match.group(1)

        current_time=str(datetime.now()).decode('unicode-escape')
        if otc_type_str == 'buy':
	    min_max_currency_price=Decimal('0.0')
        else:
            min_max_currency_price=Decimal('Inf')

        item=CoinpairarbitrageOtcItem()

        lt=response.xpath('//ul[@class="list-content"]')
        for it in lt:
            trade_count=re.sub("Trade", "", it.xpath('li[@class="user-trust"]/text()').extract()[1], flags=re.UNICODE).strip()
            currency_price=re.sub(",", "", it.xpath('li[@class="price"]/text()').extract()[1], flags=re.UNICODE).strip()
            if int(trade_count) > 10000 and self.is_suitable_price(Decimal(currency_price), min_max_currency_price, otc_type_str):
                min_max_currency_price = Decimal(currency_price)
                item['otc_user_name']=it.xpath('li[@class="user-name"]/a/text()').extract()
                item['otc_user_trade_count']=trade_count
                item['otc_user_currency_price']=currency_price
                item['otc_user_currency']=otc_currency.decode('unicode-escape')
                item['otc_type']=otc_type_str.decode('unicode-escape')
                item['current_time']=current_time
                item['final_profit']=u'10000'
        self.profit_compute_dict[otc_currency]=Decimal(currency_price)
        return item

    def is_suitable_price(self, currency_price, min_max_currency_price, otc_type):
        if otc_type == 'buy':
            return currency_price > min_max_currency_price
        else:
            return currency_price < min_max_currency_price

    def parse_bb_item(self, response):
        first_script_item = response.xpath('//script').extract_first()
        bb_price_match=re.search(r'gon.ticker={"name":"BCH/ETH".+?last":"(.+?)",', first_script_item)

        bb_type_match = re.search(r'.+?markets/(.+?)$', response.url)

        current_time=str(datetime.now()).decode('unicode-escape')

        item=CoinpairarbitrageBBItem()
        item['current_time']=current_time
        item['bb_price']=bb_price_match.group(1).decode('unicode-escape')
        item['bb_type']=bb_type_match.group(1).decode('unicode-escape')
        item['final_profit']=u'10000'

        self.profit_compute_dict[bb_type_match.group(1)]=Decimal(bb_price_match.group(1))
        return item

    def parse(self, response):
        otc_currency_match = re.search(r'currency=(.+?)&', response.url)
        if otc_currency_match:
            otc_item = self.parse_otc_item(response, otc_currency_match.group(1))
            if len(self.profit_compute_dict) == 3:
                adjust_profit = (Decimal(10000) / self.profit_compute_dict['bch']) * self.profit_compute_dict['eth'] * self.profit_compute_dict['bcheth']
                otc_item['final_profit']=unicode(adjust_profit)
            return otc_item

        else:
            bb_item = self.parse_bb_item(response) 
            if len(self.profit_compute_dict) == 3:
                adjust_profit = (Decimal(10000) / self.profit_compute_dict['bch']) * self.profit_compute_dict['eth'] * self.profit_compute_dict['bcheth']
                bb_item['final_profit']=unicode(adjust_profit)
            return bb_item
