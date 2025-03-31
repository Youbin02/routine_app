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

# Logging 설정
logging.basicConfig(level=logging.DEBUG)

# MySQL 연결 설정
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",       # MySQL 서버 호스트 (RPi와 같은 기기면 localhost)
            user="root",            # MySQL 사용자 이름
            password="webweb",  # MySQL 비밀번호
            database="routine_db"   # 사용할 데이터베이스 이름
        )
        return conn
    except mysql.connector.Error as e:
        logging.error(f"DB 연결 실패: {e}")
        return None

# LCD 초기화 및 이미지 표시 함수
def display_image(disp, image_path):
    try:
        image = Image.open(image_path)
        im_r = image.rotate(180)
        disp.ShowImage(im_r)
        logging.info(f"이미지 표시: {image_path}")
    except IOError as e:
        logging.error(f"이미지 로드 실패: {e}")

# 메인 로직
def main():
    # LCD 초기화
    try:
        disp = LCD_1inch28.LCD_1inch28()
        disp.Init()
        disp.clear()
        disp.bl_DutyCycle(50)  # 백라이트 밝기 설정
        logging.info("LCD 초기화 완료")
    except Exception as e:
        logging.error(f"LCD 초기화 실패: {e}")
        return

    # DB 연결
    conn = connect_db()
    if conn is None:
        disp.module_exit()
        return

    cursor = conn.cursor()

    try:
        while True:
            # 현재 RPi 시간 가져오기 (초는 무시)
            now = datetime.now()
            current_date = now.date()  # YYYY-MM-DD 형식
            current_time = now.strftime("%H:%M")  # HH:MM 형식

            # MySQL에서 routine 테이블 조회
            query = """
                SELECT icon 
                FROM routine 
                WHERE date = %s AND TIME_FORMAT(start_time, '%H:%i') = %s
            """
            cursor.execute(query, (current_date, current_time))
            result = cursor.fetchone()

            if result:
                icon_name = result[0]  # icon 칼럼 값 (예: "exercise.png")
                image_path = f"/home/pi/APP_icon/{icon_name.replace('.png', '.jpg')}"
                
                if os.path.exists(image_path):
                    display_image(disp, image_path)
                else:
                    logging.warning(f"이미지 파일 없음: {image_path}")

            # 2초 대기
            time.sleep(2)

    except mysql.connector.Error as e:
        logging.error(f"DB 쿼리 오류: {e}")
    except KeyboardInterrupt:
        logging.info("프로그램 종료")
    finally:
        # 정리
        cursor.close()
        conn.close()
        disp.module_exit()
        logging.info("리소스 정리 완료")

if __name__ == "__main__":
    main()