def close_all_positions(bot):
    """Close all active positions by sending market orders to flatten each position."""
    positions = bot.get_positions()
    products = bot.get_products()
    product_tick = {p.symbol: p.tickSize for p in products}
    for product, pos in positions.items():
        if pos == 0:
            continue
        # Get the latest orderbook to find the best price
        ob = bot.get_orderbook(product)
        if pos > 0 and ob.sell_orders:
            # Sell to flatten long
            price = ob.sell_orders[0].price
            print(f"Closing long {pos} {product} at {price}")
            bot.send_order(OrderRequest(product, price, Side.SELL, abs(pos)))
        elif pos < 0 and ob.buy_orders:
            # Buy to flatten short
            price = ob.buy_orders[0].price
            print(f"Closing short {abs(pos)} {product} at {price}")
            bot.send_order(OrderRequest(product, price, Side.BUY, abs(pos)))
    print("All positions close orders sent.")
def place_single_order(bot, product, price, side, volume=1):
    """Place a single open order for a given instrument at a specified price and volume."""
    from bot_template import OrderRequest, Side
    order = OrderRequest(product=product, price=price, side=side, volume=volume)
    resp = bot.send_order(order)
    if resp:
        print(f"Order placed: {resp}")
    else:
        print("Order failed.")
def print_active_orders(bot):
    orders = bot.get_orders()
    if not orders:
        print("No active orders.")
        return
    print(f"{len(orders)} active orders:")
    for o in orders:
        print(f"  {o['id'][:8]}  {o['side']:>4} {o['volume']}@{o['price']}  {o['product']}")
import time
from bot_template import BaseBot, OrderBook, OrderRequest, Side
import pandas as pd
import math

# Weather data helper (from notebook)
LONDON_LAT, LONDON_LON = 51.5074, -0.1278

def get_weather(past_steps=96, forecast_steps=96):
    variables = "temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,wind_speed_10m,cloud_cover,visibility"
    resp = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": LONDON_LAT, "longitude": LONDON_LON,
        "minutely_15": variables,
        "past_minutely_15": past_steps,
        "forecast_minutely_15": forecast_steps,
        "timezone": "Europe/London",
    })
    resp.raise_for_status()
    m = resp.json()["minutely_15"]
    return pd.DataFrame({
        "time": pd.to_datetime(m["time"]).tz_localize("Europe/London"),
        "temperature": m["temperature_2m"],
        "apparent_temperature": m["apparent_temperature"],
        "humidity": m["relative_humidity_2m"],
        "precipitation": m["precipitation"],
        "wind_speed": m["wind_speed_10m"],
        "cloud_cover": m["cloud_cover"],
        "visibility": m["visibility"],
    })

class WeatherQuoterBot(BaseBot):
    """Market making bot that biases WX_SPOT quotes using weather data."""
    def on_orderbook(self, ob: OrderBook):
        pass  # Not used in this bot
    def on_trades(self, trade):
        print(f"Trade: {trade.product} {trade.volume}@{trade.price}")
    def run_loop(self, width=5.0, volume=5, interval=5):
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        products = {p.symbol: p for p in self.get_products()}
        self.start()
        while True:
            self.cancel_all_orders()
            try:
                df_weather = get_weather()
                last = df_weather.iloc[-1]
                temp_F = last['temperature'] * 9/5 + 32
                humidity = last['humidity']
                wx_spot_est = temp_F * humidity
                logging.info(f"Weather: temp_F={temp_F:.2f}, humidity={humidity:.2f}, WX_SPOT estimate={wx_spot_est:.2f}")
            except Exception as e:
                wx_spot_est = None
                logging.warning(f"Weather fetch failed: {e}")
            for symbol, product in products.items():
                ob = self.get_orderbook(symbol)
                bids = [o.price for o in ob.buy_orders if o.volume - o.own_volume > 0]
                asks = [o.price for o in ob.sell_orders if o.volume - o.own_volume > 0]
                mid = (max(bids) + min(asks)) / 2 if bids and asks else product.startingPrice
                tick = product.tickSize
                bid = math.floor((mid - width) / tick) * tick
                ask = math.ceil((mid + width) / tick) * tick
                if symbol == "WX_SPOT" and wx_spot_est is not None:
                    if mid < wx_spot_est:
                        bid += tick
                    elif mid > wx_spot_est:
                        ask -= tick
                if bid > 0 and bid < ask:
                    logging.info(f"Placing orders for {symbol}: BUY {volume}@{bid}, SELL {volume}@{ask} (mid={mid:.2f})")
                    responses = self.send_orders([
                        OrderRequest(symbol, bid, Side.BUY, volume),
                        OrderRequest(symbol, ask, Side.SELL, volume),
                    ])
                    for resp in responses:
                        logging.info(f"OrderResponse: {resp}")
            time.sleep(interval)

