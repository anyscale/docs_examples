import ray
from ray import tune
from ray.air.callbacks import wandb as wandb_integration
from ray.rllib.algorithms import appo
from ray.rllib.examples.env.multi_agent import MultiAgentCartPole
from ray.rllib.policy import policy

ray.init(
    ignore_reinit_error=True,
    runtime_env={"working_dir": ".", "excludes": [".git", "wandb/"]},
)

config = {
    "env": MultiAgentCartPole,
    "env_config": {
        "num_agents": 2,
    },
    "framework": "tf",
    "num_gpus": 0,
    "num_workers": 2,
    "evaluation_num_workers": 2,
    "min_time_s_per_iteration": 60,
    "multiagent": {
        "policies": {"main_agent": policy.PolicySpec()},
        "policy_mapping_fn": (lambda agent_id, episode, **kwargs: "main_agent"),
        "policies_to_train": ["main_agent"],
    },
    "evaluation_interval": 1,
    "evaluation_duration": "auto",
    "evaluation_parallel_to_training": True,
}

tune.run(
    appo.APPO,
    config=config,
    verbose=1,
    callbacks=[
        wandb_integration.WandbLoggerCallback(
            entity="aia-lion",
            project="Lion-2x2-9",
            group="Wandb test",
            log_config=False,
            resume=True,
        )
    ],
)
