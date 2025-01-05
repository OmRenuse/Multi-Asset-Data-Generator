import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# Set the random seed for reproducibility
np.random.seed(0)

# Function to generate a single candlestick
def generate_candlestick(open_price):
    high_price = open_price + np.random.uniform(0, 10)
    low_price = open_price - np.random.uniform(0, 10)
    close_price = np.random.uniform(low_price, high_price)
    volume = np.random.uniform(1000, 5000)
    return open_price, high_price, low_price, close_price, volume

# Function to generate data for multiple time frames
def generate_candlestick_data(time_frames):
    data = {tf: [] for tf in time_frames}
    current_time = datetime.now()

    # Initialize the first candle
    initial_open = np.random.uniform(50, 100)
    for tf in time_frames:
        candle = generate_candlestick(initial_open)
        data[tf].append((current_time, *candle))
    
    return data, current_time

# Function to update the Excel file
def update_data_file(data, file_path):
    # Create a writer object with 'openpyxl' engine
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a' if pd.io.common.file_exists(file_path) else 'w') as writer:
        # Iterate over each time frame's data
        for tf, candles in data.items():
            # Create a DataFrame for the current time frame
            df = pd.DataFrame(candles, columns=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['TimeFrame'] = tf
            df = df[['TimeFrame', 'DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Write the DataFrame to an Excel sheet
            try:
                df.to_excel(writer, sheet_name=tf, index=False)
            except ValueError:
                # If sheet already exists, remove the existing sheet and try again
                del writer.book[tf]
                df.to_excel(writer, sheet_name=tf, index=False)


# Function to aggregate candles for a given time frame
def aggregate_candles(candles):
    if len(candles) == 0:
        return None
    open_price = candles[0][1]
    high_price = max(candle[2] for candle in candles)
    low_price = min(candle[3] for candle in candles)
    close_price = candles[-1][4]
    volume = sum(candle[5] for candle in candles)
    return open_price, high_price, low_price, close_price, volume

# List of time frames in seconds
time_frames = {
    '5sec': 5,
    '10sec': 10,
    '15sec': 15,
    '30sec': 30,
    '1min': 60,
    '2min': 120,
    '3min': 180,
    '5min': 300,
    '10min': 600,
    '15min': 900,
    '30min': 1800,
    '1hr': 3600,
    '4hr': 14400,
    '1d': 86400
}

# File to save the data
file_path = 'simulated_otc_market_data.xlsx'

# Generate initial data
data, last_update_time = generate_candlestick_data(time_frames)
update_data_file(data, file_path)

# Dictionary to hold accumulated data for each time frame
accumulated_data = {tf: [] for tf in time_frames}
last_update_times = {tf: last_update_time for tf in time_frames}

try:
    while True:
        current_time = datetime.now()
        new_data = {tf: [] for tf in time_frames}
        candles_to_aggregate = {tf: [] for tf in time_frames}

        for tf, interval in time_frames.items():
            if (current_time - last_update_times[tf]).total_seconds() >= interval:
                last_candle = data[tf][-1]
                last_open = last_candle[3]  # Close price of the last candle is used as the new open
                new_candle = generate_candlestick(last_open)
                new_candle_with_time = (current_time, *new_candle)
                new_data[tf].append(new_candle_with_time)
                candles_to_aggregate[tf].append(new_candle_with_time)
                last_update_times[tf] = current_time

        # Aggregate candles for higher time frames
        for tf, interval in sorted(time_frames.items(), key=lambda x: x[1]):
            if len(candles_to_aggregate[tf]) > 0:
                for higher_tf, higher_interval in sorted(time_frames.items(), key=lambda x: x[1]):
                    if higher_interval > interval and higher_interval % interval == 0:
                        if len(accumulated_data[higher_tf]) >= (higher_interval // interval):
                            num_full_candles = len(accumulated_data[higher_tf]) // (higher_interval // interval)
                            for _ in range(num_full_candles):
                                batch_candles = accumulated_data[higher_tf][:higher_interval // interval]
                                aggregated_candle = aggregate_candles(batch_candles)
                                if aggregated_candle is not None:
                                    new_data[higher_tf].append((current_time, *aggregated_candle))
                                accumulated_data[higher_tf] = accumulated_data[higher_tf][higher_interval // interval:]
        
        if new_data:
            update_data_file(new_data, file_path)
            for tf in time_frames:
                data[tf].extend(new_data[tf])
                accumulated_data[tf].extend(new_data[tf])

        time.sleep(1)  # Adjust sleep time as necessary

except KeyboardInterrupt:
    print("Data generation stopped.")
