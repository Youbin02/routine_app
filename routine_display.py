#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
import mysql.connector
from datetime import datetime
from PIL import Image
sys.path.append("..")
from lib import LCD_1inch28

# Raspberry Pi pin configuration
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)

# MySQL connection configuration
MYSQL_CONFIG = {
    'user': 'imopen',
    'password': 'imbest',
    'host': '192.168.92.200',  # 노트북 IP
    'database': 'routine_db',
    'port': 3306
}

def connect_db():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as err:
        logging.error(f"DB connection failed: {err}")
        return None

def get_routine_data():
    conn = connect_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        query = "SELECT date, start_time, icon FROM routine"
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        logging.error(f"Query failed: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def compare_time(date_str, time_str):
    current = datetime.now()
    current_date = current.strftime("%Y-%m-%d")
    current_time = current.strftime("%H:%M")
    db_time = time_str.strftime("%H:%M") if isinstance(time_str, datetime) else time_str[:5]
    return current_date == date_str and current_time == db_time

def main():
    disp = LCD_1inch28.LCD_1inch28()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)

    found_match = False
    while not found_match:
        routines = get_routine_data()
        if routines is None:
            time.sleep(2)
            continue

        for routine in routines:
            date_str, start_time, icon = routine
            if compare_time(date_str, start_time):
                image_path = os.path.join("/home/pi/APP_icon/", icon)
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    im_r = image.rotate(180)
                    disp.ShowImage(im_r)
                    logging.info(f"Displaying icon: {icon}")
                    found_match = True
                break

        if not found_match:
            time.sleep(2)

    while True:
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("quit:")
        sys.exit(0)
