# test_ble_send.py
from ble_sender import send_json_via_ble

test_data = {
    "type": "routine",
    "routine": {
        "id": 999,
        "date": "2025-05-23",
        "start_time": "08:00:00",
        "routine_minutes": 10,
        "icon": "test.png",
        "completed": 1,
        "routine_name": "test routine",
        "group_routine_name": "test group"
    }
}

send_json_via_ble(test_data)
