from fastapi import FastAPI
from ray import serve

msg = os.getenv("MSG", "Hello world!")

# Let serve HTTP server listen on all network interfaces
# so deployment is available throughout the Anyscale cloud.
serve.start(detached=True, http_options={"host": "0.0.0.0"})

app = FastAPI()

@serve.deployment(route_prefix="/")
@serve.ingress(app)
class HelloWorld:
    @app.get("/")
    def hello(self):
        return msg
    
    @app.get("/healthcheck")
    def healthcheck(self):
        return

HelloWorld.deploy()
