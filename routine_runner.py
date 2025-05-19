#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import json
import logging
import sqlite3
import bluetooth
from datetime import datetime
from PIL import Image
from gpiozero import Button, Buzzer
from motor_control import run_motor_routine, run_motor_timer, cleanup_motor

sys.path.append("/home/pi/LCD_final")
from LCD_1inch28 import LCD_1inch28

# 경로 및 설정
DB_PATH = '/home/pi/routine_db.db'
ICON_PATH = '/home/pi/APP_icon/'
BLE_MAC_ADDRESS = "5C:CB:99:84:52:2E"

# GPIO
button1 = Button(5, pull_up=False, bounce_time=0.05)
button2 = Button(6, pull_up=False, bounce_time=0.05)
button3 = Button(26, pull_up=False, bounce_time=0.05)
buzzer = Buzzer(13)

logging.basicConfig(level=logging.INFO)

# ------------------ 공통 ------------------ #
def buzz(duration=1):
    buzzer.on()
    time.sleep(duration)
    buzzer.off()

def connect_db():
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as err:
        logging.error(f"DB connect failed: {err}")
        return None

# ------------------ 루틴 처리 ------------------ #
def get_today_routines():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = connect_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, start_time, icon, routine_minutes, routine_name, group_routine_name
            FROM routines
            WHERE date = ?
        """, (today,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"routine query error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def compare_time(start_time):
    now = datetime.now()
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )
    return abs((now - start_time).total_seconds()) < 10

def handle_routine(routine, disp):
    routine_id, start_time, icon, minutes, name, group = routine
    duration = minutes * 60
    img_path = os.path.join(ICON_PATH, icon)
    image = Image.open(img_path).resize((240, 240)).rotate(90)

    buzz()  # 루틴 시작 알림
    disp.ShowImage(image)
    time.sleep(1)

    start = time.time()
    completed = 0

    while time.time() - start < duration:
        if button1.is_pressed:
            completed = 1
            logging.info("routine success")
            break
        elif button2.is_pressed:
            logging.info("routine fail")
            break
        time.sleep(0.1)

    disp.clear()
    update_routine_status(routine_id, completed)
    send_routine_status_via_ble(routine_id, completed)
    return True

def update_routine_status(routine_id, status):
    conn = connect_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE routines SET completed = ? WHERE id = ?", (status, routine_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"routine state update error: {e}")
    finally:
        cursor.close()
        conn.close()

def all_group_routines_completed(group_name):
    conn = connect_db()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM routines
        WHERE group_routine_name = ? AND completed = 0
    """, (group_name,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count == 0

def send_routine_status_via_ble(routine_id, status):
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, routine_name, date, group_routine_name
        FROM routines WHERE id = ?
    """, (routine_id,))
    row = cursor.fetchone()
    if row:
        data = {
            "id": row[0],
            "routine_name": row[1],
            "date": row[2],
            "group_routine_name": row[3],
            "completed": status
        }
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((BLE_MAC_ADDRESS, 1))
            sock.send(json.dumps(data))
            sock.close()
            logging.info("[BLE] routine forwarding success")
        except Exception as e:
            logging.warning(f"[BLE] forwarding fail: {e}")
    cursor.close()
    conn.close()

# ------------------ 타이머 처리 ------------------ #
def get_timer_data():
    conn = connect_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timer_minutes, rest, repeat_count, icon
            FROM timers
        """)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"timer query fail: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_minutes_until_next_routine():
    routines = get_today_routines()
    now = datetime.now()
    times = []
    for _, start_time, *_ in routines:
        st = datetime.strptime(start_time, "%H:%M:%S").time()
        dt = datetime.combine(now.date(), st)
        delta = (dt - now).total_seconds() / 60
        if delta > 0:
            times.append(delta)
    return min(times) if times else float('inf')

def generate_rest_image():
    img = Image.new("RGB", (240, 240), "navy")
    return img

def run_timer(timer_id, sec, disp, background_img=None, is_rest=False):
    while button3.is_pressed:
        time.sleep(0.1)

    if background_img:
        image = background_img.copy()
    else:
        image = Image.new("RGB", (240, 240), "BLACK")

    disp.ShowImage(image.rotate(180))
    start = time.time()
    end = start + sec
    interrupted = False

    while time.time() < end:
        minutes_left = get_minutes_until_next_routine()
        if minutes_left <= 5:
            logging.info("5 minutes before starting the routine → Force stop timer")
            break
        elif minutes_left <= 10:
            buzz()

        if button3.is_pressed:
            interrupted = True
            break
        time.sleep(0.1)

    if not is_rest:
        if interrupted:
            logging.info("Timer ends early")
        else:
            buzz(2)
            logging.info("timer timeout")
    disp.clear()

def run_repeating_timer(timer_id, minutes, rest, count, disp, image):
    run_motor_timer(minutes, rest, count)
    for i in range(count):
        logging.info(f"Round {i+1} begin")
        run_timer(timer_id, minutes * 60, disp, image, is_rest=False)

        if i < count - 1:
            logging.info(f"rest {rest}min")
            rest_img = generate_rest_image()
            run_timer(timer_id, rest * 60, disp, rest_img, is_rest=True)

# ------------------ 타이머 루프 ------------------ #
def timer_loop(disp):
    timers = get_timer_data()
    if not timers:
        logging.info("No runnable timers")
        return

    index = 0
    selected = False

    while True:
        if button1.is_pressed:
            timer = timers[index]
            timer_id, minutes, rest, repeat_count, icon = timer
            img_path = os.path.join(ICON_PATH, icon)
            if os.path.exists(img_path):
                image = Image.open(img_path).resize((240, 240)).rotate(90)
                disp.ShowImage(image)
            else:
                disp.clear()
            index = (index + 1) % len(timers)
            selected = True
            time.sleep(0.3)

        elif button2.is_pressed:
            disp.clear()
            return

        elif selected and button3.is_pressed:
            if get_minutes_until_next_routine() <= 5:
                logging.info("Timer start limit when routine time is approaching")
                disp.clear()
                return

            timer = timers[index - 1]
            timer_id, minutes, rest, repeat_count, icon = timer
            img_path = os.path.join(ICON_PATH, icon)
            if os.path.exists(img_path):
                image = Image.open(img_path).resize((240, 240)).rotate(90)
                run_repeating_timer(timer_id, minutes, rest, repeat_count, disp, image)
                return
            else:
                disp.clear()
                return

# ------------------ 메인 루프 ------------------ #
def run_routine_loop():
    disp = LCD_1inch28()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)

    group_started = {}

    while True:
        routines = get_today_routines()
        routine_matched = False

        for routine in routines:
            routine_id, start_time, icon, minutes, name, group = routine
            if group not in group_started:
                group_started[group] = False

            if compare_time(start_time):
                if not group_started[group]:
                    total_minutes = sum(r[3] for r in routines if r[5] == group)
                    run_motor_routine(total_minutes)
                    buzz()
                    group_started[group] = True

                if handle_routine(routine, disp):
                    if all_group_routines_completed(group):
                        buzz()
                    routine_matched = True
                    break

        if not routine_matched:
            timer_loop(disp)

        time.sleep(1)

if __name__ == "__main__":
    try:
        run_routine_loop()
    except KeyboardInterrupt:
        logging.info("User exit request")
        disp = LCD_1inch28()
        disp.module_exit()
        sys.exit(0)
