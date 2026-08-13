import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Load environment variables from the .env file if it exists (for local development)
load_dotenv()

# This is the crucial change for deployment: 
# It looks for a "DATABASE_URL" in the cloud server's environment variables first.
# If it doesn't find one (like when you run it locally), it defaults to your Docker database.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/elibrary")

# The engine manages the connection pool to the database.
# Note: echo=True prints all SQL statements to the terminal (great for debugging, disable in prod)
engine = create_async_engine(DATABASE_URL, echo=True)

# async_sessionmaker generates a new, isolated AsyncSession object for each request.
# expire_on_commit=False prevents SQLAlchemy from prematurely clearing object attributes after a commit.
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# The declarative base class that all our ORM models (Book, User, etc.) will inherit from
Base = declarative_base()

async def get_db():
    """
    FastAPI Dependency Injection for the database.
    Yields a dedicated database session per HTTP request and guarantees 
    the session is safely closed when the request completes, preventing connection leaks.
    """
    async with async_session() as session:
        yield session