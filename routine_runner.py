#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import sqlite3
from datetime import datetime
from PIL import Image
from gpiozero import Button, Buzzer

# LCD 라이브러리 경로 추가
sys.path.append("/home/pi/LCD_final")
from LCD_1inch28 import LCD_1inch28

# DB 및 리소스 경로
DB_PATH = '/home/pi/routine_db.db'
ICON_PATH = '/home/pi/APP_icon/'

# GPIO 설정
button1 = Button(5, pull_up=False, bounce_time=0.05)
button2 = Button(6, pull_up=False, bounce_time=0.05)
button3 = Button(26, pull
