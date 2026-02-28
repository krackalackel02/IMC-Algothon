import requests
from bot_template import BaseBot, Side
from main import place_single_order

EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
USERNAME = "PartyNextDoor"
PASSWORD = "pnd2026"

class SingleOrderBot(BaseBot):
    def on_orderbook(self, ob):
        pass
    def on_trades(self, trade):
        pass

if __name__ == "__main__":
    bot = SingleOrderBot(EXCHANGE_URL, USERNAME, PASSWORD)
    # Example: Place a BUY order for WX_SPOT at price 100.0, volume 1
    place_single_order(bot, product="WX_SPOT", price=100.0, side=Side.BUY, volume=1)
