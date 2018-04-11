import requests # pip install requests
import sys
import urllib
import http.client
import json
import hashlib
import hmac
import time
import requests

def sha512(key, data):
    H = hmac.new(key = key, digestmod = hashlib.sha512)
    H.update(data.encode('utf-8'))
    return H.hexdigest()

class EXMOPublic(object):
    """EXMO public api"""
    def __init__(self):
        super(EXMOPublic, self).__init__()
        self.API_URL = 'https://api.exmo.com/v1'
        self.name = 'Exmo'

    def ticker(self):
        response = requests.get(
            self.API_URL + '/ticker/'
        )
        
        return response.json()

    def trades(self, pair):
        response = requests.get(
            self.API_URL + '/trades/', 
            params = {
                'pair': pair
            }
        )
        
        return response.json()

    def order_book(self, pair, limit = 100):
        response = requests.get(
            self.API_URL + '/order_book/', 
            params = {
                'pair': pair, 
                'limit': limit
                }
        )
        
        return response.json()

    def pair_settings(self):
        response = requests.get(
            self.API_URL + '/pair_settings/'
        )
        
        return response.json()

    def currency(self):
        response = requests.get(
            self.API_URL + '/currency/'
        )
        
        return response.json()

class EXMOAuthenticated(object):
    """EXMO authenticated api"""
    def __init__(self, API_KEY, API_SECRET):
        super(EXMOAuthenticated, self).__init__()
        self.API_URL = 'api.exmo.com'
        self.API_VERSION = 'v1'
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')

    def __api_query(self, api_method, params = {}):

        params['nonce'] = int(round(time.time() * 1000))
        params =  urllib.parse.urlencode(params)
        
        sign = sha512(self.API_SECRET, params)
    
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Key": self.API_KEY,
            "Sign": sign
        }

        conn = http.client.HTTPSConnection(self.API_URL)
        
        conn.request("POST", "/" + self.API_VERSION + "/" + api_method, params, headers)
        response = conn.getresponse()
        response = response.read()

        conn.close()

        try:
            obj = json.loads(response.decode('utf-8'))
            if 'error' in obj and obj['error']:
                print(obj['error'], file = sys.stderr)
                sys.exit()
            return obj
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response, file = sys.stderr)
            sys.exit()

    def user_info(self):
        '''
            Метод получения информации об аккаунте пользователя

            Возращаемое значение:   
            {
                "uid": 00000,
                "server_date": 0000000000,
                "balances": {
                    "BTC": "000.000",
                    "USD": "000.00"
                },
                "reserved": {
                    "BTC": "0",
                    "USD": "0.0"
                }
            }
        '''
        return self.__api_query('user_info')
    
    def order_create(self, pair, quantity, price, order_type):
        '''
            Метод создания ордера

            Аргументы:    
                pair - валютная пара
                quantity - кол-во по ордеру
                price - цена по ордеру
                type - тип ордера, может принимать следующие значения:
                    buy - ордер на покупку
                    sell - ордер на продажу
                    market_buy - ордера на покупку по рынку
                    market_sell - ордер на продажу по рынку
                    market_buy_total - ордер на покупку по рынку на определенную сумму
                    market_sell_total - ордер на продажу по рынку на определенную сумму 
            Возвращаемое значение:
                {
                    "result": True / False,
                    "error": "" / "error text",
                    "order_id": 123456
                }
        '''
        return self.__api_query(
            'order_create', 
            {
                'pair': pair, 
                'quantity': quantity, 
                'price': price, 
                'type': order_type
            }
        )

    def order_cancel(self, order_id):
        '''
            Метод отмены ордера

            Входящие параметры:
                order_id - идентификатор ордера

            Возращаемое значение:   
            {
                "result": True / False,
                "error": "" / "error text"
            }
        '''
        return self.__api_query(
            'order_cancel', 
            {
                'order_id': order_id
            }
        )

    def user_open_orders(self):
        '''
            Метод получения списка открытых ордеров пользователя

            Возращаемое значение:   

            {
              "BTC_USD": [
                {
                  "order_id": "14",
                  "created": "1435517311",
                  "type": "buy",
                  "pair": "BTC_USD",
                  "price": "100",
                  "quantity": "1",
                  "amount": "100"
                }
              ]
            }
        '''
        return self.__api_query(
            'user_open_orders'
        )

    def user_trades(self, pair, offset = 0, limit = 100):
        '''
            Метод получения сделок пользователя

            Входящие параметры:
                pair - одна или несколько валютных пар разделенных запятой (пример BTC_USD,BTC_EUR)
                offset - смещение от последней сделки (по умолчанию 0)
                limit - кол-во возвращаемых сделок (по умолчанию 100, максимум 10 000)

            Возвращаемое значение:
                {
                  "BTC_USD": [
                    {
                      "trade_id": 3,
                      "date": 1435488248,
                      "type": "buy",
                      "pair": "BTC_USD",
                      "order_id": 7,
                      "quantity": 1,
                      "price": 100,
                      "amount": 100
                    }
                  ]
                }
        '''
        return self.__api_query(
            'user_trades', 
            {
                'pair': pair, 
                'offset': offset, 
                'limit': limit
            }
        )

    def user_cancelled_orders(self, offset = 0, limit = 100):
        '''
            Метод получения отмененных ордеров пользователя

            Входящие параметры:
                offset - смещение от последней сделки (по умолчанию 0)
                limit - кол-во возвращаемых сделок (по умолчанию 100, максимум 10 000)

            Возращаемое значение:   
                [
                  {
                    "date": 1435519742,
                    "order_id": 15,
                    "order_type": "sell",
                    "pair": "BTC_USD",
                    "price": 100,
                    "quantity": 3,
                    "amount": 300
                  }
                ]
        '''
        return self.__api_query(
            'user_cancelled_orders',
            {
                'offset': offset,
                'limit': limit
            }
        )

    def order_trades(self, order_id):
        '''
            Метод получения истории сделок ордера

            Входящие параметры:
                order_id - идентификатор ордера

            Возвращаемое значение:
                {
                  "type": "buy",
                  "in_currency": "BTC",
                  "in_amount": "1",
                  "out_currency": "USD",
                  "out_amount": "100",
                  "trades": [
                    {
                      "trade_id": 3,
                      "date": 1435488248,
                      "type": "buy",
                      "pair": "BTC_USD",
                      "order_id": 12345,
                      "quantity": 1,
                      "price": 100,
                      "amount": 100
                    }
                  ]
                }
        '''
        return self.__api_query(
            'order_trades', 
            {
                'order_id': order_id
            }
        )

    

    def required_amount(self, pair, quantity):
        '''
            Метод подсчета в какую сумму обойдется покупка определенного кол-ва валюты по конкретной валютной паре

            Входящие параметры:
                pair - валютная пара
                quantity - кол-во которое необходимо купить

            Возвращаемое значение:
                {
                  "quantity": 3,
                  "amount": 5,
                  "avg_price": 3.66666666
                }
        '''
        return self.__api_query(
            'required_amount',
            {
                'pair': pair, 
                'quantity': quantity
            }
        )

    def deposit_address(self):
        '''
            Метод получения списка адресов для депозита криптовалют

            Возвращаемое значение:
                {
                  "BTC": "16UM5DoeHkV7Eb7tMfXSuQ2ueir1yj4P7d",
                  "DOGE": "DEVfhgKErG5Nzas2FZJJH8Y8pjoLfVfWq4",
                  "LTC": "LSJFhsVJM6GCFtSgRj5hHuK9gReLhNuKFb",
                  "XRP": "rB2yjyFCoJaV8QCbj1UJzMnUnQJMrkhv3S,1234"
                }
        '''
        return self.__api_query(
            'deposit_address'
        )
