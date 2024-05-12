from dagster import asset, AssetExecutionContext, AssetsDefinition
from src.resources import (
    ParamSearchSpace,
    MlflowExperimentConfig,
    OptunaParamSearchSpace,
    OptunaConfig,
)
from dagster_graphql import DagsterGraphQLClient
from sklearn.model_selection import ParameterGrid
from typing import Any
from itertools import product
from optuna import Trial
import optuna

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
            mlflow_config["use_mlflow"] = True
            combination["mlflow"] = {"config": mlflow_config}
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

import random
def generate_optuna_search_asset(job_name: str) -> AssetsDefinition:
    @asset(name=f"{job_name}_optuna_search")
    def fortuna_search_asset(
        context: AssetExecutionContext,
        optuna_param_search_space: OptunaParamSearchSpace,
        mlflow_experiment_config: MlflowExperimentConfig,
        optuna_config: OptunaConfig,
    ):
        search_space = optuna_param_search_space.model_dump()
        mlflow_config = mlflow_experiment_config.model_dump()
        mlflow_config["use_mlflow"] = True
        
        def objective(trial: Trial):
            client = DagsterGraphQLClient("localhost", port_number=3000)
            resources_config = {}
            resources_config["mlflow"] = {"config": mlflow_config}
            
            for model_config, params_def in search_space.items():
                resources_config[model_config] = {"config": {}}
                for param, param_def in params_def.items():
                    model_param_log = f"{model_config}__{param}"
                    if isinstance(param_def, list):
                        trial.suggest_categorical(model_param_log, param_def)
                    elif isinstance(param_def['low'], int) and isinstance(param_def['high'], int):
                        trial.suggest_int(
                            model_param_log,
                            low=param_def['low'],
                            high=param_def['high'],
                            step=param_def.get('step', 1),
                            log=param_def.get('log', False)
                        )
                    elif isinstance(param_def['low'], float) and isinstance(param_def['high'], float):
                        trial.suggest_float(
                            model_param_log,
                            low=param_def['low'],
                            high=param_def['high'],
                            step=param_def.get('step', 1),
                            log=param_def.get('log', False)
                        )
            run_config = {"resources": resources_config}
            submitted_job = client.submit_job_execution(job_name, run_config=run_config)
            context.log.info("Submitted dagster jobs: %s", submitted_job)
            return random.random()
        
        
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=optuna_config.n_trials, n_jobs=optuna_config.n_jobs, show_progress_bar=True)
        
    return fortuna_search_asset