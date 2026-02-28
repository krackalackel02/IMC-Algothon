import requests
from bot_template import BaseBot, OrderRequest, Side

EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
USERNAME = "PartyNextDoor"
PASSWORD = "pnd2026"

class CloseOnePositionBot(BaseBot):
    def on_orderbook(self, ob):
        pass
    def on_trades(self, trade):
        pass

def close_one_position(bot):
    positions = bot.get_positions()
    products = bot.get_products()
    for product, pos in positions.items():
        if pos == 0:
            continue
        ob = bot.get_orderbook(product)
        if pos > 0 and ob.sell_orders:
            price = ob.sell_orders[0].price
            print(f"Closing long {pos} {product} at {price}")
            bot.send_order(OrderRequest(product, price, Side.SELL, abs(pos)))
            return
        elif pos < 0 and ob.buy_orders:
            price = ob.buy_orders[0].price
            print(f"Closing short {abs(pos)} {product} at {price}")
            bot.send_order(OrderRequest(product, price, Side.BUY, abs(pos)))
            return
    print("No open positions to close.")

if __name__ == "__main__":
    bot = CloseOnePositionBot(EXCHANGE_URL, USERNAME, PASSWORD)
    close_one_position(bot)
