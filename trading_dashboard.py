import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import data fetching module
from src.test_data_fetcher import get_data_for_dashboard

# Plotting function
def plot_strategy(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['NormalizedPrice'], mode='lines', name='Bitcoin Price (Normalized)'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['NormalizedPortfolio'], mode='lines', name='Portfolio Value (Normalized)'))
    
    # Add buy and sell signals
    buy_signals = data[data['Signal'] == 'buy']
    sell_signals = data[data['Signal'] == 'sell']
    fig.add_trace(go.Scatter(x=buy_signals['Date'], y=buy_signals['NormalizedPrice'], mode='markers', name='Buy (Fear)', marker=dict(symbol='triangle-up', size=10, color='green')))
    fig.add_trace(go.Scatter(x=sell_signals['Date'], y=sell_signals['NormalizedPrice'], mode='markers', name='Sell (Greed)', marker=dict(symbol='triangle-down', size=10, color='red')))
    
    fig.update_layout(
        title='Bitcoin Price vs Portfolio Value (Normalized)',
        xaxis_title='Date',
        yaxis_title='Normalized Value (%)',
        yaxis=dict(tickformat='.0f')
    )
    return fig

# Main Streamlit app
def main():
    st.title("Trading Bot Strategy Dashboard")

    # Fetch real-world data
    data = get_data_for_dashboard()

    if not data.empty:
        # Display strategy performance plot
        st.plotly_chart(plot_strategy(data))

        # Display raw data
        st.subheader("Raw Data")
        st.dataframe(data)

        # Additional metrics
        st.subheader("Strategy Metrics")
        col1, col2, col3 = st.columns(3)
        
        initial_value = 100  # Starting value is $100 USD total
        final_bitcoin_value = initial_value * (data['Close'].iloc[-1] / data['Close'].iloc[0])
        final_portfolio_value = data['NormalizedPortfolio'].iloc[-1]
        
        bitcoin_return = (final_bitcoin_value - initial_value) / initial_value * 100
        portfolio_return = (final_portfolio_value - initial_value) / initial_value * 100
        
        col1.metric("Bitcoin-only Return", f"{bitcoin_return:.2f}%")
        col2.metric("Portfolio Return", f"{portfolio_return:.2f}%")
        
        # Calculate Sharpe Ratio (assuming risk-free rate of 0 for simplicity)
        returns = data['NormalizedPortfolio'].pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        col3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

        # Display trade counts
        st.subheader("Trade Summary")
        buy_count = (data['Signal'] == 'buy').sum()
        sell_count = (data['Signal'] == 'sell').sum()
        st.write(f"Total trades: {buy_count + sell_count}")
        st.write(f"Buy signals (Fear): {buy_count}")
        st.write(f"Sell signals (Greed): {sell_count}")

    else:
        st.error("Failed to fetch and analyze data. Please check the logs for more information.")

if __name__ == "__main__":
    main()