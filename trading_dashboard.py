import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Import data fetching module
from src.test_data_fetcher import get_data_for_dashboard

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return get_data_for_dashboard()

def plot_strategy(data):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Scatter(x=data['Date'], y=data['NormalizedPrice'], mode='lines', name='Bitcoin Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['NormalizedPortfolio'], mode='lines', name='Portfolio Value'), row=1, col=1)
    
    buy_signals = data[data['Signal'] == 'buy']
    sell_signals = data[data['Signal'] == 'sell']
    fig.add_trace(go.Scatter(x=buy_signals['Date'], y=buy_signals['NormalizedPrice'], mode='markers', name='Buy', marker=dict(symbol='triangle-up', size=10, color='green')), row=1, col=1)
    fig.add_trace(go.Scatter(x=sell_signals['Date'], y=sell_signals['NormalizedPrice'], mode='markers', name='Sell', marker=dict(symbol='triangle-down', size=10, color='red')), row=1, col=1)
    
    fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume'), row=2, col=1)
    
    fig.update_layout(height=800, title='Bitcoin Price vs Portfolio Value (Normalized)', showlegend=True)
    fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_yaxes(title_text='Normalized Value (%)', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)
    
    return fig

def main():
    st.set_page_config(page_title="Trading Bot Strategy Dashboard", layout="wide")
    st.title("Trading Bot Strategy Dashboard")

    data = load_data()

    if not data.empty:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.plotly_chart(plot_strategy(data), use_container_width=True)
        
        with col2:
            st.subheader("Strategy Metrics")
            initial_value = 100
            final_bitcoin_value = initial_value * (data['Close'].iloc[-1] / data['Close'].iloc[0])
            final_portfolio_value = data['NormalizedPortfolio'].iloc[-1]
            
            bitcoin_return = (final_bitcoin_value - initial_value) / initial_value * 100
            portfolio_return = (final_portfolio_value - initial_value) / initial_value * 100
            
            st.metric("Bitcoin-only Return", f"{bitcoin_return:.2f}%")
            st.metric("Portfolio Return", f"{portfolio_return:.2f}%")
            
            returns = data['NormalizedPortfolio'].pct_change().dropna()
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

            st.subheader("Trade Summary")
            buy_count = (data['Signal'] == 'buy').sum()
            sell_count = (data['Signal'] == 'sell').sum()
            st.write(f"Total trades: {buy_count + sell_count}")
            st.write(f"Buy signals: {buy_count}")
            st.write(f"Sell signals: {sell_count}")

        with st.expander("Show Raw Data"):
            st.dataframe(data)
    else:
        st.error("Failed to fetch and analyze data. Please check the logs for more information.")

if __name__ == "__main__":
    main()