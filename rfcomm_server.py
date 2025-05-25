import bluetooth
import json
import sqlite3
import time
import logging

client_socket_global = None
DB_PATH = "/home/pi/LCD_final/routine_db.db"

logging.basicConfig(level=logging.INFO)

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
        logging.info(f"[BLE] timer save: ID={data['id']}")

    elif data["type"] == "routine":
        routines = data if isinstance(data, list) else [data]
        for r in routines:
            cursor.execute("""
                INSERT INTO routines (id, date, start_time, routine_minutes,
                                      icon, routine_name, group_routine_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                r["id"], r["date"], r["start_time"], r["routine_minutes"],
                r["icon"], r["routine_name"], r["group_routine_name"]
            ))
            logging.info(f"[BLE] routine save: {r['routine_name']}")

    conn.commit()
    conn.close()

def start_rfcomm_server():
    global client_socket_global
    while True:
        try:
            server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            port = 1
            server_sock.bind(("", port))
            server_sock.listen(1)

            logging.info("[🔌] RFCOMM Bluetooth connect wait...")
            client_sock, address = server_sock.accept()
            client_socket_global = client_sock
            logging.info(f"[✅] connected: {address}")

            buffer = ""
            while True:
                data = client_sock.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue

                    logging.info(f"[📥] send data: {line}")
                    try:
                        json_data = json.loads(line)
                        if isinstance(json_data, list):
                            for entry in json_data:
                                save_to_db(entry)
                        else:
                            save_to_db(json_data)
                        ack = json.dumps({"ack": True}) + '\n'
                        client_sock.send(ack.encode())
                    except Exception as e:
                        logging.error(f"[❌] JSON error: {e}")
        except Exception as e:
            logging.error(f"[❌] connect or receive error: {e}")
            time.sleep(1)
        finally:
            try:
                client_sock.close()
                server_sock.close()
            except:
                pass

def send_json_to_app(data_dict):
    global client_socket_global
    if client_socket_global:
        try:
            json_str = json.dumps(data_dict) + '\n'
            client_socket_global.send(json_str.encode())
            logging.info(f"[📤] sent to app: {json_str.strip()}")
        except Exception as e:
            logging.error(f"[❌] sending error: {e}")
    else:
        logging.warning("[⚠️] no client connected to send data")

if __name__ == "__main__":
    start_rfcomm_server()
