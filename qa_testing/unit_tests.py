import configparser
import logging

import finnhub

config = configparser.ConfigParser()

config.read('configs/config_sec.ini')
api_key = config['finnhub']['ApiToken']


def TEST_get_stock_price():
    stock_symbol = 'AMZN'

    rsp = finnhub.get_stock_price(stock_symbol)

    logging.info(rsp)

    if rsp <= 0 and not rsp:
        logging.error("Stock symbol all capital: FAIL")
    else:
        logging.info("Stock symbol all capital: SUCCESS")

    rsp = finnhub.get_stock_price(stock_symbol.lower())
    logging.info(rsp)

    if rsp <= 0 and not rsp:
        logging.error("Stock symbol all lowercase: FAIL")
    else:
        logging.info("Stock symbol all lowercase: SUCCESS")


def run_finnhub_tests():
    TEST_get_stock_price()


def main():
    logging_format = "%(asctime)s: %(message)s"
    # logging_format = "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
    # logging_format = "%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(name)s | %(message)s"

    # logging.basicConfig(handlers=[logging.FileHandler(all_logs_file_path),logging.StreamHandler()], format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")

    run_finnhub_tests()


main()