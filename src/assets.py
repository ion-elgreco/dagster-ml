from dagster import asset, AssetExecutionContext
from src.resources import ModelConfig, ConfigurableMlflow
import random


@asset(
    description="training the ML Model",
    code_version="1",
)
def train_model(
    context: AssetExecutionContext,
    model_config: ModelConfig,
    mlflow: ConfigurableMlflow,
):
    if context.resources.mlflow.use_mlflow:
        mlflow.log_params(model_config.model_dump())
        mlflow.log_metric("val_loss", random.random())
    else:
        print("production run, so no mlflow used.")
