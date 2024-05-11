from dagster import (
    ConfigurableResource,
    resource,
    InitResourceContext,
    PermissiveConfig,
)
from pydantic import Field
from dagster_mlflow.resources import MlFlow


class ModelConfig(ConfigurableResource):
    """Config for ML model."""

    param_a: int
    param_b: int
    param_c: int


class ParamSearchSpace(PermissiveConfig, ConfigurableResource):
    """Provide params in a list per ModelConfig.

    Example:
        ParamSearchSpace:
            Config:
                model_1_config:
                    param_a: [1,2,3,4]
                    param_b: [10,20]
                model_2_config:
                    param_a: [10,20]
                    param_b: [50]
    """

    pass


class MlflowExperimentConfig(ConfigurableResource):
    """Config for ML model."""

    experiment_name: str
    mlflow_tracking_uri: str = Field(default="http://localhost:5000")
    parent_run_id: str | None
    extra_tags: dict = Field(default={})


class OptMlflow(ConfigurableResource):
    use_mlflow: bool = Field(default=False)
