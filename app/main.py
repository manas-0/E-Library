from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import books

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Automatically creates all database tables defined in the SQLAlchemy models 
    when the server starts up. (Note: In a true production environment, 
    a migration tool like Alembic is preferred).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Yield control back to the application to start accepting requests
    yield
    
    # (Any shutdown logic, like closing connection pools, would go here)

# Initialize FastAPI with detailed metadata for the Swagger UI documentation
app = FastAPI(
    title="E-Library Management System API",
    description="A backend API for managing books, users, borrowing records, and AI-generated summaries.",
    version="1.0.0",
    lifespan=lifespan
)

# Register the routing module for books and users
app.include_router(books.router)

@app.get("/", tags=["System"], summary="System Health Check")
async def health_check():
    """
    Root endpoint used by load balancers and deployment platforms 
    to verify that the API is running and accessible.
    """
    return {
        "status": "System online",
        "message": "Welcome to the E-Library API"
    }