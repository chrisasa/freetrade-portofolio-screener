import configparser
import csv
import json
import os
import random
import time
from datetime import datetime, timezone

import pandas as pd

import admintools
import toolbox as tbx
from exporters.influxdb import exporter_influxdb as infdb

#  ================================================================================
config = configparser.ConfigParser()

config.read('configs/config.ini')

portfolio_averages_data = config['FilePaths']['PortfolioAveragesData']
output_data_csv = config['FilePaths']['OutputData']

refresh_interval_sec = 2


#  ================================================================================

def average_portfolio_stock_price(transactions_file):
    price_list = []
    total_shares_list = []

    with open(transactions_file) as json_file:
        data = json.load(json_file)

        for trn in data['transactions']:
            price_list.append(trn['stock_price_usd'])
            total_shares_list.append(trn['total_shares'])

    return tbx.weighted_average(price_list, total_shares_list)


def average_portfolio_stock_currency_rate(transactions_file):
    currency_list = []
    total_shares_list = []

    with open(transactions_file) as json_file:
        data = json.load(json_file)

        for trn in data['transactions']:
            currency_list.append(trn['currency_gbp_to_usd'])
            total_shares_list.append(trn['total_shares'])

    return tbx.weighted_average(currency_list, total_shares_list)


def total_portfolio_stock_amount(transactions_file):
    total_stocks_amount = 0

    with open(transactions_file) as json_file:
        data = json.load(json_file)

        for trn in data['transactions']:
            total_stocks_amount += trn['total_shares']

    return total_stocks_amount


def calc_portfolio_averages(stocks_json_folder_path, stocks_list, output_portfolio_avg_file_path):
    admintools.clear_file(output_portfolio_avg_file_path)
    output_data = {}
    output_data['stocks'] = []

    for stock in stocks_list:
        tmpfilepath = "%s%s.json" % (stocks_json_folder_path, stock)

        output_data['stocks'].append({
            'ticker': stock,
            'total_shares': total_portfolio_stock_amount(tmpfilepath),
            'avg_stock_price_usd': average_portfolio_stock_price(tmpfilepath),
            'avg_currency_gbp_to_usd': average_portfolio_stock_currency_rate(tmpfilepath)
        })

    with open(output_portfolio_avg_file_path, 'w+') as outfile:
        json.dump(obj=output_data, fp=outfile, ensure_ascii=False, indent=2)


# Id
fld_out_data_pull_id = 'pull_id'
fld_out_data_ticker = 'stock_symbol'
fld_out_data_timestamp = 'timestamp'
# Current
fld_out_data_cur_stock_price_usd = 'current_stock_price_usd'
fld_out_data_cur_price_change_percent = 'current_price_change_percent'
fld_out_data_cur_total_value_usd = 'current_total_value_usd'
fld_out_data_cur_total_value_gbp = 'current_total_value_gbp'
fld_out_data_cur_total_value_after_fee_gbp = 'current_total_value_after_fee_gbp'
# Sell all
fld_out_data_cur_sell_fx_fee_gbp = 'current_sell_fx_fee_gbp'
fld_out_data_cur_sell_pre_fee_change_gbp = 'current_sell_change_gbp'
fld_out_data_cur_sell_pre_fee_change_percent = 'current_sell_change_percent'
fld_out_data_cur_sell_balance_gbp = 'current_sell_balance_gbp'
fld_out_data_cur_sell_balance_percent = 'current_sell_balance_percent'
# AVG details
fld_out_data_pfl_total_shares = 'pfl_total_shares'
fld_out_data_pfl_avg_price_usd = 'pfl_avg_price_usd'
fld_out_data_pfl_avg_rate_gbp_usd = 'pfl_avg_rate_gbp_usd'
fld_out_data_pfl_total_investment_usd = 'pfl_total_investment_usd'
fld_out_data_pfl_total_investment_gbp = 'pfl_total_investment_gbp'
fld_out_data_pfl_total_fx_fee_usd = 'pfl_total_fx_fee_usd'
fld_out_data_pfl_total_fx_fee_gbp = 'pfl_total_fx_fee_gbp'
fld_out_data_pfl_total_cost_gbp = 'pfl_total_cost_gbp'

