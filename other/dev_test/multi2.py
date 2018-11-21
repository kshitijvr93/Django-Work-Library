from multiprocessing import Process
import os
from time import sleep
import sys

def info(title):
    print(f"title={title}")
    print('module name:', __name__)
    if hasattr(os, 'getppid'):  # only available on Unix
        print ('parent process:', os.getppid())
    print ('process id:', os.getpid())
    sys.stdout.flush()

def f(name):
    info('function f')
    for i in range(10):
        print (f'hello {i}', name)
        sys.stdout.flush()
        sleep(1)
    print("goodbye from f")
    sys.stdout.flush()


if __name__ == '__main__':
    info('main line')
    print("Calling Process now...")
    sys.stdout.flush()
    p = Process(target=f, args=('bob',))
    p.start()
    print("Main - started now...")
    sys.stdout.flush()
    #p.join()
    #print("Main - joined...")
    sys.stdout.flush()
    print("Main - GOODBYE...")
    sys.stdout.flush()
