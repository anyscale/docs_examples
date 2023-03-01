from ray import serve
from transformers import pipeline
from fastapi import FastAPI

app = FastAPI()

@serve.deployment(route_prefix="/")
@serve.ingress(app)
class LanguageModel:
    def __init__(self, task="sentiment-analysis"):
        self.pipeline = pipeline(task)

    @app.get("/predict")
    async def run_prediction(self, text: str):
        assert len(text) > 0, "input text should not be empty"
        result = self.pipeline(text)
        return result

model = LanguageModel.bind()

# The following block will be executed if the script is run by Python directly
if __name__ == "__main__":
    serve.run(model)