field_names = [
    # Id
    fld_out_data_pull_id,
    fld_out_data_ticker,
    fld_out_data_timestamp,
    # Current
    fld_out_data_cur_stock_price_usd,
    fld_out_data_cur_price_change_percent,
    fld_out_data_cur_total_value_usd,
    fld_out_data_cur_total_value_gbp,
    fld_out_data_cur_total_value_after_fee_gbp,
    # Sell all
    fld_out_data_cur_sell_fx_fee_gbp,
    fld_out_data_cur_sell_pre_fee_change_gbp,
    fld_out_data_cur_sell_pre_fee_change_percent,
    fld_out_data_cur_sell_balance_gbp,
    fld_out_data_cur_sell_balance_percent,
    # AVG details
    fld_out_data_pfl_total_shares,
    fld_out_data_pfl_avg_price_usd,
    fld_out_data_pfl_avg_rate_gbp_usd,
    fld_out_data_pfl_total_investment_usd,
    fld_out_data_pfl_total_investment_gbp,
    fld_out_data_pfl_total_fx_fee_usd,
    fld_out_data_pfl_total_fx_fee_gbp,
    fld_out_data_pfl_total_cost_gbp
]


def append_current_status(info_obj_list, output_csv_file, fields_names):
    with open(output_csv_file, 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fields_names)

        for info in info_obj_list:
            csv_writer.writerow(info)


def get_current_status(stock_symbol_list, portfolio_avg_file, output_csv_file, fields_names):
    if not (os.path.isfile(output_csv_file)):
        with open(output_csv_file, 'w+') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fields_names)
            csv_writer.writeheader()  # file doesn't exist yet, write a header

    while True:
        ts = datetime.now(timezone.utc).timestamp()

        pull_ts = pd.Timestamp.utcnow()

        pull_id = datetime.utcfromtimestamp(ts).strftime('%Y%m%d_%H%M%S')

        info_obj_list = []

        # Read the averages from file

        with open(portfolio_avg_file) as json_file:
            pfl_avg_data = json.load(json_file)

        for ticker in stock_symbol_list:
            info = stock_info(pfl_avg_data, pull_id, pull_ts, ticker)
            info_obj_list.append(info)
            # print(info)

            # --- InfluxDB ---
            # current_stock_price_usd = info.get(fld_out_data_cur_stock_price_usd)
            # data_tag = ticker.lower()
            # data = ('test=ola-kala current_stock_price_usd=%s' % current_stock_price_usd)
            # data = ('%s,%s' % (data_tag, data) )
            # infdb.write_data(data=data)

            # --- Pushgateway ---
            # registry_info = CollectorRegistry()
            # tmp_name = 'stock_price_' + ticker
            # i = Info(tmp_name, 'Description of info', registry=registry_info)
            # keys_values = info.items()
            # new_info = {str(key): str(value) for key, value in keys_values}
            # i.info(new_info)
            # tmp_job_name = ('stock_info_' + ticker)
            # push_to_gateway('localhost:9091', job=tmp_job_name, registry=registry_info)

        print(info_obj_list)
        df = pd.DataFrame(data=info_obj_list, columns=fields_names).set_index(fld_out_data_timestamp)
        measurement = 'stock-4'
        tags = ['stock_symbol']
        print(df)
        infdb.write_dataframe(df, measurement=measurement, tags=tags)
        append_current_status(info_obj_list, output_csv_file, fields_names)

        time.sleep(refresh_interval_sec)


