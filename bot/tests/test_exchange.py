import datetime

from bot.exchange import Cache, Exchange


def test_cache():
    now = datetime.datetime.now()
    cache = Cache(size=2)
    assert len(cache) == 0
    cache[('USD', 'RUB')] = (1, now)
    assert len(cache) == 1
    cache[('USD'), ('CHF')] = (2, now)
    assert len(cache) == 2
    cache[('USD'), ('CAD')] = (3, now)
    assert len(cache) == 2
    assert cache[('USD', 'RUB')] is None
    assert cache[('USD'), ('CHF')] == (2, now)


def test_exchange():
    exchange = Exchange()

    amount = 10
    result = exchange.make_deal(10, 'USD', 'RUB')
    assert result > amount

    amount = 10
    result = exchange.make_deal(10, 'RUB', 'USD')
    assert result < amount
