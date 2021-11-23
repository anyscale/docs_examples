import ray
import anyscale

@ray.remote
def say_hi(message):
    return f"Hello, {message}."

ray.init()
print(ray.get(say_hi.remote("World")))
