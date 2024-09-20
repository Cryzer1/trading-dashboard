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
    
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'magenta']  # Add more colors if needed
    
    # Always plot Bitcoin price first with a distinct color (gold)
    bitcoin_data = data['Bitcoin']
    fig.add_trace(go.Scatter(x=bitcoin_data['Date'], y=bitcoin_data['Close'], mode='lines', name='Bitcoin Price ($)', line=dict(color='gold', width=2)), row=1, col=1)
    
    for i, (strategy_name, df) in enumerate(data.items()):
        if strategy_name != 'Bitcoin':
            color = colors[i % len(colors)]
            if f'NormalizedPortfolio_{strategy_name}' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df[f'NormalizedPortfolio_{strategy_name}'], mode='lines', name=f'{strategy_name} Portfolio', line=dict(color=color)), row=1, col=1)
            
            if f'Signal_{strategy_name}' in df.columns and 'Close' in df.columns:
                buy_signals = df[df[f'Signal_{strategy_name}'] == 'buy']
                sell_signals = df[df[f'Signal_{strategy_name}'] == 'sell']
                fig.add_trace(go.Scatter(x=buy_signals['Date'], y=buy_signals['Close'], mode='markers', name=f'{strategy_name} Buy', marker=dict(symbol='triangle-up', size=10, color=color)), row=1, col=1)
                fig.add_trace(go.Scatter(x=sell_signals['Date'], y=sell_signals['Close'], mode='markers', name=f'{strategy_name} Sell', marker=dict(symbol='triangle-down', size=10, color=color)), row=1, col=1)
    
    if 'Volume' in bitcoin_data.columns:
        fig.add_trace(go.Bar(x=bitcoin_data['Date'], y=bitcoin_data['Volume'], name='Volume', marker_color='lightgray'), row=2, col=1)
        fig.update_yaxes(title_text='Volume', row=2, col=1)
    
    fig.update_layout(height=800, title='Strategy Comparison', showlegend=True)
    fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_yaxes(title_text='Value', row=1, col=1)
    
    # Add a secondary y-axis for the normalized portfolio values
    fig.update_layout(yaxis2=dict(title='Normalized Portfolio Value (%)', overlaying='y', side='right'))
    
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

    available_strategies = ['Simple Moving Average', 'RSI', 'MACD', 'Bollinger Bands', 'Sentiment Based']
    selected_strategies = st.multiselect("Select strategies to compare", available_strategies, default=['Simple Moving Average'])

    if not selected_strategies:
        st.warning("Please select at least one strategy to display.")
        return

    # Always include 'Bitcoin' in the data fetch
    data = load_data(selected_strategies + ['Bitcoin'])

    if data:
        st.plotly_chart(plot_strategies(data), use_container_width=True)

        col1, col2 = st.columns(2)
        for i, (strategy_name, df) in enumerate(data.items()):
            if strategy_name != 'Bitcoin':
                with col1 if i % 2 == 0 else col2:
                    st.subheader(f"{strategy_name} Metrics")
                    metrics = calculate_metrics(df, strategy_name)
                    for metric, value in metrics.items():
                        st.metric(metric, value)

        with st.expander("Show Raw Data"):
            for strategy_name, df in data.items():
                if strategy_name != 'Bitcoin':
                    st.subheader(f"{strategy_name} Data")
                    st.dataframe(df)
    else:
        st.error("Failed to fetch and analyze data. Please check the logs for more information.")

if __name__ == "__main__":
    main()