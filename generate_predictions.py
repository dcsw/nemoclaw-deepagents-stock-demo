import pandas as pd
import json
from prophet import Prophet
from dateutil.relativedelta import relativedelta

# Load the data
with open('data.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data['data'])
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').reset_index(drop=True)

# We'll store predictions in a list
predictions = []

# Calculate the earliest date we can predict (need 39 months of prior data for training)
earliest_predict_date = df['Date'].min() + relativedelta(months=39)
# Latest date we can predict (use all available data)
latest_predict_date = df['Date'].max()

# Generate monthly dates (first day of each month) covering the full range
monthly_dates = pd.date_range(start=earliest_predict_date, end=latest_predict_date, freq='MS')

print(f"Generating predictions for {len(monthly_dates)} monthly dates from {earliest_predict_date.date()} to {latest_predict_date.date()}")

for i, target_date in enumerate(monthly_dates):
    # Find the first available trading day on or after target_date
    mask = df['Date'] >= target_date
    if not any(mask):
        continue
    current_date = df.loc[mask, 'Date'].iloc[0]
    current_volume = df.loc[mask, 'Volume'].iloc[0]
    
    # We need at least 39 months of data before current_date to have 36 months of training data ending 3 months prior
    if current_date < df['Date'].min() + relativedelta(months=39):
        continue
    
    # Training period: 36 months ending 3 months before current_date
    train_end = current_date - relativedelta(months=3)
    train_start = train_end - relativedelta(months=36)
    
    # Filter training data
    train_mask = (df['Date'] >= train_start) & (df['Date'] <= train_end)
    train_df = df.loc[train_mask, ['Date', 'Close', 'Volume']].copy()
    train_df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
    
    # Initialize and fit Prophet model with Volume as regressor
    m = Prophet()
    m.add_regressor('Volume')
    m.fit(train_df)
    
    # Prepare future dataframe for prediction date (we need the Volume for the current date)
    future = pd.DataFrame({
        'ds': [current_date],
        'Volume': [current_volume]
    })
    
    # Make prediction
    forecast = m.predict(future)
    predicted_close = forecast['yhat'].iloc[0]
    
    # Store prediction
    predictions.append({
        'Date': current_date.strftime('%Y-%m-%d'),
        'PredictedClose': round(predicted_close, 4)
    })
    
    print(f"Processed {i+1} predictions, date: {current_date}, predicted close: {predicted_close:.2f}")

print(f"Generated {len(predictions)} predictions and saved to predictions.json")

# Create the result dictionary
result = {
    'symbol': 'AAPL',
    'last_updated': pd.Timestamp.now().isoformat(),
    'data': predictions
}

# Write to predictions.json
with open('predictions.json', 'w') as f:
    json.dump(result, f, indent=2)