from typing import Any, Dict

from ray import serve

from fastapi import FastAPI

f = FastAPI()

@serve.deployment(user_config={"model_path": "/mnt/shared_storage/model_v0"})
@serve.ingress(f)
class ModelLoader:
    def reconfigure(self, d: Dict[str, Any]):
        self._path = d["model_path"]
        print(f"Loading model from path: {self._path}")

    @f.get("/")
    def predict(self) -> str:
        return f"Response from model at {self._path}"

d = ModelLoader.bind()
