import concurrent.futures
import time

import admintools
import data_factory as df
import finnhub

stock_symbol = 'AAPL'
stockSymbolsList = ['AMZN', 'AAPL', 'MSFT', 'GOOGL']


def currency_exchange_agent(refresh_in_seconds):
    while True:
        admintools.clear()

        gbp_to_eur = str(finnhub.get_exchange_rate('GBP', 'EUR'))
        gbp_to_usd = str(finnhub.get_exchange_rate('GBP', 'USD'))
        eur_to_usd = str(finnhub.get_exchange_rate('EUR', 'USD'))

        print('GBP / EUR --> ', gbp_to_eur )
        print('GBP / USD --> ', gbp_to_usd )
        print('EUR / USD --> ', eur_to_usd )

        currency_info = {
            "GBP_to_EUR": gbp_to_eur,
            "GBP_to_USD": gbp_to_usd,
            "EUR_to_USD": eur_to_usd
        }
        print(currency_info)

        time.sleep(refresh_in_seconds)


def stock_list_agent(refresh_in_seconds, stocks_list):
    while True:
        admintools.clear()

        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            executor.map(finnhub.get_stock_price, stocks_list)

        time.sleep(refresh_in_seconds)


def main():
    print('main')

    # df.main()

    # currency_exchange_agent(5)

    # data_plot.main()


    # stock_list_agent(3, stockSymbolsList)

    # portfolio_stock_transactions_folder_file_path = 'stocks_files/'
    # portfolio_avg_file_path = 'support_files/portfolio_averages.json'
    # stockSymbolsList = ['msft', 'tsla']
    # df.calc_portfolio_averages(portfolio_stock_transactions_folder_file_path, stockSymbolsList,
    #                                      portfolio_avg_file_path)


if __name__ == "__main__":
    admintools.reset()

    main()
