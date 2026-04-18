import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Bachtbaaz Investment Dashboard", layout="wide")
st.title("📈 Bachtbaaz Investment Analytics")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Dashboard Parameters")
# Changed the default text to look cleaner without the .NS
raw_ticker = st.sidebar.text_input("Enter Indian Stock Ticker (e.g., RELIANCE, TCS, INFY)", "RELIANCE")

# THE MAGIC TRICK: Auto-format the ticker
ticker_symbol = raw_ticker.strip().upper() # Cleans up accidental spaces and makes it uppercase
if not ticker_symbol.endswith(".NS"):      # Checks if they forgot the .NS
    ticker_symbol = ticker_symbol + ".NS"  # Silently adds it!

# --- TABS ---
tab1, tab2 = st.tabs(["Stock & EPS Analysis", "SIP Calculator"])

with tab1:
    st.subheader(f"Real-Time Data for {ticker_symbol}")
    
    try:
        # Simply ask for the ticker - yfinance handles the disguise internally now!
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1y")
        
        # Check if Yahoo returned an empty dataset
        if hist.empty:
            st.warning(f"Yahoo Finance returned no data for {ticker_symbol}. It might be temporarily blocking the request.")
        else:
            # Try to get fundamental info (EPS), but don't crash if it fails
            try:
                info = stock.info
            except:
                info = {} # If it fails, just use an empty dictionary
            
            # Display Key Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"₹{hist['Close'].iloc[-1]:.2f}")
            col2.metric("Trailing EPS", info.get('trailingEps', 'Data Unavailable'))
            col3.metric("52-Week High", info.get('fiftyTwoWeekHigh', 'Data Unavailable'))
            
            # Plot interactive chart
            st.markdown("### 1-Year Price Trend")
            fig = go.Figure(data=[go.Candlestick(x=hist.index,
                            open=hist['Open'],
                            high=hist['High'],
                            low=hist['Low'],
                            close=hist['Close'])])
            fig.update_layout(xaxis_rangeslider_visible=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        # This will now print the EXACT error from Yahoo so we can debug it
        st.error(f"System Error: {e}")

with tab2:
    st.subheader("SIP Wealth Projections")
    
    col_sip1, col_sip2 = st.columns(2)
    with col_sip1:
        monthly_investment = st.number_input("Monthly SIP Amount (₹)", min_value=500, value=5000, step=500)
        years = st.slider("Investment Duration (Years)", 1, 30, 10)
    with col_sip2:
        expected_return = st.number_input("Expected Annual Return (%)", min_value=1.0, value=12.0, step=0.5)
    
    months = years * 12
    monthly_rate = (expected_return / 100) / 12
    future_value = monthly_investment * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
    total_invested = monthly_investment * months
    
    st.success(f"**Total Invested:** ₹{total_invested:,.2f}")
    st.success(f"**Estimated Future Value:** ₹{future_value:,.2f}")