import threading
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class BotGUI:
    def __init__(self, bot):
        self.bot = bot
        self.root = tk.Tk()
        self.root.title("WeatherQuoterBot Visualizer")
        self.log_queue = queue.Queue()

        self.text = ScrolledText(self.root, width=100, height=30, state='disabled', font=("Consolas", 10))
        self.text.pack(padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 12, "bold"))
        self.status_label.pack(pady=(0,10))

        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, msg):
        self.log_queue.put(msg)

    def update_log(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.text.config(state='normal')
            self.text.insert(tk.END, msg + "\n")
            self.text.see(tk.END)
            self.text.config(state='disabled')
        if self.running:
            self.root.after(200, self.update_log)

    def set_status(self, msg):
        self.status_var.set(msg)

    def on_close(self):
        self.running = False
        if self.bot:
            self.bot.cancel_all_orders()
            self.bot.stop()
        self.root.destroy()

    def run(self):
        self.update_log()
        self.root.mainloop()

class GUIMarketBot(WeatherQuoterBot):
    def __init__(self, *args, gui=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gui = gui

    def run_loop(self, width=5.0, volume=5, interval=5):
        products = {p.symbol: p for p in self.get_products()}
        self.start()
        while self.gui is None or self.gui.running:
            self.cancel_all_orders()
            try:
                df_weather = get_weather()
                last = df_weather.iloc[-1]
                temp_F = last['temperature'] * 9/5 + 32
                humidity = last['humidity']
                wx_spot_est = temp_F * humidity
                msg = f"Weather: temp_F={temp_F:.2f}, humidity={humidity:.2f}, WX_SPOT estimate={wx_spot_est:.2f}"
                if self.gui:
                    self.gui.log(msg)
                    self.gui.set_status(f"WX_SPOT estimate: {wx_spot_est:.2f}")
                else:
                    print(msg)
            except Exception as e:
                wx_spot_est = None
                msg = f"Weather fetch failed: {e}"
                if self.gui:
                    self.gui.log(msg)
                else:
                    print(msg)
            for symbol, product in products.items():
                ob = self.get_orderbook(symbol)
                bids = [o.price for o in ob.buy_orders if o.volume - o.own_volume > 0]
                asks = [o.price for o in ob.sell_orders if o.volume - o.own_volume > 0]
                mid = (max(bids) + min(asks)) / 2 if bids and asks else product.startingPrice
                tick = product.tickSize
                bid = math.floor((mid - width) / tick) * tick
                ask = math.ceil((mid + width) / tick) * tick
                if symbol == "WX_SPOT" and wx_spot_est is not None:
                    if mid < wx_spot_est:
                        bid += tick
                    elif mid > wx_spot_est:
                        ask -= tick
                if bid > 0 and bid < ask:
                    msg = f"Placing orders for {symbol}: BUY {volume}@{bid}, SELL {volume}@{ask} (mid={mid:.2f})"
                    if self.gui:
                        self.gui.log(msg)
                    else:
                        print(msg)
                    responses = self.send_orders([
                        OrderRequest(symbol, bid, Side.BUY, volume),
                        OrderRequest(symbol, ask, Side.SELL, volume),
                    ])
                    for resp in responses:
                        msg = f"OrderResponse: {resp}"
                        if self.gui:
                            self.gui.log(msg)
                        else:
                            print(msg)
            time.sleep(interval)

if __name__ == "__main__":
    import requests
    TEST_URL = "http://ec2-52-49-69-152.eu-west-1.compute.amazonaws.com/"
    EXCHANGE_URL = TEST_URL
    USERNAME = "PartyNextDoor"
    PASSWORD = "pnd2026"
    gui = BotGUI(None)
    bot = GUIMarketBot(EXCHANGE_URL, USERNAME, PASSWORD, gui=gui)
    gui.bot = bot
    t = threading.Thread(target=bot.run_loop, kwargs={"width":5, "volume":5, "interval":5}, daemon=True)
    t.start()
    gui.run()
