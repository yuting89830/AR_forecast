import pandas as pd
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
from datetime import timedelta
import csv
from datetime import datetime, timedelta

# Process and save data
def process_and_save_data(input_path, output_path):
    data = []

    # 讀取原始 CSV 檔案內容
    with open(input_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)

    processed_data = []
    for i in range(len(data)):
        current_time = datetime.strptime(data[i]['Time'], '%Y-%m-%d %H:%M')
        processed_data.append(data[i])  # 直接加入原始資料
        
        if i < len(data) - 1:
            next_time = datetime.strptime(data[i + 1]['Time'], '%Y-%m-%d %H:%M')
            while (next_time - current_time).total_seconds() > 60:
                # 補足缺失的分鐘資料
                missing_time = current_time + timedelta(minutes=1)
                average_metric = (int(data[i]['A metric']) + int(data[i + 1]['A metric'])) // 2
                processed_data.append({'Time': missing_time.strftime('%Y-%m-%d %H:%M'), 'A metric': average_metric})
                current_time = missing_time

    # 寫入處理後的資料到新的 CSV 檔案
    with open(output_path, mode='w', newline='') as csv_file:
        fieldnames = ['Time', 'A metric']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(processed_data)

def load_and_process_data(file_path):
    df = pd.read_csv(file_path, engine='python')
    df['Time'] = pd.to_datetime(df['Time'], yearfirst=True)
    df.set_index('Time', inplace=True)
    half_hourly_count = df['A metric'].resample('30T').nunique()
    series = half_hourly_count.values
    return series

def train_and_predict(series, train_size=0.8, lags=50, further_pred_length=50):
    train_size = int(len(series) * train_size)
    train, test = series[:train_size], series[train_size:]
    
    model = AutoReg(train, lags=lags)
    model_fit = model.fit()
    
    start_idx = len(train)
    end_idx = len(train) + len(test) - 1 + further_pred_length
    predictions = model_fit.predict(start=start_idx, end=end_idx, dynamic=True)
    
    return predictions


def calculate_rmse(test, predictions):
    rmse = sqrt(mean_squared_error(test, predictions[:len(test)]))
    return rmse

def plot_results(test, predictions):
    plt.figure(figsize=(10, 4))
    plt.title('[AutoRegression] Crowd Forecasting')
    plt.xlabel('Time points')
    plt.ylabel('Number of people')
    plt.plot(test, label='Ground Truth')
    plt.plot(predictions, color='red', label='Predictions')
    plt.legend()
    plt.show()

def output_predictions(test, predictions):
    for i, (true_value, pred_value) in enumerate(zip(test, predictions), start=1):
        print(f'Step {i}: Predicted={pred_value:.2f}, Expected={true_value:.2f}')
