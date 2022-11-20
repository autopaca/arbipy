# -*- coding: utf-8 -*-

import asyncio
import os
from pprint import pprint

import ccxt.async_support as ccxt  # noqa: E402

from utils import get_btcdom_index_info, BTC_SYMBOL, BTCDOM_SYMBOL

root = os.path.dirname(os.path.abspath(__file__))

API_KEY = '77ecb759150908d28b99590f8a76fe6bd6d3ff00ccab6aec55f1aa020521013f'
API_SECRET = '20d706473d0923d0fc919b6dc61ce1052494a818a2ea3bceba1c7d27ea0a3578'

capital_each_leg = 500.0


async def run():
    proxy_addr = 'sock5://localhost:7890'
    exchange = ccxt.binanceusdm({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'aiohttp_proxy': proxy_addr,
        'options': {
            'defaultType': 'future'
        }
    })
    exchange.set_sandbox_mode(True)
    spot_exchange = ccxt.binance({
        'aiohttp_proxy': proxy_addr,
    })
    markets = await spot_exchange.load_markets()
    pprint({
        'ETH': markets['ETH/USDT']
    })

    await spot_exchange.close()
    await exchange.close()


asyncio.run(run())
