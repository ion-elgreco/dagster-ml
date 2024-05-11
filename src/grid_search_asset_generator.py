from dagster import asset, AssetExecutionContext, AssetsDefinition
from src.resources import (
    ParamSearchSpace,
    MlflowExperimentConfig,
)
from dagster_graphql import DagsterGraphQLClient
from sklearn.model_selection import ParameterGrid
from typing import Any
from itertools import product


def generate_grid_search_asset(job_name: str) -> AssetsDefinition:
    @asset(name=f"{job_name}_grid_search")
    def grid_search_asset(
        context: AssetExecutionContext,
        param_search_space: ParamSearchSpace,
        mlflow_experiment_config: MlflowExperimentConfig,
    ):
        client = DagsterGraphQLClient("localhost", port_number=3000)
        search_space = param_search_space.model_dump()
        param_combinations = _generate_param_combinations(search_space)
        model_config_combinations = _generate_config_combinations(param_combinations)

        submitted_jobs = []
        for combination in model_config_combinations:
            mlflow_config = mlflow_experiment_config.model_dump()
            combination["mlflow"] = {"config": mlflow_config}
            combination["opt_mlflow"] = {"config": {"use_mlflow": True}}
            run_config = {"resources": combination}
            submitted_jobs.append(
                client.submit_job_execution(job_name, run_config=run_config)
            )
        context.log.info("Submitted dagster jobs: %s", submitted_jobs)

    return grid_search_asset


def _generate_param_combinations(search_space: dict[str, Any]):
    param_combinations = {}
    for model_config in search_space.keys():
        grid = ParameterGrid(search_space[model_config])
        for params in grid:
            if model_config in param_combinations:
                param_combinations[model_config].append(params)
            else:
                param_combinations[model_config] = [params]

    return param_combinations


def _generate_config_combinations(config_dict):
    combinations = []
    model_names = list(config_dict.keys())
    model_configs = list(config_dict.values())

    for config_combination in product(*model_configs):
        run_config = {}
        for i, config in enumerate(config_combination):
            model_name = model_names[i]
            run_config[model_name] = {"config": config}
        combinations.append(run_config)

    return combinations
