from dagster import (
    ConfigurableResource,
    InitResourceContext,
    PermissiveConfig,
)
from pydantic import Field
from dagster_mlflow.resources import MlFlow
import mlflow


class ModelConfig(ConfigurableResource):
    """Config for ML model."""

    param_a: int
    param_b: int
    param_c: int


class ParamSearchSpace(PermissiveConfig, ConfigurableResource):
    """Provide params in a list per ModelConfig. Pass this dict to
    resources: {"param_search_space": ParamSearchSpace()} in defintions object, and
    below there is an example of how you configure the resource in launchpad.

    Example:
        param_search_space:
            config:
                model_1_config:
                    param_a: [1,2,3,4]
                    param_b: [10,20]
                model_2_config:
                    param_a: [10,20]
                    param_b: [50]
    """

    pass


class MlflowExperimentConfig(ConfigurableResource):
    """Config for MLFlow experiment."""

    experiment_name: str
    mlflow_tracking_uri: str = Field(default="http://localhost:5000")
    parent_run_id: str | None
    extra_tags: dict = Field(default={})


class mCustomMlflow(type(ConfigurableResource), type(MlFlow)):
    pass


class ConfigurableMlflow(ConfigurableResource, MlFlow, metaclass=mCustomMlflow):
    mlflow_tracking_uri: str = Field(default="http://localhost:5000")
    experiment_name: str = Field(default="DEFAULT_EXPERIMENT")
    parent_run_id: str | None = Field(default=None)
    env_tags_to_log: list = Field(default=[], alias="env_to_tag")
    extra_tags: dict = Field(default={})
    use_mlflow: bool = Field(default=False)

    class Config:
        frozen = False
        extra = "allow"

    def setup_for_execution(self, context: InitResourceContext) -> None:
        if not self.use_mlflow:
            # Just no-ops and doesn't set any experiment and runs.
            return
        self.log = context.log
        if context.dagster_run is not None:
            self.run_name = context.dagster_run.job_name
        else:
            raise ValueError("dagster_run should be available at this point in time.")
        self.dagster_run_id = context.run_id

        # If the experiment exists then the set won't do anything
        mlflow.set_experiment(self.experiment_name)
        self.experiment = mlflow.get_experiment_by_name(self.experiment_name)

        # Get the client object
        self.tracking_client = mlflow.tracking.MlflowClient()

        # Set up the active run and tags
        self._setup()

    def teardown_after_execution(self, context: InitResourceContext) -> None:
        if not self.use_mlflow:
            return
        self.cleanup_on_error()
