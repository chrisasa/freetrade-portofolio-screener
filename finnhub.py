import configparser

import requests

config = configparser.ConfigParser()

config.read('configs/config_sec.ini')
api_key = config['finnhub']['ApiToken']

config.read('configs/config.ini')
url_api_base = config['finnhub']['BaseUrl']


def get_stock_quote(stock_symbol):
    url_quotes = url_api_base + 'quote?symbol=' + stock_symbol.upper() + '&token=' + api_key
    rsp = requests.get(url_quotes)
    quote = rsp.json()

    return quote


def get_stock_price(stock_symbol):
    qt = get_stock_quote(stock_symbol)
    current_price = qt["c"]
    # print("%s --> %d" % (stock_symbol, current_price))
    return current_price


def get_stock_price_and_timestamp(stock_symbol):
    qt = get_stock_quote(stock_symbol)

    obj = {
        "current_price": qt["c"],
        "timestamp": qt["t"]
    }

    return obj


def get_exchange_rate(base_currency_symbol, compare_with_currency_symbol):
    if base_currency_symbol == compare_with_currency_symbol:
        return 1.000

    url = url_api_base + '/forex/rates?' + 'token=' + api_key + '&base=' + base_currency_symbol

    response = requests.get(url)

    currency_rate_obj = response.json()

    currency_rate_raw = currency_rate_obj['quote'][compare_with_currency_symbol]

    currency_rate_rounded = round(currency_rate_raw, 4)

    rtn = currency_rate_rounded

    return rtn
