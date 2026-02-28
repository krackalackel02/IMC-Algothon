import requests
from bot_template import BaseBot

EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
USERNAME = "PartyNextDoor"
PASSWORD = "pnd2026"

class PrintPositionsBot(BaseBot):
    def on_orderbook(self, ob):
        pass
    def on_trades(self, trade):
        pass

if __name__ == "__main__":
    bot = PrintPositionsBot(EXCHANGE_URL, USERNAME, PASSWORD)
    positions = bot.get_positions()
    if not positions:
        print("No open positions.")
    else:
        print("Open positions:")
        for product, pos in positions.items():
            print(f"  {product}: {pos:+d}")
