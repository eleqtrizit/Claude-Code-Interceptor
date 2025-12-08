.PHONY: help install dev test lint format clean cov

help:  ## Show this help message
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	uv sync

install-prod:  ## Install with development dependencies
	uv sync --no-dev

test:  ## Run tests
	pytest tests/ -v

cov:  ## Run tests with coverage report
	pytest tests/ --cov=cci --cov-report=term-missing --cov-report=html

lint:  ## Run linters
	flake8 cci/ tests/
	mypy cci/ tests/

format:  ## Format code
	autopep8 -a  --in-place --recursive .

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build


run:
	python -m claude_code_intercept
