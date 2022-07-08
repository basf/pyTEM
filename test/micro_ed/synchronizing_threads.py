import threading
import time
from pathos.helpers import mp


class MyThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + str(self.name))
        # Get lock to synchronize threads
        threadLock.acquire()
        print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()


class MyProcess(mp.Process):
    def __init__(self, process_id, name, counter):
        mp.Process.__init__(self)
        self.process_id = process_id
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + str(self.name))
        # Get lock to synchronize threads
        # threadLock.acquire()
        print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        # threadLock.release()

    def join(self, *args):
        return self.name


def print_time(thread_name, delay, counter):
    while counter:
        time.sleep(delay)
        print(str(thread_name) + "  " + str(time.ctime(time.time())))
        counter -= 1


if __name__ == "__main__":

    print("Thread testing...")
    threadLock = threading.Lock()
    threads = []

    # Create threads
    thread1 = MyThread(1, "Thread-1", 1)
    thread2 = MyThread(2, "Thread-2", 2)

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("Process testing...")
    processes = []

    # Create processes
    process1 = MyProcess(1, "Process-1", 1)
    process2 = MyProcess(2, "Process-2", 2)

    # Start new Threads
    process1.start()
    status = process1.is_alive()
    print(status)
    process2.start()

    # Add threads to thread list
    processes.append(process1)
    processes.append(process2)

    # Wait for all threads to complete
    for p in processes:
        print(str(p.join()) + " has joined.")

    # We are now all done
    print("\nExiting Main Thread")
