# ccxt unified symbol
BTCDOM_SYMBOL = "BTCDOM/USDT"
BTC_SYMBOL = 'BTC/USDT'
# binance symbol
BTCDOM_INDEX_SYMBOL = "BTCDOMUSDT"


async def get_btcdom_index_info(exchange):
    infos = await exchange.fapiPublic_get_indexinfo()
    # pprint(infos)
    btcdom_list = [info for info in infos if info['symbol'] == BTCDOM_INDEX_SYMBOL]
    if len(btcdom_list) != 1:
        raise Exception('cannot find ' + BTCDOM_INDEX_SYMBOL + 'index')
    return btcdom_list[0]


def ts(dtime):
    return int(dtime.timestamp() * 1000)


def table(values):
    first = values[0]
    keys = list(first.keys()) if isinstance(first, dict) else range(0, len(first))
    widths = [max([len(str(v[k])) for v in values]) for k in keys]
    string = ' | '.join(['{:<' + str(w) + '}' for w in widths])
    return "\n".join([string.format(*[str(v[k]) for k in keys]) for v in values])