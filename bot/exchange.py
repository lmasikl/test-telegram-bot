import datetime

import requests

from .exceptions import ExchangeException


class Singleton(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instance


class Cache(dict, metaclass=Singleton):

    def __init__(self, size=None):
        self.size = size

    def __setitem__(self, key, item):
        """
        Item (rate, datetime)
        Example (71.77, datetime.datetime(2020, 7, 28, 9, 48, 36))
        """
        assert isinstance(item, tuple)
        assert len(item) == 2
        if self.size and len(self) == self.size:
            oldest_pair = min(self.items(), key=lambda i: i[1][1])[0]
            self.pop(oldest_pair)

        super().__setitem__(key, item)

    def __getitem__(self, key):
        try:
            item = super().__getitem__(key)
        except KeyError:
            item = None

        if item is None:
            return None

        update_time = item[1]
        if (datetime.datetime.now() - update_time).seconds > 60 * 60:
            self.pop(key)
            return None

        return item


class Exchange(metaclass=Singleton):

    def __init__(self, cache_size=None):
        self.cache = Cache(size=cache_size)

    def make_deal(self, amount, from_, to):
        try:
            amount = float(amount)
        except ValueError:
            raise ExchangeException('Bab amount parameter')

        pair = self._make_pair((from_, to))
        rate = self.get_rate(pair)
        if rate is None:
            raise ExchangeException(f'Pair {"/".join(pair)} not found')

        if from_ == pair[0]:
            result = amount * rate
        else:
            result = amount / rate

        return result

    def _make_pair(self, pair):
        if pair[0].upper() == 'RUB' or pair[1].upper() == 'USD':
            return (pair[1], pair[0])

        return pair

    def get_rate(self, pair):
        rate = None
        if pair in self.cache.keys():
            rate = self.cache[pair][0]
        else:
            rate = self._get_from_stock(pair)
            if rate is not None:
                self.cache[pair] = (rate, datetime.datetime.now())

        return rate

    def _get_from_stock(self, pair):
        url = 'https://iss.moex.com/iss/statistics/engines/futures/markets/indicativerates/securities.json'
        response = requests.get(url)
        data = response.json()['securities']['data']
        pair = '/'.join(pair)
        for tradedate, tradetime, secid, rate in data:
            if secid == pair:
                return rate
        return None
