import bluetooth
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
        logging.info("✅ 루틴 삽입 완료")
    except Exception as e:
        logging.error(f"❌ 루틴 삽입 실패: {e}")
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
            data.get("rest", 0),
            data["icon"],
            data["timer_name"],
            data["user_id"]
        ))
        conn.commit()
        logging.info("✅ 타이머 삽입 완료")
    except Exception as e:
        logging.error(f"❌ 타이머 삽입 실패: {e}")
    finally:
        conn.close()

def handle_data(text):
    try:
        logging.info(f"📩 수신된 데이터: {text}")
        parsed = json.loads(text)
        dtype = parsed.get("type")

        if dtype == "routine":
            insert_routine(parsed)
        elif dtype == "timer":
            insert_timer(parsed)
        else:
            logging.warning("⚠️ 알 수 없는 타입 수신")
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON 파싱 실패: {e}")
    except Exception as e:
        logging.error(f"❌ 처리 중 예외 발생: {e}")

def run_bluetooth_server():
    try:
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 1
        server_sock.bind(("", port))
        server_sock.listen(1)
        logging.info("📡 Bluetooth 서버 시작됨 - 포트 1에서 연결 대기 중...")

        client_sock, client_info = server_sock.accept()
        logging.info(f"🔗 클라이언트 연결됨: {client_info}")

        while True:
            data = client_sock.recv(1024)
            if not data:
                logging.info("📴 클라이언트 연결 종료됨")
                break
            try:
                handle_data(data.decode("utf-8").strip())
            except Exception as e:
                logging.error(f"❌ 데이터 처리 중 오류: {e}")

    except Exception as e:
        logging.error(f"❌ 블루투스 서버 시작 실패: {e}")
    finally:
        try:
            client_sock.close()
            server_sock.close()
        except:
            pass
        logging.info("🔌 Bluetooth 서버 종료됨.")

if __name__ == "__main__":
    run_bluetooth_server()
