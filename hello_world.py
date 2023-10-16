import ray


@ray.remote
def hello_world():
    return "Hello World!"


result = ray.get(hello_world.remote())
print(result)
