import bluetooth
import json
import threading
import queue
import time

incoming_queue = queue.Queue()

def handle_client(client_sock):
    buffer = ""
    try:
        while True:
            data = client_sock.recv(1024).decode()
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if not line:
                    continue
                print(f"[📥] receive data: {line}")
                try:
                    message = json.loads(line)
                    print(f"[🔍] parsing JSON: {message}")
                    incoming_queue.put(message)

                    # 응답 전송
                    response = {"ack": True, "received_type": message.get("type")}
                    client_sock.send((json.dumps(response) + '\n').encode())
                    print(f"[📤] message send")
                except json.JSONDecodeError:
                    print("[⚠️] JSON parsing failed")
    except Exception as e:
        print(f"[❌] Error processing client: {e}")
    finally:
        client_sock.close()
        print("[🔌] client connect finish")

def start_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]

    bluetooth.advertise_service(
        server_sock,
        "RoutineAppServer",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print(f"[🟢] RFCOMM Bluetooth server running... port: {port}")

    try:
        while True:
            client_sock, client_info = server_sock.accept()
            print(f"[✅] connected: {client_info}")
            threading.Thread(target=handle_client, args=(client_sock,)).start()
    except KeyboardInterrupt:
        print("[🛑] server stop")
    finally:
        server_sock.close()

if __name__ == "__main__":
    start_server()
