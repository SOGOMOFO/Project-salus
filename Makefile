.PHONY: help install test run smoke clean docker-build docker-up docker-down docker-logs status snapshot

help:
	@echo "Project Salus commands"
	@echo "  make install       Install dependencies"
	@echo "  make test          Run tests"
	@echo "  make run           Run local dev server"
	@echo "  make smoke         Run local smoke checks"
	@echo "  make status        Show git/app status"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start Docker Compose"
	@echo "  make docker-down   Stop Docker Compose"
	@echo "  make docker-logs   Tail Docker logs"
	@echo "  make clean         Remove local caches"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest

run:
	python -m uvicorn backend.main:app --reload --port 8010

smoke:
	bash scripts/smoke_check.sh

status:
	git status
	python scripts/startup_check.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
