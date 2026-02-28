from bot_template import BaseBot, OrderBook, OrderRequest, Side
import time
import numpy as np

# Simple Market Making Bot
class LiquidityProviderBot(BaseBot):
    def __init__(self, *args, spread=5, size=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.spread = spread  # ticks away from mid
        self.size = size
        self.active_products = []

    def on_orderbook(self, ob: OrderBook):
        if not ob.buy_orders or not ob.sell_orders:
            return
        mid = (ob.buy_orders[0].price + ob.sell_orders[0].price) / 2
        bid = mid - self.spread
        ask = mid + self.spread
        # Cancel all previous orders
        self.cancel_all_orders()
        # Place new two-sided quotes
        self.send_orders([
            OrderRequest(ob.product, bid, Side.BUY, self.size),
            OrderRequest(ob.product, ask, Side.SELL, self.size)
        ])

    def on_trades(self, trade):
        pass  # Could log or update inventory

# Simple Trader Bot (momentum: buy if price rising, sell if falling)
class TraderBot(BaseBot):
    def __init__(self, *args, lookback=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookback = lookback
        self.last_prices = {}

    def on_orderbook(self, ob: OrderBook):
        if not ob.buy_orders or not ob.sell_orders:
            return
        mid = (ob.buy_orders[0].price + ob.sell_orders[0].price) / 2
        prices = self.last_prices.setdefault(ob.product, [])
        prices.append(mid)
        if len(prices) > self.lookback:
            prices.pop(0)
        if len(prices) == self.lookback:
            if prices[-1] > prices[0]:
                # Uptrend: buy
                self.send_order(OrderRequest(ob.product, ob.sell_orders[0].price, Side.BUY, 1))
            elif prices[-1] < prices[0]:
                # Downtrend: sell
                self.send_order(OrderRequest(ob.product, ob.buy_orders[0].price, Side.SELL, 1))

    def on_trades(self, trade):
        pass

# Example usage (uncomment to run)
# EXCHANGE_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
# USERNAME = "PartyNextDoor"
# PASSWORD = "pnd2026"
# bot = LiquidityProviderBot(EXCHANGE_URL, USERNAME, PASSWORD)
# bot.start()
# time.sleep(60)
# bot.stop()
