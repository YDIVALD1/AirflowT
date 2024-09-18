import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

def get_stock_data(tickers, period='3mo'):
    """
    Fetches stock data for multiple tickers over a specified period.
    
    Parameters:
        tickers (list of str): List of stock tickers.
        period (str): The period over which to fetch data (default is '1mo').
        
    Returns:
        pd.DataFrame: Combined DataFrame with percentage change and stock info.
    """
    all_data = []

    for ticker in tickers:
        # Fetch data
        df = yf.download(ticker, period=period)
        df['Ticker'] = ticker  # Add ticker column for identification

        # Calculate percentage change
        df['Pct Change'] = df['Close'].pct_change() * 100  # Convert to percentage
        
        # Drop NaN values
        df = df.dropna()
        
        all_data.append(df)
    
    # Combine all DataFrames
    combined_df = pd.concat(all_data)
    
    return combined_df

def plot_stock_comparison(tickers):
    """
    Plots stock data with a custom hover template showing comparison and overall summary.
    
    Parameters:
        tickers (list of str): List of stock tickers to include in the plot.
    """
    df = get_stock_data(tickers)
    
    # Create subplots: one for the line chart, one for the overall summary
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=("Daily Percentage Change", "Overall Percentage Change"),
        column_widths=[0.7, 0.3]
    )
    
    # Add traces for percentage change
    for ticker in tickers:
        # Filter data for the current ticker
        ticker_df = df[df['Ticker'] == ticker]
        
        # Add line chart trace for each ticker
        fig.add_trace(go.Scatter(
            x=ticker_df.index,
            y=ticker_df['Pct Change'],
            mode='lines+markers',
            name=ticker,
            hovertemplate=f"<b>Date:</b> %{{x|%Y-%m-%d}}<br>" +
                          f"<b>{ticker} % Change:</b> %{{y:.2f}}%<br>" +
                          f"<b>Open:</b> %{{customdata[0]:.2f}}<br>" +
                          f"<b>Close:</b> %{{customdata[1]:.2f}}<br>" +
                          "<extra></extra>",
            customdata=ticker_df[['Open', 'Close']].values
        ), row=1, col=1)
    
    # Calculate overall percentage change for each stock
    summary_df = df.groupby('Ticker').agg(
        Start_Price=('Close', 'first'),
        End_Price=('Close', 'last')
    )
    summary_df['Overall_Pct_Change'] = (summary_df['End_Price'] - summary_df['Start_Price']) / summary_df['Start_Price'] * 100
    summary_df = summary_df.reset_index()
    
    # Add bar chart trace for overall percentage change
    fig.add_trace(go.Bar(
        x=summary_df['Ticker'],
        y=summary_df['Overall_Pct_Change'],
        name='Overall % Change',
        marker=dict(color='rgba(49,130,189,0.7)')
    ), row=1, col=2)
    
    # Update layout
    fig.update_layout(
        title='Stock Data Visualization with Overall Summary',
        xaxis_title='Date',
        yaxis_title='% Change',
        hovermode='x unified',
        barmode='group',  # Group bars for overall percentage change
        xaxis2_title='Stocks',
        yaxis2_title='Percentage Change',
        xaxis2=dict(tickangle=-45)  # Rotate tick labels for better readability
    )
    
    fig.show()

# Example usage
tickers = ['NVDA', 'AAPL', 'MSFT','U']  # List of tickers to visualize
plot_stock_comparison(tickers)
