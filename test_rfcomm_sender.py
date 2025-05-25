import bluetooth
import json
import logging

logging.basicConfig(level=logging.INFO)

def start_test_rfcomm_server():
    try:
        # RFCOMM 서버 소켓 생성 및 바인딩
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        port = 1
        server_sock.bind(("", port))
        server_sock.listen(1)

        logging.info("[🔌] Bluetooth RFCOMM 서버 대기 중...")
        client_sock, client_info = server_sock.accept()
        logging.info(f"[✅] 클라이언트 연결됨: {client_info}")

        # 테스트용 데이터 전송
        test_data = {
            "id": 123,
            "completed": 1
        }

        json_str = json.dumps(test_data) + '\n'
        client_sock.send(json_str.encode())
        logging.info(f"[📤] 전송됨: {json_str.strip()}")

        # 추가로 수신 테스트도 하고 싶다면 여기에 recv() 추가 가능
        # 예:
        # data = client_sock.recv(1024)
        # logging.info(f"받은 데이터: {data}")

    except bluetooth.BluetoothError as e:
        logging.error(f"[❌] Bluetooth 오류: {e}")
    finally:
        try:
            client_sock.close()
            server_sock.close()
            logging.info("[🔚] 연결 종료")
        except:
            pass

if __name__ == "__main__":
    start_test_rfcomm_server()
