import time
import ray

@ray.remote
def fn():
    print("Started function")
    time.sleep(180)
    print("Finished sleeping")
    1/0

ray.get(fn.remote())