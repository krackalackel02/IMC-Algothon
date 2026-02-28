import requests
from bot_template import BaseBot

EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
USERNAME = "PartyNextDoor"
PASSWORD = "pnd2026"

class CancelBot(BaseBot):
    def on_orderbook(self, ob):
        pass
    def on_trades(self, trade):
        pass

if __name__ == "__main__":
    bot = CancelBot(EXCHANGE_URL, USERNAME, PASSWORD)
    print("Cancelling all orders...")
    bot.cancel_all_orders()
    print("All orders cancelled.")
