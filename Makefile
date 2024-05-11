
SHELL=/bin/bash

venv:  ## Set up virtual environment
	pip install --upgrade uv
	uv venv
	uv pip install -r requirements.txt

lint: venv ## Run linter
	unset CONDA_PREFIX && \
	source venv/bin/activate && ruff check --fix .

format: venv ## Run formatters
	unset CONDA_PREFIX && \
	source venv/bin/activate && ruff format .

clean: ## Clean venv
	-@rm -r .venv

.PHONY: help
help:  ## Display this help screen
	@echo -e "\033[1mAvailable commands:\033[0m"
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' | sort