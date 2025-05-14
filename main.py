from multiprocessing import Process
from ble_receiver import receive_bluetooth_data
from routine_runner import run_routine_loop

if __name__ == "__main__":
    p1 = Process(target=receive_bluetooth_data)
    p2 = Process(target=run_routine_loop)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
