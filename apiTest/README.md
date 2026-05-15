# Legacy E-Commerce API (apiTest) Walkthrough

The legacy e-commerce API has been successfully generated based on the implementation plan. The application contains all the requested intentional flaws to simulate a real-world, slightly inconsistent backend system for testing your AI agent.

## What Was Accomplished

1. **Application Structure**: Created a modular FastAPI project in `apiTest/app` containing `main.py`, routers, services, models, middleware, and a simulated in-memory database.
2. **Environment Setup**: Created a standard Python `.venv` inside `apiTest/` and installed the dependencies (FastAPI, Uvicorn, Pydantic) using standard `pip`.
3. **Intentional Flaws Implemented**:
   - **Type Hints Missing**: Endpoints in `routes/auth.py` and functions in `services/payment_service.py` lack type hints.
   - **Async/Sync Mix**: `products` and `users` routes use `async def`, while `orders` and `payments` simulate legacy blocking code with standard `def`.
   - **Formatting & Code Smells**: `utils/helpers.py` features unused imports, confusing variable names, and bad indentation. `order_service.py` acts as a "God object" with large functions and duplicated discount logic.
   - **Response Inconsistencies**: `users.py` returns raw dictionaries directly, whereas `products.py` correctly uses Pydantic `response_model`s.
   - **Missing Try/Except**: `payment_service.py` performs key lookups without appropriate error handling.
   - **Technical Debt Comments**: `TODO` and `FIXME` comments were scattered throughout the code.
   - **MCP Candidates**: `products.py` was created as an ideal, clean MCP candidate. In contrast, `payments.py` acts as a problematic MCP candidate since it behaves strangely based on request headers (`x-custom-header`) and has side effects without proper type definitions.

## How to Run and Verify

You can run the application directly from your terminal. Make sure you are in the `apiTest` directory:

```bash
cd apiTest
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Once running, navigate to `http://127.0.0.1:8000/docs` in your browser. You will see the interactive Swagger documentation where you can test out all the endpoints and see how the AI agent might interact with or document them.

> [!NOTE]
> The dependencies were kept minimal (`fastapi`, `uvicorn`, `pydantic`) and were installed exclusively using `pip` within the local `.venv`, as requested.
