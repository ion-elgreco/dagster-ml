from dagster import asset, AssetExecutionContext
from src.resources import (
    ModelConfig,
)
from dagster_mlflow.resources import MlFlow


@asset(
    description="training the ML Model",
    code_version="1",
    required_resource_keys={"opt_mlflow", "model_config", "mlflow"},
)
def train_model(context: AssetExecutionContext):
    if context.resources.opt_mlflow.use_mlflow:
        mlflow: MlFlow = context.resources.mlflow
        model_config: ModelConfig = context.resources.model_config
        context.log.info(
            "Loggin params to mlflow experiment: %s", mlflow.experiment_name
        )
        mlflow.log_params(model_config.model_dump())
    else:
        print("production run, so no mlflow used.")