def stock_info(pfl_avg_data, pull_id, pull_ts, ticker):
    # tmp_cur_stock_price_usd = fn.get_stock_price(ticker)
    tmp_cur_stock_price_usd = random.uniform(0, 3500)

    avg_obj = pfl_avg_data['stocks']['ticker' == ticker]
    tmp_pfl_total_shares = avg_obj['total_shares']
    tmp_pfl_avg_price_usd = avg_obj['avg_stock_price_usd']
    tmp_pfl_avg_rate_gbp_usd = avg_obj['avg_currency_gbp_to_usd']
    tmp_pfl_total_investment_usd = tbx.total_stocks_value(stocks_total=tmp_pfl_total_shares,
                                                          stock_price=tmp_pfl_avg_price_usd)
    tmp_pfl_total_investment_gbp = tbx.convert_currency_with_rate(
        amount=tmp_pfl_total_investment_usd,
        rate=tmp_pfl_avg_rate_gbp_usd)
    tmp_cur_price_change_percent = tbx.change_percentage(old_value=tmp_pfl_avg_price_usd,
                                                         new_value=tmp_cur_stock_price_usd)
    tmp_cur_total_value_usd = tbx.total_stocks_value(stock_price=tmp_cur_stock_price_usd,
                                                     stocks_total=tmp_pfl_total_shares)
    tmp_cur_total_value_gbp = tbx.convert_currency(amount=tmp_cur_total_value_usd,
                                                   from_currency='USD', to_currency='GBP')
    tmp_pfl_total_fx_fee_usd = tbx.transaction_fx_fee(amount=tmp_pfl_total_investment_usd)
    tmp_pfl_total_fx_fee_gbp = tbx.transaction_fx_fee(amount=tmp_pfl_total_investment_gbp)
    tmp_pfl_total_cost_gbp = tbx.transaction_cost_with_currency_conversion(total_shares=tmp_pfl_total_shares,
                                                                           stock_price=tmp_pfl_avg_price_usd,
                                                                           currency_rate=tmp_pfl_avg_rate_gbp_usd)

    tmp_cur_sell_fx_fee_gbp = tbx.transaction_fx_fee(tmp_cur_total_value_gbp)
    tmp_cur_total_value_after_fee_gbp = tmp_cur_total_value_gbp - tmp_cur_sell_fx_fee_gbp

    tmp_cur_sell_change_gbp = ''
    tmp_cur_sell_change_percent = ''
    tmp_cur_sell_balance_gbp = tmp_cur_total_value_after_fee_gbp - tmp_pfl_total_cost_gbp
    tmp_cur_sell_balance_percent = tbx.change_percentage(old_value=tmp_pfl_total_cost_gbp,
                                                         new_value=tmp_cur_total_value_after_fee_gbp)

    info = {
        # Id
        fld_out_data_pull_id: pull_id,
        fld_out_data_ticker: ticker,
        fld_out_data_timestamp: pull_ts,
        # Current
        fld_out_data_cur_stock_price_usd: tmp_cur_stock_price_usd,
        fld_out_data_cur_price_change_percent: tmp_cur_price_change_percent,
        fld_out_data_cur_total_value_usd: tmp_cur_total_value_usd,
        fld_out_data_cur_total_value_gbp: tmp_cur_total_value_gbp,
        fld_out_data_cur_total_value_after_fee_gbp: tmp_cur_total_value_after_fee_gbp,
        # Sell All
        fld_out_data_cur_sell_fx_fee_gbp: tmp_cur_sell_fx_fee_gbp,
        fld_out_data_cur_sell_pre_fee_change_gbp: tmp_cur_sell_change_gbp,
        fld_out_data_cur_sell_pre_fee_change_percent: tmp_cur_sell_change_percent,
        fld_out_data_cur_sell_balance_gbp: tmp_cur_sell_balance_gbp,
        fld_out_data_cur_sell_balance_percent: tmp_cur_sell_balance_percent,
        # AVG details
        fld_out_data_pfl_total_shares: tmp_pfl_total_shares,
        fld_out_data_pfl_avg_price_usd: tmp_pfl_avg_price_usd,
        fld_out_data_pfl_avg_rate_gbp_usd: tmp_pfl_avg_rate_gbp_usd,
        fld_out_data_pfl_total_investment_usd: tmp_pfl_total_investment_usd,
        fld_out_data_pfl_total_investment_gbp: tmp_pfl_total_investment_gbp,
        fld_out_data_pfl_total_fx_fee_usd: tmp_pfl_total_fx_fee_usd,
        fld_out_data_pfl_total_fx_fee_gbp: tmp_pfl_total_fx_fee_gbp,
        fld_out_data_pfl_total_cost_gbp: tmp_pfl_total_cost_gbp
    }
    return info


def main():
    # stockSymbolsList = ['AMZN', 'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'CRM', 'BABA', 'NIO', 'KO', 'F']
    stockSymbolsList = ['AMZN', 'AAPL', 'MSFT', 'GOOGL']

    # infdb.write_dataframe(output_data_csv)

    get_current_status(stock_symbol_list=stockSymbolsList,
                       portfolio_avg_file=portfolio_averages_data,
                       output_csv_file=output_data_csv,
                       fields_names=field_names)

# main()
