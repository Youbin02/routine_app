import bluetooth
import json
import time

def send_test_json():
    # RFCOMM 클라이언트 소켓 생성
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    # 앱의 Bluetooth MAC 주소로 교체 필요
    bd_addr = "5C:CB:92:88:52:2E"  # ← 실제 안드로이드 기기의 Bluetooth MAC 주소
    port = 1

    try:
        print(f"[🔌] Connecting to {bd_addr} ...")
        sock.connect((bd_addr, port))
        print("[✅] Connected.")

        # 테스트 JSON 데이터
        test_data = {
            "id": 123,
            "completed": 1
        }

        json_str = json.dumps(test_data) + '\n'
        sock.send(json_str.encode())
        print(f"[📤] Sent: {json_str.strip()}")

        time.sleep(1)  # 전송 후 잠시 대기

    except bluetooth.btcommon.BluetoothError as err:
        print(f"[❌] Bluetooth error: {err}")

    finally:
        sock.close()
        print("[🔚] Connection closed.")

if __name__ == "__main__":
    send_test_json()
