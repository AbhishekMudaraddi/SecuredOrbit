.PHONY: install test run clean docker-build docker-run

# Variables
VENV = .venv
PYTHON = python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
PYTHON_CMD = $(VENV)/bin/python

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  make install    - Create virtual environment and install dependencies"
	@echo "  make test       - Run tests with pytest and coverage"
	@echo "  make run        - Run the Flask application"
	@echo "  make clean      - Remove virtual environment and generated files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"

install:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Installation complete! Activate with: source $(VENV)/bin/activate"

test:
	@echo "Running tests..."
	@mkdir -p reports
	$(PYTEST) tests/ -v

run:
	@echo "Starting Flask application..."
	$(PYTHON_CMD) app.py

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf reports
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

docker-build:
	@echo "Building Docker image..."
	docker build -t password-manager:local .

docker-run:
	@echo "Running Docker container..."
	@echo "Note: Make sure AWS credentials are set in your environment or .env file"
	@if [ -f .env ]; then \
		docker run -p 5001:5001 --env-file .env password-manager:local; \
	else \
		echo "Warning: .env file not found. Using environment variables from shell."; \
		docker run -p 5001:5001 \
			--env PORT=$${PORT:-5001} \
			--env AWS_ACCESS_KEY_ID \
			--env AWS_SECRET_ACCESS_KEY \
			--env AWS_REGION \
			--env AWS_ENDPOINT \
			--env SESSION_SECRET \
			--env DYNAMODB_USERS_TABLE \
			--env DYNAMODB_ACCOUNTS_TABLE \
			--env DYNAMODB_PASSWORDS_TABLE \
			password-manager:local; \
	fi

