# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from pprint import pprint
import functools

from utils import get_btcdom_index_info

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt.async_support as ccxt  # noqa: E402

# ccxt unified symbol
btcdom_symbol = "BTCDOM/USDT"
btc_symbol = 'BTC/USDT'
# binance symbol
btcdom_index_symbol = "BTCDOMUSDT"

# the number of funding rate data points, change this to sample different time ranges, funding rate occurs every 8
# hours, so 3 data points for 1 day
limit = 30


async def run():
    proxy_addr = 'sock5://localhost:7890'
    exchange = ccxt.binanceusdm({
        'aiohttp_proxy': proxy_addr
    })
    btcdom_info = await get_btcdom_index_info(exchange)

    assets_fr = await get_avg_weighted_fr(exchange, btcdom_info['baseAssetList'])
    btcdom_fr = await get_avg_fr(exchange, btcdom_symbol)

    btc_fr = await get_avg_fr(exchange, btc_symbol)

    # if FR is positive, long position pay short position; negative reversely
    final_fr = btcdom_fr + assets_fr - btc_fr  # short btcDom, short base assets, long btc
    apr = final_fr * 3 * 365 / 3  # funding rate is paid every 8 hours, total 3 legs
    pprint({
        'btcdom_fr': btcdom_fr,
        'assets_fr': assets_fr,
        'btc_fr': btc_fr,
        'final_fr': final_fr,
        'APR': apr,
        'sample_days': limit / 3
    })
    await exchange.close()
    # return everything


async def get_avg_weighted_fr(exchange, base_asset_list):
    res = 0
    for base_asset in base_asset_list:
        symbol = base_asset['quoteAsset'] + '/USDT'  # the ccxt unified symbol format
        res += (await get_avg_fr(exchange, symbol)) * float(base_asset['weightInPercentage'])
    return res


async def get_avg_fr(exchange, symbol):
    fr_infos = await get_fr_infos(exchange, symbol)
    avg = 100 * functools.reduce(lambda prev, cur: prev + cur['fundingRate'], fr_infos, 0) / len(fr_infos)
    print(symbol + 'average funding rate for ' + str(limit) + ' data points: ' + str(avg))
    return avg


async def get_fr_infos(exchange, symbol):
    fr_infos = await exchange.fetch_funding_rate_history(symbol, None, limit)
    if len(fr_infos) != limit:
        raise Exception('frInfos of ' + symbol + 'length ' + str(len(fr_infos)) + ' != ' + str(limit))
    return fr_infos


asyncio.run(run())
