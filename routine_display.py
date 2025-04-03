#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
import mysql.connector
from datetime import datetime
sys.path.append("..")
from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont

# Raspberry Pi pin configuration
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 

# MySQL configuration
MYSQL_HOST = "192.168.1.15"
MYSQL_USER = "root"
MYSQL_PASSWORD = "webweb"
MYSQL_DATABASE = "routine_db"

logging.basicConfig(level=logging.DEBUG)

def connect_to_mysql():
    """MySQL 데이터베이스에 연결"""
    try:
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
    except mysql.connector.Error as e:
        logging.error(f"MySQL connection error: {e}")
        return None

def get_routine_icon():
    """현재 시간과 일치하는 routine 테이블의 icon 데이터 가져오기"""
    try:
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        
        logging.info(f"Checking DB - Date: {current_date}, Time: {current_time.hour}:{current_time.minute}")
        
        db = connect_to_mysql()
        if db is None:
            return None
            
        cursor = db.cursor()
        
        query = """
        SELECT icon 
        FROM routine 
        WHERE DATE(date) = %s 
        AND HOUR(start_time) = %s 
        AND MINUTE(start_time) = %s
        """
        cursor.execute(query, (current_date, current_time.hour, current_time.minute))
        
        result = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return result[0] if result else None
        
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return None

def main():
    try:
        # LCD 초기화
        disp = LCD_1inch28.LCD_1inch28()
        disp.Init()
        disp.clear()
        disp.bl_DutyCycle(50)

        # 폰트 설정
        Font1 = ImageFont.truetype("../Font/Font01.ttf", 25)
        Font2 = ImageFont.truetype("../Font/Font01.ttf", 35)

        while True:
            # 현재 시간 가져오기 (2초마다 갱신)
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")  # "HH:MM" 형식으로 시간 문자열 생성

            # 빈 이미지 생성
            image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
            draw = ImageDraw.Draw(image1)

            # 기본 디자인 (원과 선)
            draw.arc((1,1,239,239), 0, 360, fill=(0,0,255))
            draw.arc((2,2,238,238), 0, 360, fill=(0,0,255))
            draw.arc((3,3,237,237), 0, 360, fill=(0,0,255))
            draw.line([(120,1),(120,12)], fill=(128,255,128), width=4)
            draw.line([(120,227),(120,239)], fill=(128,255,128), width=4)
            draw.line([(1,120),(12,120)], fill=(128,255,128), width=4)
            draw.line([(227,120),(239,120)], fill=(128,255,128), width=4)

            # 현재 시간 표시
            draw.text((70, 50), f"Time: {current_time_str}", fill=(128,255,128), font=Font2)

            # 데이터베이스에서 아이콘 가져오기
            icon_file = get_routine_icon()

            if icon_file:
                image_path = f"../pic/{icon_file}.jpg"
                if os.path.exists(image_path):
                    # 아이콘 이미지 로드 및 표시
                    icon_image = Image.open(image_path)
                    im_r = icon_image.rotate(180)
                    disp.ShowImage(im_r)
                    logging.info(f"Displaying icon: {icon_file}")
                else:
                    # 아이콘 파일 없음 메시지
                    draw.text((40, 150), f"Icon: {icon_file} (Not Found)", fill="WHITE", font=Font1)
                    im_r = image1.rotate(180)
                    disp.ShowImage(im_r)
            else:
                # 루틴 없음 메시지
                draw.text((40, 150), "No Routine", fill="WHITE", font=Font2)
                im_r = image1.rotate(180)
                disp.ShowImage(im_r)

            # 2초 대기 (다음 갱신까지)
            time.sleep(2)

    except IOError as e:
        logging.error(f"IO Error: {e}")
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("Program terminated by user")
        sys.exit(0)
    finally:
        disp.module_exit()

if __name__ == "__main__":
    main()
