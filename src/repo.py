from dagster import Definitions, define_asset_job
from src.assets import train_model
from src.grid_search_asset_generator import generate_grid_search_asset
from src.resources import (
    ModelConfig,
    OptMlflow,
    ParamSearchSpace,
    MlflowExperimentConfig,
)
from dagster_mlflow import end_mlflow_on_run_finished, mlflow_tracking

grid_search_assets = [
    generate_grid_search_asset(job_name) for job_name in ["train_model_job"]
]
all_assets = [train_model, *grid_search_assets]
jobs = define_asset_job(
    "train_model_job", selection=[train_model], hooks={end_mlflow_on_run_finished}
)


my_resources = {
    "model_config": ModelConfig(param_a=2, param_b=10, param_c=5),
    "mlflow": mlflow_tracking,  # Figure out why pre-configuring doesn't allow me to override afterwards.
    "opt_mlflow": OptMlflow(use_mlflow=False),
    "param_search_space": ParamSearchSpace.configure_at_launch(),
    "mlflow_experiment_config": MlflowExperimentConfig.configure_at_launch(),
}

defs = Definitions(assets=all_assets, resources=my_resources, jobs=[jobs])
