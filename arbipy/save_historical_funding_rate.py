# -*- coding: utf-8 -*-

import asyncio
import os
import csv
from pprint import pprint
import functools
from datetime import datetime, timedelta
import ccxt.async_support as ccxt  # noqa: E402

from utils import get_btcdom_index_info

root = os.path.dirname(os.path.abspath(__file__))
# ccxt unified symbol
btcdom_symbol = "BTCDOM/USDT"
btc_symbol = 'BTC/USDT'
# binance symbol
btcdom_index_symbol = "BTCDOMUSDT"

sample_days = 365

max_limit = 1000
eight_hours_ms = 8 * 60 * 60 * 1000


async def run():
    proxy_addr = 'sock5://localhost:7890'
    exchange = ccxt.binanceusdm({
        'aiohttp_proxy': proxy_addr
    })

    async def save_fr(symbol):
        now = datetime.now()
        start_time = now - timedelta(sample_days)
        start_ts = int(start_time.timestamp() * 1000)
        finish = False
        res = []
        while not finish:
            data = await exchange.fetch_funding_rate_history(symbol, start_ts, max_limit)
            res = res + data
            if len(data) < max_limit:
                finish = True
            else:
                start_ts = data[-1]['timestamp'] + eight_hours_ms  # last time + 1 hour
        print(symbol + ' fr history total: ' + str(len(res)))
        data = [[d['timestamp'], d['fundingRate'], d['datetime']] for d in res]
        write_fr_csv(data, symbol)
        return

    btcdom_index_info = await get_btcdom_index_info(exchange)

    # save assets klines
    for base_asset in btcdom_index_info['baseAssetList']:
        symbol = base_asset['quoteAsset'] + '/USDT'  # the ccxt unified symbol format
        await save_fr(symbol)

    await save_fr(btcdom_symbol)

    await save_fr(btc_symbol)

    await exchange.close()
    # return everything


def write_fr_csv(data, symbol):
    filename = symbol.replace('/', '_') + '_fr.csv'
    filename = os.path.join(root, '../fr_data', filename)
    fr_header = ['timestamp', 'funding_rate', 'datetime']
    with open(filename, 'w', encoding='UTF8') as file:
        writer = csv.writer(file)
        writer.writerow(fr_header)
        writer.writerows(data)


asyncio.run(run())
