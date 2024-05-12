from src.repo import optuna_search_assets, my_resources
from dagster import materialize


materialize(
    optuna_search_assets,
    resources=my_resources,
    run_config={
        "resources": {
            "mlflow_experiment_config": {
                "config": {
                    "mlflow_tracking_uri": "http://localhost:5000",
                    "experiment_name": "test_optuna_retrieve",
                }
            },
            "optuna_config": {
                "config": {
                    "n_jobs": 20,
                    "n_trials": 50,
                    "metric_name": "val_loss",
                    "direction": "MINIMIZE",
                }
            },
            "optuna_param_search_space": {
                "config": {
                    "model_config": {
                        "param_a": {"high": 10, "low": 2, "step": 2},
                        "param_b": [10, 1, 5, 9],
                        "param_c": [5],
                    }
                }
            },
        }
    },
)
