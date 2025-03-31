import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from index import get_stock_price, trigger_multi_stock_voice_alert

# Page setup
st.set_page_config(page_title="Voice-Based Stock Alert")
st.title("Voice-Based Stock Alerts")
st.markdown("Enter one or more stock symbols for stock voice alert.")

# User input
symbols_input = st.text_input(
    "Enter stock symbols separated by commas (e.g. AAPL, TSLA, GOOGL):",
    value="AAPL, TSLA",
)

voice_choice = st.selectbox(
    "Select a voice for your alert:",
    options=["Rachel", "Bella", "Domi", "Antoni", "Elli"],
    index=0,
)

threshold = st.slider(
    "Trigger alert if stock is below this price (set 0 to disable):",
    min_value=0,
    max_value=1000,
    value=0,
    step=10,
)

trigger = st.button("Generate Voice Update")

# Trigger Voice Alert
if trigger:
    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    if not symbols:
        st.warning("Please enter at least one valid stock symbol.")
    else:
        st.info("Fetching prices...")
        prices = {}
        price_data = {}

        for symbol in symbols:
            price = get_stock_price(symbol)
            if price is not None:
                prices[symbol] = price
                st.write(f"{symbol} is trading at ${price}")

                # Fetch historical data
                history = yf.Ticker(symbol).history(period="7d", interval="1h")
                if not history.empty:
                    price_data[symbol] = history
            else:
                st.error(f"Could not fetch data for {symbol}")

        # Plot combined chart
        if price_data:
            st.subheader("7-Day Price Chart (Combined)")
            fig = go.Figure()
            for symbol, df in price_data.items():
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df["Close"],
                    mode="lines",
                    name=symbol
                ))
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                legend_title="Stock Symbol"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Generate Voice Alert
        if prices:
            if threshold > 0:
                below_threshold = {s: p for s, p in prices.items() if p < threshold}
                if below_threshold:
                    st.success("Threshold triggered. Generating voice alert.")
                    trigger_multi_stock_voice_alert(below_threshold, voice=voice_choice)
                    st.audio("multi_stock_alert.mp3", format="audio/mp3")
                else:
                    st.info("No stocks are below the threshold.")
            else:
                st.success("Generating voice alert for all stocks.")
                trigger_multi_stock_voice_alert(prices, voice=voice_choice)
                st.audio("multi_stock_alert.mp3", format="audio/mp3")
