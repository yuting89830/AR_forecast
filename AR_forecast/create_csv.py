###一次產生大範圍時間數據的csv檔###

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import time
import csv
import pytz
import os

# 连接数据库
hostname = '***'
port = '***'
username = '***'
password = '***'
database = '***'


# CSV檔案名稱
csv_filename = 'grafana_data_export.csv'

try:
    while True:
        # 建立資料庫連線
        connection = mysql.connector.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database=database
        )
        print("成功连接到数据库！")

        if connection.is_connected():
            cursor = connection.cursor()

            # 使用者輸入起始日期時間及結束日期時間
            start_datetime_str = input("請輸入起始日期時間 (YYYY-MM-DD hh:mm:ss): ")
            end_datetime_str = input("請輸入結束日期時間 (YYYY-MM-DD hh:mm:ss): ")

            # 將輸入的日期時間轉換為本地 datetime 物件
            local_tz = pytz.timezone('Asia/Taipei')  # 你的本地時區
            start_datetime_local = local_tz.localize(datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S'))
            end_datetime_local = local_tz.localize(datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S'))

            # 轉換成 UTC 時間
            start_datetime_utc = start_datetime_local.astimezone(pytz.utc)
            end_datetime_utc = end_datetime_local.astimezone(pytz.utc)

            # 轉換成 Unix 時間戳
            start_unix_timestamp = int(start_datetime_utc.timestamp())
            end_unix_timestamp = int(end_datetime_utc.timestamp())

            # 執行 SQL 查詢
            query = """
                SELECT COUNT(DISTINCT MAC) AS unique_mac_count,
                       DATE_FORMAT(FROM_UNIXTIME(TID), '%Y-%m-%d %H:%i') AS minute
                FROM devices
                WHERE TID BETWEEN %s AND %s
                GROUP BY DATE_FORMAT(FROM_UNIXTIME(TID), '%Y-%m-%d %H:%i');
            """
            cursor.execute(query, (start_unix_timestamp, end_unix_timestamp))

            # 取得查詢結果
            mac_counts = cursor.fetchall()

            # 讀取現有 CSV 檔案內容並追加新資料
            data_to_append = []
            if os.path.exists(csv_filename):
                with open(csv_filename, mode='r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader:
                        data_to_append.append(row)

            for result in mac_counts:
                unique_mac_count = result[0]
                minute = result[1]
                data_to_append.append([minute, unique_mac_count])

            # 將新的資料追加到現有或新建的 CSV 檔案
            with open(csv_filename, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Time', 'A metric'])  # 寫入標題行
                csv_writer.writerows(data_to_append)

except Error as e:
    print("資料庫錯誤:", e)

except KeyboardInterrupt:
    print("程式已中斷")

finally:
    # 關閉資料庫連線
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")
