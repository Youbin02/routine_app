import os
import time
import logging
import sqlite3
from datetime import datetime
from PIL import Image
from gpiozero import Button, Buzzer
from LCD_1inch28 import LCD_1inch28
from motor_control import run_motor_routine, run_motor_timer
from rfcomm_server import incoming_queue

# 경로 설정
DB_PATH = "/home/pi/LCD_final/routine_db.db"
ICON_PATH = "/home/pi/APP_icon/"

# GPIO 설정
button1 = Button(5, pull_up=False, bounce_time=0.05)
button2 = Button(6, pull_up=False, bounce_time=0.05)
button3 = Button(26, pull_up=False, bounce_time=0.05)
buzzer = Buzzer(13)

logging.basicConfig(level=logging.INFO)

def buzz(duration=1):
    logging.info(f"Buzzing for {duration} second(s)")
    buzzer.on()
    time.sleep(duration)
    buzzer.off()

def connect_db():
    return sqlite3.connect(DB_PATH)

def update_routine_status(routine_id, status):
    logging.info(f"Updating routine {routine_id} status to {status}")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE routines SET completed = ? WHERE id = ?", (status, routine_id))
    conn.commit()
    conn.close()

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
        logging.info(f"[BLE] timer save complete: ID={data['id']}")

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
            logging.info(f"[BLE] routine save complete: {r['routine_name']}")

    conn.commit()
    conn.close()

def handle_routine(r, disp):
    logging.info(f"Starting routine {r['id']} for {r['routine_minutes']} minute(s)")
    duration = r['routine_minutes'] * 60
    image_path = os.path.join(ICON_PATH, r['icon'])
    image = Image.open(image_path).resize((240, 240)).rotate(90)
    disp.ShowImage(image)
    buzz()
    start = time.time()
    result = None

    while time.time() - start < duration:
        if button1.is_pressed:
            logging.info(f"Routine {r['id']} marked as completed by button1")
            update_routine_status(r['id'], 1)
            result = 1
            break
        elif button2.is_pressed:
            logging.info(f"Routine {r['id']} marked as failed by button2")
            update_routine_status(r['id'], 0)
            result = 0
            break
        time.sleep(0.1)
    else:
        logging.info(f"Routine {r['id']} failed due to timeout")
        update_routine_status(r['id'], 0)
        result = 0

    disp.clear()

def run_timer(timer_id, sec, disp, image):
    logging.info(f"Running timer {timer_id} for {sec} seconds")
    while button3.is_pressed:
        time.sleep(0.1)
    disp.ShowImage(image.rotate(180))
    steps = sec // 60
    for i in range(steps):
        time.sleep(60)
    disp.clear()
    logging.info("Timer finished")

def run_repeating_timer(timer_data, disp):
    logging.info(f"Running repeating timer {timer_data['id']} for {timer_data['repeat_count']} sets")
    run_motor_timer(timer_data['timer_minutes'], timer_data['rest'], timer_data['repeat_count'])
    image_path = os.path.join(ICON_PATH, timer_data['icon'])
    image = Image.open(image_path).resize((240, 240)).rotate(90)
    for i in range(timer_data['repeat_count']):
        logging.info(f"Round {i+1} - Work")
        run_timer(timer_data['id'], timer_data['timer_minutes'] * 60, disp, image)
        logging.info(f"Round {i+1} - Rest")
        time.sleep(timer_data['rest'] * 60)

def run_routine_runner():
    disp = LCD_1inch28()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)
    logging.info("[🔁] 루틴 실행기 시작됨")

    while True:
        try:
            data = incoming_queue.get(timeout=1)
            logging.info(f"[📦] queue data type: {type(data)}, contents: {data}")

            # 루틴 리스트 처리
            if isinstance(data, list):
                for item in data:
                    if item.get("type") == "routine":
                        save_to_db(item)
                        handle_routine(item, disp)
                    elif item.get("type") == "timer":
                        save_to_db(item)
                        run_repeating_timer(item, disp)

            # 단일 JSON 처리
            elif isinstance(data, dict):
                if data.get("type") == "routine":
                    save_to_db(data)
                    handle_routine(data, disp)
                elif data.get("type") == "timer":
                    save_to_db(data)
                    run_repeating_timer(data, disp)

        except Exception as e:
            logging.error(f"[❌] queue error: {e}")
            continue
