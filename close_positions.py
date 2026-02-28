import requests
from bot_template import BaseBot, OrderRequest, Side
from main import close_all_positions

EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
USERNAME = "PartyNextDoor"
PASSWORD = "pnd2026"

class ClosePositionsBot(BaseBot):
    def on_orderbook(self, ob):
        pass
    def on_trades(self, trade):
        pass

if __name__ == "__main__":
    bot = ClosePositionsBot(EXCHANGE_URL, USERNAME, PASSWORD)
    close_all_positions(bot)
