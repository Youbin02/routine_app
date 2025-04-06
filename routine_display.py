#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
import mysql.connector
from datetime import datetime, time as dtime, timedelta
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
        logging.info(f"Fetched data: {data}")
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

    # time_str 타입에 따른 처리
    if isinstance(time_str, dtime):
        db_time = f"{time_str.hour:02d}:{time_str.minute:02d}"
    elif isinstance(time_str, timedelta):
        total_seconds = int(time_str.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        db_time = f"{hours:02d}:{minutes:02d}"
    else:
        db_time = str(time_str)[:5]

    # 디버깅용 로그 강화
    logging.info(f"Comparing: current_date={current_date}, db_date={date_str}, current_time={current_time}, db_time={db_time}")
    is_match = current_date == str(date_str) and current_time == db_time
    logging.info(f"Match result: {is_match}")
    return is_match

def main():
    disp = LCD_1inch28.LCD_1inch28()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)

    found_match = False
    while not found_match:
        routines = get_routine_data()
        if routines is None:
            logging.warning("No data fetched, retrying in 2 seconds")
            time.sleep(2)
            continue

        for routine in routines:
            date_str, start_time, icon = routine
            logging.info(f"Processing routine: date={date_str}, start_time={start_time}, icon={icon}")
            if compare_time(date_str, start_time):
                image_path = os.path.join("/home/pi/APP_icon/", icon)
                logging.info(f"Attempting to load image: {image_path}")
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    im_r = image.rotate(180)
                    disp.ShowImage(im_r)
                    logging.info(f"Displaying icon: {icon}")
                    found_match = True
                else:
                    logging.error(f"Image file not found: {image_path}")
                break  # 일치하는 첫 번째 레코드만 처리

        if not found_match:
            logging.info("No match found, waiting 2 seconds")
            time.sleep(2)

    logging.info("Match found, entering idle loop")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("quit:")
        sys.exit(0)
