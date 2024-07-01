# Makefile for managing Poetry and Docker Compose

# Variables
POETRY := poetry
PYPROJECT_DIR := controller
DOCKER_COMPOSE := docker-compose

# Default target
.PHONY: all
all: help

# Help target
.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install project dependencies"
	@echo "  update           Update project dependencies"
	@echo "  lock             Generate poetry.lock file"
	@echo "  run              Run the application"
	@echo "  shell            Start a shell within the virtual environment"
	@echo "  check            Check the dependency status"
	@echo "  clean            Clean up the environment"
	@echo "  dc-up            Start Docker Compose services"
	@echo "  dc-down          Stop Docker Compose services"
	@echo "  dc-restart       Restart Docker Compose services"
	@echo "  dc-logs          View Docker Compose logs"

# Poetry targets
.PHONY: install
install:
	cd $(PYPROJECT_DIR) && $(POETRY) install

.PHONY: update
update:
	cd $(PYPROJECT_DIR) && $(POETRY) update

.PHONY: lock
lock:
	cd $(PYPROJECT_DIR) && $(POETRY) lock

.PHONY: run
run:
	cd $(PYPROJECT_DIR) && $(POETRY) run python -m controller

.PHONY: shell
shell:
	cd $(PYPROJECT_DIR) && $(POETRY) shell

.PHONY: check
check:
	cd $(PYPROJECT_DIR) && $(POETRY) check

.PHONY: clean
clean:
	cd $(PYPROJECT_DIR) && $(POETRY) env remove --all

# Docker Compose targets
.PHONY: dc-up
dc-up:
	$(DOCKER_COMPOSE) up -d

.PHONY: dc-down
dc-down:
	$(DOCKER_COMPOSE) down

.PHONY: dc-restart
dc-restart: dc-down dc-up

.PHONY: dc-logs
dc-logs:
	$(DOCKER_COMPOSE) logs -f
