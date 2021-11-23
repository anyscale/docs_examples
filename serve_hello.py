import ray
from ray import serve

ray.init()

serve.start(detached=True)

@serve.deployment
def healthcheck():
   return

@serve.deployment
def hello(request):
   name = request.query_params["name"]
   return f"Hello {name}!"

hello.deploy()
