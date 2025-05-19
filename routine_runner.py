import os
import time
import logging
import sqlite3
from datetime import datetime
from PIL import Image
from gpiozero import Button, Buzzer
from LCD_1inch28 import LCD_1inch28
from motor_control import run_motor_routine, run_motor_timer

# 경로 설정
DB_PATH = "/home/pi/LCD_final/routine_db.db"
ICON_PATH = "/home/pi/LCD_final/APP_icon/"

# GPIO 설정
button1 = Button(5, pull_up=False, bounce_time=0.05)
button2 = Button(6, pull_up=False, bounce_time=0.05)
button3 = Button(26, pull_up=False, bounce_time=0.05)
buzzer = Buzzer(13)

logging.basicConfig(level=logging.INFO)

def buzz(duration=1):
    buzzer.on()
    time.sleep(duration)
    buzzer.off()

def connect_db():
    return sqlite3.connect(DB_PATH)

def get_today_routines():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, start_time, icon, routine_minutes, routine_name, group_routine_name
        FROM routines
        WHERE date = ? AND completed = 0
    """, (today,))
    routines = cursor.fetchall()
    conn.close()
    return routines

def update_routine_status(routine_id, status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE routines SET completed = ? WHERE id = ?", (status, routine_id))
    conn.commit()
    conn.close()

def compare_time(start_time_str):
    now = datetime.now()
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )
    return now >= start_time

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

def handle_routine(routine_id, minutes, image, disp):
    duration = minutes * 60
    disp.ShowImage(image)
    buzz()
    start = time.time()
    while time.time() - start < duration:
        if button1.is_pressed:
            update_routine_status(routine_id, 1)
            disp.clear()
            return
        elif button2.is_pressed:
            update_routine_status(routine_id, 0)
            disp.clear()
            return
        time.sleep(0.1)
    update_routine_status(routine_id, 0)
    disp.clear()

def get_timer_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timer_minutes, rest, repeat_count, icon FROM timers
    """)
    timers = cursor.fetchall()
    conn.close()
    return timers

def run_timer(timer_id, sec, disp, image):
    while button3.is_pressed:
        time.sleep(0.1)
    disp.ShowImage(image.rotate(180))
    start = time.time()
    steps = sec // 60
    for i in range(steps):
        time.sleep(60)
        minutes_left = get_minutes_until_next_routine()
        if minutes_left <= 5:
            break
    disp.clear()

def run_repeating_timer(timer_id, minutes, rest, count, disp, image):
    run_motor_timer(minutes, rest, count)
    for i in range(count):
        run_timer(timer_id, minutes * 60, disp, image)
        time.sleep(rest * 60)

def timer_loop(disp):
    if get_minutes_until_next_routine() <= 5:
        print("⚠️ 루틴 임박 → 타이머 실행 제한")
        return
    timers = get_timer_data()
    if not timers:
        return
    index = 0
    selected = False
    while True:
        if button1.is_pressed:
            timer = timers[index]
            timer_id, minutes, rest, repeat_count, icon = timer
            image_path = os.path.join(ICON_PATH, icon)
            if os.path.exists(image_path):
                image = Image.open(image_path).resize((240, 240)).rotate(90)
                disp.ShowImage(image)
            index = (index + 1) % len(timers)
            selected = True
            time.sleep(0.3)
        elif button2.is_pressed:
            disp.clear()
            return
        elif selected and button3.is_pressed:
            timer = timers[index - 1]
            timer_id, minutes, rest, repeat_count, icon = timer
            image_path = os.path.join(ICON_PATH, icon)
            if os.path.exists(image_path):
                image = Image.open(image_path).resize((240, 240)).rotate(90)
                run_repeating_timer(timer_id, minutes, rest, repeat_count, disp, image)
                return

def run_routine_loop():
    disp = LCD_1inch28()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)
    while True:
        routines = get_today_routines()
        for routine in routines:
            routine_id, start_time, icon, minutes, name, group = routine
            if compare_time(start_time):
                img_path = os.path.join(ICON_PATH, icon)
                if os.path.exists(img_path):
                    img = Image.open(img_path).resize((240, 240)).rotate(90)
                    run_motor_routine(minutes)
                    handle_routine(routine_id, minutes, img, disp)
                    break  # 루틴 하나 실행 후 빠져나감
        else:
            if get_minutes_until_next_routine() > 5:
                timer_loop(disp)
        time.sleep(1)

if __name__ == "__main__":
    try:
        run_routine_loop()
    except KeyboardInterrupt:
        disp = LCD_1inch28()
        disp.module_exit()
        os._exit(0)
