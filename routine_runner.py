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
            if data['type'] == 'routine':
                handle_routine(data, disp)
            elif data['type'] == 'timer':
                run_repeating_timer(data, disp)
        except Exception:
            continue
