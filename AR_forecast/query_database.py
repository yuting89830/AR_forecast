###每分鐘抓前一分鐘的時間跟不重複MAC位址數量###

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import time
import csv

# connected database
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
        print("connected successfully！")

        if connection.is_connected():
            cursor = connection.cursor()

            # 執行 SQL 查詢
            query = """
                SELECT COUNT(DISTINCT MAC) AS unique_mac_count,
                       DATE_FORMAT(FROM_UNIXTIME(TID), '%Y-%m-%d %H:%i') AS minute
                FROM devices
                WHERE FROM_UNIXTIME(TID) >= NOW() - INTERVAL 1 MINUTE
                GROUP BY minute;
            """
            cursor.execute(query)

            # 取得查詢結果
            mac_counts = cursor.fetchall()

            # 讀取現有CSV檔案內容並插入新資料
            data_to_write = []
            with open(csv_filename, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    data_to_write.append(row)

            for result in mac_counts:
                unique_mac_count = result[0]
                minute = result[1]
                data_to_write.append([minute, unique_mac_count])

            # 寫入更新後的資料到CSV檔案
            with open(csv_filename, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerows(data_to_write)

        # 休息一分鐘
        time.sleep(60)

except Error as e:
    print("資料庫錯誤:", e)

finally:
    # 關閉資料庫連線
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")
