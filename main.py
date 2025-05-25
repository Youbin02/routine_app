from multiprocessing import Process
from rfcomm_server import start_server
from routine_runner import run_routine_runner

if __name__ == "__main__":
    p1 = Process(target=start_server)
    p2 = Process(target=run_routine_runner)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
