import time
import ray

@ray.remote
def fn():
    print("Started function")
    i = 0
    while True:
        print(f"Sleeping for 180 sec {i}")
        time.sleep(180)
        i += 1

ray.get(fn.remote())