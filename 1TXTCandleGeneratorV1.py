import pandas as pd
import numpy as np
import time
from datetime import datetime

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

# Function to update the data file
def update_data_file(data, file_path):
    with open(file_path, 'a') as f:
        for tf, candles in data.items():
            for candle in candles:
                line = f"{tf},{candle[0]},{candle[1]},{candle[2]},{candle[3]},{candle[4]},{candle[5]}\n"
                f.write(line)

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
file_path = 'simulated_otc_market_data.txt'

# Generate initial data
data, last_update_time = generate_candlestick_data(time_frames)
update_data_file(data, file_path)

try:
    while True:
        current_time = datetime.now()
        new_data = {tf: [] for tf in time_frames}
        
        for tf, interval in time_frames.items():
            if (current_time - last_update_time).total_seconds() >= interval:
                last_candle = data[tf][-1][1:]
                new_open = last_candle[3]
                new_candle = generate_candlestick(new_open)
                new_data[tf].append((current_time, *new_candle))
                last_update_time = current_time
        
        if new_data:
            update_data_file(new_data, file_path)
            for tf in time_frames:
                data[tf].extend(new_data[tf])
        
        time.sleep(1)  # Adjust sleep time as necessary

except KeyboardInterrupt:
    print("Data generation stopped.")
