import requests
from bot_template import BaseBot
from main import print_active_orders

EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
USERNAME = "PartyNextDoor"
PASSWORD = "pnd2026"

class PrintOrdersBot(BaseBot):
    def on_orderbook(self, ob):
        pass
    def on_trades(self, trade):
        pass

if __name__ == "__main__":
    bot = PrintOrdersBot(EXCHANGE_URL, USERNAME, PASSWORD)
    print_active_orders(bot)
