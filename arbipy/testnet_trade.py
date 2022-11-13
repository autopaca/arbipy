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
    markets = await exchange.load_markets()

    balance = await exchange.fetch_balance()
    usdt_balance = balance['USDT']['free']

    btcdom_index_info = await get_btcdom_index_info(exchange)
    btcdom_init_capital, btc_init_capital, assets_init_capital = capital_each_leg, capital_each_leg, capital_each_leg
    base_asset_symbols = []
    for base_asset in btcdom_index_info['baseAssetList']:
        base_quote_asset = base_asset['quoteAsset']
        if base_quote_asset == 'ICP':
            symbol = base_quote_asset + '/BUSD'
        else:
            symbol = base_quote_asset + '/USDT'  # the ccxt unified symbol format
        base_asset_symbols.append(symbol)

    tickers = await exchange.fetch_tickers(base_asset_symbols + [BTCDOM_SYMBOL, BTC_SYMBOL])
    for i, base_asset_symbol in enumerate(base_asset_symbols):
        base_asset = btcdom_index_info['baseAssetList'][i]
        weight = float(base_asset['weightInPercentage'])
        capital = assets_init_capital * weight
        await make_order(exchange, base_asset_symbol, 'sell', capital, tickers, markets)

    # short btcdom
    await make_order(exchange, BTCDOM_SYMBOL, 'sell', btcdom_init_capital, tickers, markets)
    await make_order(exchange, BTC_SYMBOL, 'buy', btcdom_init_capital, tickers, markets)
    pprint({
        # 'markets': markets,
        'usdt_balance': usdt_balance
    })

    await exchange.close()


async def make_order(exchange, symbol, side, capital, tickers, markets):
    last = tickers[symbol]['last']
    market = markets[symbol]
    quantity_precision = market['precision']['amount']
    amount = round(capital / last, quantity_precision)
    origin_amount = amount
    min_notional = market['limits']['cost']['min']  # same limits for order cost = price * amount
    min_amount = market['limits']['amount']['min']  # same limits for order cost = price * amount
    if amount < min_amount:
        amount = min_amount
    if amount * last < min_notional:
        amount = round(min_notional / last + 1, quantity_precision)
    try:
        await exchange.set_leverage(20, symbol)
        order = await exchange.create_market_order(symbol, side, amount)
        pprint({
            'symbol': symbol,
            'last': last,
            'quantity_precision': quantity_precision,
            'origin_amount': origin_amount,
            'position_amount': amount,
            'min_amount': min_amount,
            'capital': capital,
            'order_amount': order['amount'],
            'order_price': order['price'],
            'order_cost': order['cost']
        })
        return order
    except Exception as e:
        print('open position error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        pprint({
            'error': e,
            'symbol': symbol,
            'last': last,
            'min_amount': min_amount,
            'quantity_precision': quantity_precision,
            'origin_amount': origin_amount,
            'position_amount': amount,
            'capital': capital,
        })


asyncio.run(run())
