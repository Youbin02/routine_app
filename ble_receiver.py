from bluedot import BluetoothServer
import json
import sqlite3
import logging

DB_PATH = "/home/pi/routine_db.db"

logging.basicConfig(level=logging.INFO)

def insert_routine(data):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO routines (
                completed, date, duration_hours, duration_minutes,
                icon, routine_name, start_time, user_id, group_routine_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            0,
            data["date"],
            data["duration_hours"],
            data["duration_minutes"],
            data["icon"],
            data["routine_name"],
            data["start_time"],
            data["user_id"],
            data.get("group_routine_name")
        ))
        conn.commit()
        logging.info("루틴 삽입 완료")
    except Exception as e:
        logging.error(f"루틴 삽입 실패: {e}")
    finally:
        conn.close()

def insert_timer(data):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO timers (
                completed, duration_hours, duration_minutes,
                rest, icon, timer_name, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            0,
            data["duration_hours"],
            data["duration_minutes"],
            data.get("rest", 0),  # JSON에 rest가 없으면 0으로 기본 처리
            data["icon"],
            data["timer_name"],
            data["user_id"]
        ))
        conn.commit()
        logging.info("타이머 삽입 완료")
    except Exception as e:
        logging.error(f"타이머 삽입 실패: {e}")
    finally:
        conn.close()

def data_received(data):
    try:
        text = data.strip()
        logging.info(f"수신된 데이터: {text}")
        parsed = json.loads(text)
        dtype = parsed.get("type")

        if dtype == "routine":
            insert_routine(parsed)
        elif dtype == "timer":
            insert_timer(parsed)
        else:
            logging.warning("알 수 없는 데이터 타입 수신")
    except Exception as e:
        logging.error(f"JSON 파싱 오류: {e}")

# 블루투스 서버 실행
server = BluetoothServer(data_received)
logging.info("📡 블루투스 서버 시작됨 - 연결 대기 중...")

try:
    while True:
        pass  # 프로그램이 계속 실행되도록 유지
except KeyboardInterrupt:
    server.stop()
    logging.info("서버 종료됨")
