import configparser
from itertools import count

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.animation import FuncAnimation

config = configparser.ConfigParser()

config.read('configs/config.ini')

output_csv = config['FilePaths']['OutputData']

plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []

index = count()


def animate(i):
    data = pd.read_csv(output_csv)
    # x = data['timestamp']
    x = data['date_utc']
    y1 = data['price']
    # y2 = data['total_2']

    plt.cla()

    # ax = plt.gca()
    # # datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # formatter = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    # ax.xaxis.set_major_formatter(formatter)

    plt.plot(x, y1, label='Apple')
    # plt.plot(x, y2, label='Channel 2')

    plt.legend(loc='upper left')
    plt.tight_layout()


def main_1():
    ani = FuncAnimation(plt.gcf(), animate, interval=1000)
    plt.tight_layout()
    plt.show()

    # dates = ["01/02/2020", "01/03/2020", "01/04/2020"]
    # x_values = [datetime.datetime.strptime(d,"%m/%d/%Y").date() for d in dates]


def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'] + .02, point['y'], str(point['val']))


def main():
    data = pd.read_csv(output_csv)
    print(data)
    # data_amzn = data[data.stock_symbol == 'AMZN']
    # print(data_amzn)
    #
    # data_aapl = data[data.stock_symbol == 'AAPL']
    # print(data_aapl)

    unique = data.stock_symbol.unique()
    # print(unique)

    # x = data['timestamp']
    # y1 = data['price']

    # Clear current axis
    # plt.cla()

    # # # Get current axis
    # # # ax = plt.gca()
    # # # # datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # # # formatter = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    # # # ax.xaxis.set_major_formatter(formatter)
    #
    # plt.plot(x, y1, label='Apple')
    # # plt.plot(x, y2, label='Channel 2')

    # plt.plot(data_amzn['price'], label="AMZN")
    # # label_point(data_amzn.timestamp, data_amzn.price, data_amzn.price, plt.gca())
    #
    # plt.plot(data_baba['price'], label="BABA")

    # =======================================
    # Seaborn lmplot()
    # sns.set_theme(color_codes=True)
    # g = sns.lmplot(x="timestamp", y="price", data=data,
    g = sns.lmplot(x="timestamp", y="current_sell_balance_gbp",
                   data=data,
                   hue="stock_symbol",
                   col='stock_symbol',
                   col_wrap=2,
                   height=3,
                   legend_out=True,
                   sharey=False,
                   scatter=True
                   )

    # label_point(data.timestamp, data.price, data.price, plt.gca())

    # ========================================
    # Seaborn relplot()
    # g = sns.relplot(x="timestamp", y="price", data=data,
    #                 hue="stock_symbol",
    #                 kind="line",
    #                 col='stock_symbol',
    #                 col_wrap=4,
    #                 height=3,
    #                 legend_out=True
    #                 )

    # g.fig.autofmt_xdate()

    # plt.xticks(rotation=90)
    # plt.legend(loc='lower right')
    # plt.tight_layout()
    # plt.gcf()
    plt.show()
