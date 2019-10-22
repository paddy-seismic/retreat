import concurrent.futures
from concurrent.futures import ProcessPoolExecutor as PPE
from multiprocessing import cpu_count

# define stop process function
def stop_process_pool(executor):
    for pid, processes in executor._processes.items():
        process.terminate()
    executor.shutdown()

# define iterable checker
def isiterable(p_object):
    try:
        it = iter(p_object)
    except TypeError:
        return False
    return True

def get_nproc():
    # get number of processors to use
    try:
        workers = cpu_count() - 2
        if workers < 1:
            workers = 1
    except NotImplementedError:
        workers = 1

    return workers
