import os
from dotenv import load_dotenv  # Load key(s) securely from .env
from elevenlabs import ElevenLabs
import yfinance as yf
import time

load_dotenv() # load variables from .env

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Track stocks
symbols_to_track = ["AAPL", "TSLA", "GOOGL"]

threshold = 0 

# Fetch price
def get_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1h")  # hourly intervals

        if data.empty:
            print(f"No price data found for {symbol}")
            return None

        latest_price = data["Close"].iloc[-1]
        return round(latest_price, 2)

    except Exception as e:
        print(f" Error fetching price for {symbol}: {e}")
        return None

# Generate voice alert 
def trigger_multi_stock_voice_alert(prices: dict, voice: str = "Rachel"):

    if not prices:
        print("No prices to announce.")
        return

    message = "Stock update: "
    for symbol, price in prices.items():
        message += f"{symbol} is currently trading at {price} dollars. "

    print("Generating voice alert:", message)

    audio_stream = client.generate(
        text=message,
        voice=voice,
        model="eleven_monolingual_v1",
        stream=True,
    )

    with open("multi_stock_alert.mp3", "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    print("Voice alert saved as multi_stock_alert.mp3")

# alert check
def run_alert_check():

    stock_prices = {}

    for symbol in symbols_to_track:
        price = get_stock_price(symbol.upper())
        if price:
            stock_prices[symbol] = round(price, 2)

    if stock_prices:
        if threshold > 0:
            for symbol, price in stock_prices.items():
                if price < threshold:
                    trigger_multi_stock_voice_alert(stock_prices)
                    break
        else:
            trigger_multi_stock_voice_alert(stock_prices)

# Run manually
if __name__ == "__main__":
    run_alert_check()

    time.sleep(600)  # 10 minutes wait time
