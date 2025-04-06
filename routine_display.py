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
    'user': 'root',
    'password': 'webweb',
    'host': 'localhost',
    'database': 'routine_db'
}

# Image path
ICON_PATH = "/home/pi/APP_icon/"

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
    # 현재 시간 가져오기 (년-월-일 시:분)
    current = datetime.now()
    current_date = current.strftime("%Y-%m-%d")
    current_time = current.strftime("%H:%M")
    
    # DB의 시간에서 초 제거
    db_time = time_str.strftime("%H:%M") if isinstance(time_str, datetime) else time_str[:5]
    
    return current_date == date_str and current_time == db_time

def main():
    try:
        # LCD 초기화
        disp = LCD_1inch28.LCD_1inch28()
        disp.Init()
        disp.clear()
        disp.bl_DutyCycle(50)

        found_match = False
        while not found_match:
            # DB에서 데이터 조회
            routines = get_routine_data()
            if routines is None:
                time.sleep(2)
                continue

            # 현재 시간과 비교
            for routine in routines:
                date_str, start_time, icon = routine
                if compare_time(date_str, start_time):
                    # 일치하는 경우 이미지 표시
                    image_path = os.path.join(ICON_PATH, icon)
                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        im_r = image.rotate(180)
                        disp.ShowImage(im_r)
                        logging.info(f"Displaying icon: {icon}")
                        found_match = True
                    else:
                        logging.error(f"Image not found: {image_path}")
                    break

            if not found_match:
                # 기본 대기 화면 (원과 라인)
                image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
                draw = ImageDraw.Draw(image1)
                draw.arc((1,1,239,239),0, 360, fill =(0,0,255))
                draw.line([(120, 1),(120, 12)], fill = (128,255,128),width = 4)
                draw.line([(120, 227),(120, 239)], fill = (128,255,128),width = 4)
                disp.ShowImage(image1.rotate(180))
                time.sleep(2)

        # 매칭 후 프로그램 종료까지 대기
        while True:
            time.sleep(60)

    except IOError as e:
        logging.info(e)    
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("quit:")
        sys.exit(0)
    finally:
        disp.module_exit()

if __name__ == "__main__":
    main()
