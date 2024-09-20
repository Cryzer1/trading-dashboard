import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Import data fetching module
from src.test_data_fetcher import get_data_for_dashboard

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(selected_strategies):
    data = get_data_for_dashboard(selected_strategies)
    for strategy, df in data.items():
        print(f"Columns in the data for {strategy}:", df.columns)
        print(f"Data types for {strategy}:", df.dtypes)
        print(f"First few rows for {strategy}:", df.head())
    return data

def plot_strategies(data):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    
    colors = ['blue', 'red', 'green', 'purple', 'orange']  # Add more colors if needed
    
    for i, (strategy_name, df) in enumerate(data.items()):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(x=df['Date'], y=df[f'NormalizedPortfolio_{strategy_name}'], mode='lines', name=f'{strategy_name} Portfolio', line=dict(color=color)), row=1, col=1)
        
        buy_signals = df[df[f'Signal_{strategy_name}'] == 'buy']
        sell_signals = df[df[f'Signal_{strategy_name}'] == 'sell']
        fig.add_trace(go.Scatter(x=buy_signals['Date'], y=buy_signals['NormalizedPrice'], mode='markers', name=f'{strategy_name} Buy', marker=dict(symbol='triangle-up', size=10, color=color)), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_signals['Date'], y=sell_signals['NormalizedPrice'], mode='markers', name=f'{strategy_name} Sell', marker=dict(symbol='triangle-down', size=10, color=color)), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df['Date'], y=df['NormalizedPrice'], mode='lines', name='Bitcoin Price', line=dict(color='black')), row=1, col=1)
    
    if 'Volume' in df.columns:
        fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume'), row=2, col=1)
        fig.update_yaxes(title_text='Volume', row=2, col=1)
    
    fig.update_layout(height=800, title='Strategy Comparison', showlegend=True)
    fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_yaxes(title_text='Normalized Value (%)', row=1, col=1)
    
    return fig

def calculate_metrics(df, strategy_name):
    initial_value = 100
    final_bitcoin_value = initial_value * (df['Close'].iloc[-1] / df['Close'].iloc[0])
    final_portfolio_value = df[f'NormalizedPortfolio_{strategy_name}'].iloc[-1]
    
    bitcoin_return = (final_bitcoin_value - initial_value) / initial_value * 100
    portfolio_return = (final_portfolio_value - initial_value) / initial_value * 100
    
    returns = df[f'NormalizedPortfolio_{strategy_name}'].pct_change().dropna()
    sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
    
    buy_count = (df[f'Signal_{strategy_name}'] == 'buy').sum()
    sell_count = (df[f'Signal_{strategy_name}'] == 'sell').sum()
    
    return {
        "Bitcoin Return": f"{bitcoin_return:.2f}%",
        "Portfolio Return": f"{portfolio_return:.2f}%",
        "Sharpe Ratio": f"{sharpe_ratio:.2f}",
        "Total Trades": buy_count + sell_count,
        "Buy Signals": buy_count,
        "Sell Signals": sell_count
    }

def main():
    st.set_page_config(page_title="Trading Bot Strategy Dashboard", layout="wide")
    st.title("Trading Bot Strategy Comparison Dashboard")

    available_strategies = ['Simple Moving Average', 'RSI']  # Add more strategies here
    selected_strategies = st.multiselect("Select strategies to compare", available_strategies, default=['Simple Moving Average'])

    if not selected_strategies:
        st.warning("Please select at least one strategy to display.")
        return

    data = load_data(selected_strategies)

    if data:
        st.plotly_chart(plot_strategies(data), use_container_width=True)

        col1, col2 = st.columns(2)
        for i, (strategy_name, df) in enumerate(data.items()):
            with col1 if i % 2 == 0 else col2:
                st.subheader(f"{strategy_name} Metrics")
                metrics = calculate_metrics(df, strategy_name)
                for metric, value in metrics.items():
                    st.metric(metric, value)

        with st.expander("Show Raw Data"):
            for strategy_name, df in data.items():
                st.subheader(f"{strategy_name} Data")
                st.dataframe(df)
    else:
        st.error("Failed to fetch and analyze data. Please check the logs for more information.")

if __name__ == "__main__":
    main()