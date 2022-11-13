# -*- coding: utf-8 -*-

import asyncio
import os
from datetime import datetime, timedelta
import csv

import ccxt.async_support as ccxt  # noqa: E402

from utils import get_btcdom_index_info, ts

root = os.path.dirname(os.path.abspath(__file__))
# ccxt unified symbol
btcdom_symbol = "BTCDOM/USDT"
btc_symbol = 'BTC/USDT'
# binance symbol
btcdom_index_symbol = "BTCDOMUSDT"

# the number of funding rate data points, change this to sample different time ranges, funding rate occurs every 8
# hours, so 3 data points for 1 day

sample_days = 365

max_limit = 1000
one_hour_ms = 60 * 60 * 1000


# total_data_points = sample_days * 24  # 24 hours a day


async def run():
    proxy_addr = 'sock5://localhost:7890'
    binance_spot = ccxt.binance({
        'aiohttp_proxy': proxy_addr
    })
    exchange = ccxt.binanceusdm({
        'aiohttp_proxy': proxy_addr
    })

    # btcdom_info = await get_btcdom_index_info(exchange)
    async def save_klines(symbol):
        now = datetime.now()
        start_time = now - timedelta(sample_days)
        start_ts = ts(start_time)
        finish = False
        res = []
        while not finish:
            try:
                data = await binance_spot.fetch_ohlcv(symbol, '1h', start_ts, max_limit)
                res = res + data
                if len(data) < max_limit:
                    finish = True
                else:
                    start_ts = data[-1][0] + one_hour_ms  # last time + 1 hour
            except ccxt.errors.BadSymbol:
                finish = True
        print(symbol + ' klines total: ' + str(len(res)))
        if len(res) > 0:
            write_klines_csv(res, symbol)
        return

    # now_timestamp = int(datetime.now().timestamp() * 1000)
    btcdom_index_info = await get_btcdom_index_info(exchange)

    # save assets klines
    for base_asset in btcdom_index_info['baseAssetList']:
        symbol = base_asset['quoteAsset'] + '/BTC'  # the ccxt unified symbol format
        await save_klines(symbol)

    # await save_klines(btcdom_symbol)
    await save_klines(btc_symbol)
    # # btc_klines = await query_klines(btc_symbol)
    # write_klines_csv(btcdom_klines, btcdom_symbol)
    # pprint(len(btcdom_klines))
    await exchange.close()
    await binance_spot.close()
    # return everything


def write_klines_csv(data, symbol):
    filename = symbol.replace('/', '_') + '_klines.csv'
    filename = os.path.join(root, '../btc_based_klines_data', filename)
    klines_header = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    with open(filename, 'w', encoding='UTF8') as file:
        writer = csv.writer(file)
        writer.writerow(klines_header)
        writer.writerows(data)



asyncio.run(run())
