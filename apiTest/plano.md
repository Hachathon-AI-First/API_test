# Implementation Plan: Legacy E-Commerce API (apiTest)

This plan outlines the creation of an intentionally flawed, legacy-style e-commerce API using FastAPI, designed for AI agent testing. The application will be fully functional but will contain a mix of good practices and deliberate anti-patterns, missing types, inconsistent formatting, and architectural issues as requested.

## Proposed Application Structure

The application will be located in the `apiTest` folder with the following structure:

```
apiTest/
│
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── db.py (In-memory database simulation)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   └── payments.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── order_service.py (Large, complex, some duplicate logic)
│   │   └── payment_service.py (Large, missing types, missing try/except)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py (Pydantic models, some missing)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py (Intentionally poorly formatted, unused imports)
│   └── middleware/
│       ├── __init__.py
│       └── logging.py (Simple middleware)
```

## Intentional Flaws Map

Here is how the deliberate issues will be distributed across the application:

### Missing Type Hints & Docstrings
- `routes/auth.py` and `routes/payments.py` will have missing or partial type hints.
- `services/payment_service.py` will lack docstrings and type hints.

### Synchronous vs Asynchronous
- `routes/users.py` and `routes/products.py` will use `async def`.
- `routes/orders.py` and `routes/payments.py` will use `def` (sync) to simulate blocking legacy code.

### Bad Formatting & Unused Imports
- `utils/helpers.py` will have inconsistent indentation, unused imports (e.g., `import os`, `import sys`), and poorly named variables (e.g., `def x(y): return y*2`).

### Inconsistent Responses & Missing Try/Except
- `routes/products.py` will return Pydantic models.
- `routes/users.py` will return raw dictionaries `{"user_id": 1, "name": "Test"}` instead of models.
- `services/payment_service.py` will have raw dictionary manipulations without `try/except` for key errors.

### Large Services & Duplication
- `services/order_service.py` will be a "God object" style service with overly long functions and duplicate logic for calculating totals and applying discounts.

### TODO and FIXME Comments
- Sprinkled across `routes/orders.py` and `services/order_service.py` indicating technical debt (e.g., `# FIXME: move this to database`, `# TODO: add authentication check here`).

### MCP Compatibility
- **Good MCP Candidate**: `routes/products.py` (has clear inputs/outputs, Pydantic models, no side effects).
- **Bad MCP Candidate**: `routes/payments.py` (stateful, relies on request headers/context, sync blocking, poorly typed).

## Verification Plan

1. Create the `apiTest` directory and all files.
2. Initialize a `.venv` using `python -m venv .venv`.
3. Install dependencies (`fastapi`, `uvicorn`, `pydantic`).
4. Run `uvicorn app.main:app --reload` to ensure the application starts without crashing.
5. Manually test a few endpoints via the `/docs` Swagger UI to ensure the API works despite its intentional flaws.

## User Review Required

> [!IMPORTANT]
> Please review the distribution of intentional flaws above. Are these the kinds of anti-patterns and inconsistencies you want your AI agent to detect? If approved, I will generate the complete application.
