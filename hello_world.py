import ray
import anyscale
import time

@ray.remote
def say_hi(message):
    time.sleep(360)
    return f"Hello, {message}."

ray.init()
print(ray.get(say_hi.remote("World")))
