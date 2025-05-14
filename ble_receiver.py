import json
import sqlite3
import bluetooth  # pybluez 필요
import time

DB_PATH = "routine_db.db"

def save_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if data["type"] == "timer":
        cursor.execute("""
            INSERT INTO timers (id, timer_minutes, rest, repeat_count, icon)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["id"], data["timer_minutes"], data["rest"],
            data["repeat_count"], data["icon"]
        ))

    elif data["type"] == "routine":
        if isinstance(data, list):
            for routine in data:
                insert_routine(cursor, routine)
        else:
            insert_routine(cursor, data)

    conn.commit()
    conn.close()

def insert_routine(cursor, routine):
    cursor.execute("""
        INSERT INTO routines (id, date, start_time, routine_minutes,
                              icon, routine_name, group_routine_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        routine["id"], routine["date"], routine["start_time"],
        routine["routine_minutes"], routine["icon"],
        routine["routine_name"], routine["group_routine_name"]
    ))

def receive_bluetooth_data():
    while True:
        try:
            server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            port = 1
            server_sock.bind(("", port))
            server_sock.listen(1)

            print("[BLE] connecting...")
            client_sock, address = server_sock.accept()
            print(f"[BLE] connected: {address}")

            data = client_sock.recv(4096).decode('utf-8')
            print("[BLE] receive data:", data)

            json_data = json.loads(data)
            if isinstance(json_data, list):
                for item in json_data:
                    save_to_db(item)
            else:
                save_to_db(json_data)

        except Exception as e:
            print("[BLE] error:", e)
            time.sleep(1)

        finally:
            try:
                client_sock.close()
                server_sock.close()
            except:
                pass

