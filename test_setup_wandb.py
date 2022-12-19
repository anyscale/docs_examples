import numpy as np
import wandb

import ray
from ray import tune
from ray.tune import Trainable
from ray.air.callbacks.wandb import setup_wandb

def train_function_wandb(config):
    wandb = setup_wandb(config)

    for i in range(30):
        loss = config["mean"] * np.random.randn()
        wandb.log(dict(loss=loss))
        tune.report(loss=loss, nodes=ray.nodes())


def tune_function():
    """Example for using a WandbLoggerCallback with the function API"""
    analysis = tune.run(
        train_function_wandb,
        metric="loss",
        mode="min",
        config={
            "mean": tune.grid_search([1, 2, 3, 4, 5]),
        },
    )
    return analysis.best_config

tune_function()