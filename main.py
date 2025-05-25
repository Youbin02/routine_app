from multiprocessing import Process
from rfcomm_server import start_rfcomm_server
from routine_runner import run_routine_loop

if __name__ == "__main__":
    try:
        p1 = Process(target=start_rfcomm_server)
        p2 = Process(target=run_routine_loop)

        p1.start()
        p2.start()

        p1.join()
        p2.join()

    except KeyboardInterrupt:
        print("[🛑] main proccess stopped")
