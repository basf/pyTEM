import threading
import time

import multiprocessing as mp

# from pathos.helpers import mp
# from multiprocessing.managers import BaseManager


class MyThread(threading.Thread):
    def __init__(self, thread_id, lock, name, counter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.lock = lock
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + str(self.name))
        # Get lock to synchronize threads
        self.lock.acquire()
        print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        self.lock.release()


class MyProcess(mp.Process):
    def __init__(self, process_id, barrier, name, counter):
        mp.Process.__init__(self)
        self.process_id = process_id
        self.barrier = barrier
        self.name = name
        self.counter = counter
        self.end_time = None

    def run(self):
        print("Starting " + str(self.name))

        # with self.lock:
        #     MyManager.register('get_barrier')
        #     manager = MyManager(address=('localhost', 5555), authkey=b'akey')
        #     manager.connect()
        #     barrier = manager.get_barrier()
        #     print("Got the barrier from the manager")

        # Get lock to synchronize threads
        # threadLock.acquire()
        print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        # threadLock.release()
        print("Waiting at the barrier...")
        self.barrier.wait()
        print(time.time())

    def join(self, *args) -> str:
        mp.Process.join(self, *args)
        return self.name


class ProcessWithBarrier(mp.Process):
    def __init__(self, process_id, barrier, barrier2, name):
        mp.Process.__init__(self)
        self.process_id = process_id
        self.barrier = barrier
        self.barrier2 = barrier2
        self.name = name

    def run(self):
        print("Starting " + str(self.name))
        time.sleep(3)
        self.barrier.wait()  # Note: We should use locks here to prevent stuff from printing at exactly the same time.
        print(str(self.name) + " moving on from barrier 1 at " + str(time.time()))

        self.barrier2.wait()
        print(str(self.name) + " moving on from barrier 2 at " + str(time.time()))

    def join(self, *args) -> str:
        mp.Process.join(self, *args)
        return self.name


def print_time(thread_name, delay, counter):
    while counter:
        time.sleep(delay)
        print(str(thread_name) + "  " + str(time.ctime(time.time())))
        counter -= 1


if __name__ == "__main__":

    """ Thread testing """
    # print("Thread testing...")
    # threadLock = threading.Lock()
    # threads = []
    #
    # # Create threads
    # thread1 = MyThread(1, "Thread-1", 1)
    # thread2 = MyThread(2, "Thread-2", 2)
    #
    # # Start new Threads
    # thread1.start()
    # thread2.start()
    #
    # # Add threads to thread list
    # threads.append(thread1)
    # threads.append(thread2)
    #
    # # Wait for all threads to complete
    # for t in threads:
    #     t.join()


    """ Process testing """
    # print("Process testing...")
    #
    # barrier_ = mp.Barrier(2)
    #
    # # Create processes
    # process1 = MyProcess(1, barrier_, "Process-1", 1)
    # process2 = MyProcess(2, barrier_, "Process-2", 2)
    #
    # # Start the new processes
    # process1.start()
    # # print("Process 1 is alive: " + str(process1.is_alive()))
    # process2.start()
    #
    # # Add processes to process list
    # processes = [process1, process2]
    #
    # # Wait for all threads to complete
    # for p in processes:
    #     print(str(p.join()) + " joined at " + str(time.time()))


    """ Barrier testing """
    print("Barrier testing...")
    lock_ = mp.Lock()

    barrier_ = mp.Barrier(2)
    barrier2_ = mp.Barrier(2)
    # MyManager.register('get_barrier', callable=lambda: barrier)
    # manager_ = MyManager(address=('localhost', 5555), authkey=b'akey')
    # manager_.start()

    # Create processes
    process1 = ProcessWithBarrier(1, barrier_, barrier2_, "Process-1")

    # Start the new processes
    process1.start()

    barrier_.wait()  # Wait for the process to start
    print("Main moving on from barrier 1 at " + str(time.time()))

    time.sleep(3)
    barrier2_.wait()
    print("Main moving on from barrier 2 at " + str(time.time()))

    # Wait for all threads to complete
    print(str(process1.join()) + " joined at " + str(time.time()))

    # We are now all done
    print("\nExiting Main Thread")
