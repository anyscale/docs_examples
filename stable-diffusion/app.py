from io import BytesIO

import numpy as np
from PIL import Image
from ray import serve
from starlette.responses import Response


@serve.deployment(
    ray_actor_options={"num_gpus": 1},
    autoscaling_config={"min_replicas": 0, "max_replicas": 1},
    route_prefix="/diffusion",
)
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

    async def __call__(self, prompt_request):
        prompt: str = prompt_request.query_params["prompt"]
        assert len(prompt), "prompt parameter cannot be empty"

        image = self.pipe(prompt, height=768, width=768).images[0]

        file_stream = BytesIO()
        image.save(file_stream, "PNG")
        return Response(content=file_stream.getvalue(), media_type="image/png")


v2_model = StableDifussionV2.bind()
