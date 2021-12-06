from fastapi import FastAPI
from ray import serve

serve.start(detached=True)

app = FastAPI()

@serve.deployment(route_prefix="/")
@serve.ingress(app)
class HelloWorld:
    @app.get("/")
    def hello(self):
        return f"Hello world!"
    
    @app.get("/health")
    def healthcheck(self):
        return

HelloWorld.deploy()
