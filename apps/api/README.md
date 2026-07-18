# Sentinel AI API

This is the API backend for Sentinel AI, built with Python 3.12/3.13 and FastAPI.

## Directory Structure

- `src/sentinel_api`: Root Python package containing core modules (config, database, logging), APIs, models, schemas, and services.
- `tests`: Unit and integration testing harness.

## Local Setup

1. Create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run the development server:
   ```bash
   uvicorn sentinel_api.main:app --reload
   ```
