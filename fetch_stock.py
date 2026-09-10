import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import traceback

def fetch_aapl_data():
    try:
        # Fetch AAPL data
        aapl = yf.Ticker("AAPL")
        # Get all available historical data
        hist = aapl.history(period="max")
        
        if hist.empty:
            raise ValueError("No data returned from Yahoo Finance")
            
        # Reset index to have Date as a column
        hist.reset_index(inplace=True)
        # Convert Date to string format
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        
        # Select relevant columns: Date, Open, High, Low, Close, Volume
        data = hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Drop rows with NaN values in OHLC columns (e.g., today's incomplete data)
        data = data.dropna(subset=['Open', 'High', 'Low', 'Close'])
        
        # Convert to list of dictionaries
        data_list = data.to_dict(orient='records')
        
        # Create a dictionary with metadata and data
        result = {
            "symbol": "AAPL",
            "last_updated": datetime.now().isoformat(),
            "data": data_list
        }
        
        return result, None
    except Exception as e:
        return None, str(e)

def generate_dummy_data():
    """Generate realistic dummy data for demonstration when API fails"""
    import random
    from datetime import datetime, timedelta
    
    # Generate data for the past 20 years (approx 5000 trading days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20*365)
    
    data_list = []
    current_date = start_date
    price = 100.0  # Starting price
    
    while current_date <= end_date:
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            # Generate realistic OHLCV data
            volatility = 0.02  # 2% daily volatility
            open_price = price * (1 + random.uniform(-volatility, volatility))
            close_price = open_price * (1 + random.uniform(-volatility, volatility))
            high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility))
            volume = random.randint(1000000, 10000000)
            
            data_list.append({
                "Date": current_date.strftime('%Y-%m-%d'),
                "Open": round(open_price, 2),
                "High": round(high_price, 2),
                "Low": round(low_price, 2),
                "Close": round(close_price, 2),
                "Volume": volume
            })
            price = close_price  # Use close as next day's open price
        
        current_date += timedelta(days=1)
    
    # Create a dictionary with metadata and data
    result = {
        "symbol": "AAPL",
        "last_updated": datetime.now().isoformat(),
        "data": data_list
    }
    
    return result

def main():
    result, error = fetch_aapl_data()
    
    if error is not None:
        print(f"Warning: Failed to fetch data from Yahoo Finance: {error}")
        print("Generating dummy data for demonstration...")
        result = generate_dummy_data()
    
    if result is not None:
        # Write to JSON file
        with open('data.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Successfully wrote {len(result['data'])} records to data.json")
        print(f"Last updated: {result['last_updated']}")
    else:
        print("Error: Failed to fetch or generate data")
        exit(1)

if __name__ == "__main__":
    main()