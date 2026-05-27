# TRACE Data Ingestion Pipeline - Backend Task

## Overview
This repository contains the backend implementation for the TRACE field agent data ingestion pipeline. It is built using **FastAPI** to handle highly concurrent, asynchronous data submissions from mobile clients operating in low-connectivity environments.

## Architecture & Design Decisions
* **Validation Layer:** Utilizes Pydantic `BaseModel` for strict data schema enforcement. Custom `@field_validator` methods are implemented to catch formatting errors (e.g., Nigerian National ID regex) before the data reaches the application logic.
* **Granular Error Handling:** A custom exception handler overrides default `RequestValidationError` responses. It flattens nested error arrays into a clean `{"field": "error_message"}` dictionary, allowing the Mobile App to easily map errors to specific inline UI inputs.
* **In-Memory Store:** Implements a localized Python dictionary for `db_farms` to fulfill the task requirements without requiring external PostgreSQL/Docker setup for the reviewer.
* **Idempotency & State:** Designed with offline-first mobile clients in mind, returning fully updated resource objects on state changes to prevent unnecessary secondary `GET` requests.

## Setup & Running the API
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `uvicorn main:app --reload`
3. The API will be available at: `http://127.0.0.1:8000`
4. Interactive Swagger documentation: `http://127.0.0.1:8000/docs`

## Running Tests
Run `pytest` in the root directory. The test suite covers successful ingestion, duplicate 409 conflicts, GPS boundary limits, Enum constraints, and missing field validation.