import json

import aiohttp
import requests

import config

session = aiohttp.ClientSession()


def get_ip() -> str:
    r = requests.get('http://ifconfig.me')
    r.text.replace('\n', '')
    return r.text


async def convert(amount: float, from_currency: str, to_currency: str = 'RUB') -> float:
    if from_currency != to_currency:
        pair = (from_currency + to_currency).upper()
        params = {
            'key':   config.currency_api_key,
            'get':   'rates',
            'pairs': pair
        }
        async with session.get(url='https://currate.ru/api/', params=params) as resp:
            r = json.loads(await resp.text())
            res = float(r['data'][pair]) * amount
            return res
    else:
        return amount
