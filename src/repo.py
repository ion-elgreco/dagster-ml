from dagster import Definitions, define_asset_job
from src.assets import train_model
from src.search_asset_generator import (
    generate_optuna_search_asset,
)
from src.resources import (
    ModelConfig,
    ParamSearchSpace,
    MlflowExperimentConfig,
    ConfigurableMlflow,
    OptunaParamSearchSpace,
    OptunaConfig,
)
from dagster_mlflow import end_mlflow_on_run_finished

optuna_search_assets = [
    generate_optuna_search_asset(job_name) for job_name in ["train_model_job"]
]
all_assets = [train_model, *optuna_search_assets]
jobs = define_asset_job(
    "train_model_job", selection=[train_model], hooks={end_mlflow_on_run_finished}
)

my_resources = {
    "model_config": ModelConfig(param_a=2, param_b=10, param_c=5),
    "mlflow": ConfigurableMlflow(),
    "param_search_space": ParamSearchSpace.configure_at_launch(),
    "mlflow_experiment_config": MlflowExperimentConfig.configure_at_launch(),
    "optuna_config": OptunaConfig.configure_at_launch(),
    "optuna_param_search_space": OptunaParamSearchSpace.configure_at_launch(),
}

defs = Definitions(assets=all_assets, resources=my_resources, jobs=[jobs])
