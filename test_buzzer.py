import RPi.GPIO as GPIO
import time

BUZZER_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

try:
    print("buzzer test start")
    for i in range(5):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.2)  # 0.2초 울림
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.2)  # 0.2초 정지
    print("finish")

except KeyboardInterrupt:
    print("사용자 인터럽트로 종료됨")

finally:
    GPIO.cleanup()
    print("GPIO 핀 정리 완료")
