import numpy as np
import wandb

import ray
from ray import tune
from ray.tune import Trainable
from ray.air.callbacks.wandb import WandbLoggerCallback

def objective(config, checkpoint_dir=None):
    for i in range(30):
        loss = config["mean"]
        tune.report(loss=loss, nodes=ray.nodes())

def tune_function():
    """Example for using a WandbLoggerCallback with the function API"""
    analysis = tune.run(
        objective,
        metric="loss",
        mode="min",
        config={
            "mean": tune.grid_search([1, 2, 3, 4, 5]),
        },
        callbacks=[
            WandbLoggerCallback(project="test_proj_override", group="test_group_override")
        ],
    )
    return analysis.best_config


tune_function()