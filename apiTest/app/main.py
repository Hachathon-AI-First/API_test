from fastapi import FastAPI
from app.middleware.logging import LogMiddleware
from app.routes import auth, users, products, orders, payments, check

app = FastAPI(
    title="Legacy E-Commerce API",
    description="An intentionally flawed API for AI agent testing.",
    version="1.0.0"
)

# Add middleware
app.add_middleware(LogMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(check.router)  # Include the new check router

@app.get("/")
def root():
    return {"message": "Welcome to the Legacy API. Check /docs for endpoints."}
