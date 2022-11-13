# -*- coding: utf-8 -*-

import asyncio
import os
import csv
from pprint import pprint

import ccxt.async_support as ccxt  # noqa: E402

from utils import get_btcdom_index_info, BTC_SYMBOL, BTCDOM_SYMBOL

root = os.path.dirname(os.path.abspath(__file__))

capital_each_leg = 10000.0

last_n_hours = 24 * 30


async def run():
    proxy_addr = 'sock5://localhost:7890'
    exchange = ccxt.binanceusdm({
        'aiohttp_proxy': proxy_addr
    })
    btcdom_index_info = await get_btcdom_index_info(exchange)
    btc_klines = read_kline_data(BTC_SYMBOL)
    btcdom_klines = read_kline_data(BTCDOM_SYMBOL)

    btcdom_init_capital, btc_init_capital, assets_init_capital = capital_each_leg, 0.95 * capital_each_leg, 1.05 * capital_each_leg
    total_init_capital = btcdom_init_capital + btc_init_capital + assets_init_capital
    btc_position, btc_capital = position_and_end_capital(btc_klines, btc_init_capital)
    btcdom_position, btcdom_capital = position_and_end_capital(btcdom_klines, btcdom_init_capital)

    assets_position, assets_capital = 0, 0
    for base_asset in btcdom_index_info['baseAssetList']:
        symbol = base_asset['quoteAsset'] + '/USDT'  # the ccxt unified symbol format
        asset_klines = read_kline_data(symbol)
        # assets_klines.append(read_kline_data(symbol))
        weight = float(base_asset['weightInPercentage'])
        capital = assets_init_capital * weight
        asset_position, asset_capital = position_and_end_capital(asset_klines, capital)
        assets_position += asset_position
        assets_capital += asset_capital
        # print(symbol + ' position: ' + str(asset_position) + ' | ' + symbol + ' end capital: ' + str(asset_capital))

    # short btcdom(short btc long assets), long btc, short assets
    btcdom_pnl = btcdom_init_capital - btcdom_capital
    btc_pnl = btc_capital - btc_init_capital
    assets_pnl = assets_init_capital - assets_capital

    print(
        'short btcdom | init capital: ' + str(btcdom_init_capital) + ' | btcdom position: ' + str(
            btcdom_position) + ' | btcdom end capital: ' + str(
            btcdom_capital) + ' | pnl: ' + str(
            btcdom_pnl))
    print(
        'long btc | init capital: ' + str(btc_init_capital) + ' | btc position: ' + str(
            btc_position) + ' | btc end capital: ' + str(btc_capital) + ' | pnl: ' + str(
            btc_pnl))
    print(
        'short assets | init capital: ' + str(assets_init_capital) + ' | assets position: ' + str(
            assets_position) + ' | assets end capital: ' + str(
            assets_capital) + ' | pnl: ' + str(
            assets_pnl))

    # short btcdom(short btc long assets), long btc, short assets
    pnl = btcdom_pnl + btc_pnl + assets_pnl
    fr_estimation = 0.15 / 365 / 24 * last_n_hours * 3 * total_init_capital
    print('total init capital: ' + str(total_init_capital) + ' total pnl: ' + str(
        pnl) + ' | estimated funding rate: ' + str(fr_estimation) + ' | ' + 'pnl + funding rate: ' + str(
        pnl + fr_estimation))
    await exchange.close()
    # return everything


def position_and_end_capital(klines, init_capital):
    start_price, end_price = start_end_price(klines)
    position = init_capital / start_price
    capital = position * end_price
    return position, capital


def start_end_price(klines):
    return float(klines[0][4]), float(klines[-1][4])


def read_kline_data(symbol):
    filename = symbol.replace('/', '_') + '_klines.csv'
    filename = os.path.join(root, '../klines_data', filename)
    with open(filename, encoding='UTF8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        return list(reader)[-last_n_hours::]


asyncio.run(run())
