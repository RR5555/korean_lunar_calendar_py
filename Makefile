.DEFAULT_GOAL := help
NAME ?= 'korean_lunar_calendar'

docker-build: ## Build the Docker container
	docker build -t $(NAME) -f ./Docker/Dockerfile .


docker-run: ## Run the Docker container
	docker run --rm -it -v .:/root/korean_lunar_calendar \
	--name $(NAME) $(NAME)


docker-bash: ## Access container bash
	docker exec -it $(NAME) /bin/bash

dev-install: ## uv sync
	uv sync --all-groups

lint: ## Run linter [dev]
	uv run ruff check .

format: ## Run formatter [dev]
	uv run ruff format --diff .

tox-rerun: ## Launch Tox [dev, tox]
	uv run tox --parallel

tox-run: ## Launch Tox [dev, tox]
	uv run tox -r --parallel


# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
