import configparser

import finnhub as fn

config = configparser.ConfigParser()

#########################################################################
# Variables
config.read('configs/config.ini')
freetrande_fx_rate = config['finnhub']['FxRate']

fx_fee_rate = float(freetrande_fx_rate)


#########################################################################
# Functions

def total_transaction_cost(total_shares, stock_price):
    total_value = total_stocks_value(stocks_total=total_shares, stock_price=stock_price)

    fx_fee = transaction_fx_fee(amount=total_value)

    total_transaction_cost = fx_fee + total_value

    return total_transaction_cost


def transaction_cost_with_currency_conversion(total_shares, stock_price, currency_rate):
    total_value_usd = total_stocks_value(stocks_total=total_shares, stock_price=stock_price)

    total_value_gbp = convert_currency_with_rate(amount=total_value_usd, rate=currency_rate)

    fx_usd = transaction_fx_fee(amount=total_value_usd)

    fx_gbp = convert_currency_with_rate(amount=fx_usd, rate=currency_rate)

    total_transaction_cost = fx_gbp + total_value_gbp

    return total_transaction_cost


def transaction_fx_fee(amount):
    rtn = amount * fx_fee_rate
    return rtn


def weighted_average(distribution, weights):
    numerator = sum([distribution[i] * weights[i] for i in range(len(distribution))])
    denominator = sum(weights)
    w_avg = numerator / denominator

    # return round(numerator / denominator, 2)
    return w_avg


def change_percentage(old_value, new_value):
    rtn = (new_value - old_value) / old_value

    return round(rtn, 4)


def total_stocks_value(stocks_total, stock_price):
    rtn = stocks_total * stock_price

    return rtn


def convert_currency(amount, from_currency, to_currency):
    exchange_rate = fn.get_exchange_rate(base_currency_symbol=from_currency, compare_with_currency_symbol=to_currency)

    rtn = amount * exchange_rate

    return rtn


def convert_currency_with_rate(amount, rate):
    rtn = amount * (1 / rate)

    return rtn
