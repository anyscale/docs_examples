import ray
import os

print("DEBUG environ in job: ", os.environ)

@ray.remote
def get_environ_of_remote_task():
	print("DEBUG environ in remote task: ", os.environ)

ray.get(get_environ_of_remote_task.remote())