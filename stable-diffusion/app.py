from io import BytesIO

import numpy as np
from PIL import Image
from ray import serve
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()


@serve.deployment(
    ray_actor_options={"num_gpus": 1},
    # num_replicas=1,
    autoscaling_config={"min_replicas": 0, "max_replicas": 2},
    route_prefix="/",
)
@serve.ingress(app)
class StableDifussionV2:
    def __init__(self):
        import numpy as np
        import torch
        from diffusers import EulerDiscreteScheduler, StableDiffusionPipeline

        model_id = "stabilityai/stable-diffusion-2"

        # Use the Euler scheduler here instead
        scheduler = EulerDiscreteScheduler.from_pretrained(
            model_id, subfolder="scheduler"
        )
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float16
        )
        self.pipe = self.pipe.to("cuda")

    @app.get(
        "/imagine",
        responses={200: {"content": {"image/png": {}}}},
        response_class=Response,
    )
    def generate(self, prompt: str, img_size: int = 512):
        assert len(prompt), "prompt parameter cannot be empty"

        image = self.pipe(prompt, height=img_size, width=img_size).images[0]

        file_stream = BytesIO()
        image.save(file_stream, "PNG")
        return Response(content=file_stream.getvalue(), media_type="image/png")


v2_model = StableDifussionV2.bind()
