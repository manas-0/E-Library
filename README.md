# E-Library Management System API

>  Live API Documentation:** [Access Swagger UI](https://e-library-kt57.onrender.com/docs)

A production-ready, asynchronous FastAPI backend for managing library books, user accounts, borrowing lifecycles, and automated AI-generated book summaries.
## Features
- **Modern FastAPI & Pydantic V2:** Built using type-safe validation, FastAPI `Annotated` dependency injection, and automatic Swagger UI documentation with pre-filled examples.
- **Asynchronous PostgreSQL:** Uses SQLAlchemy (AsyncIO) and `asyncpg` for high-performance, non-blocking database operations.
- **AI Integration:** Automatically caches LLM-generated book summaries to minimize external API costs and latency.
- **Robust Error Handling & Inventory Control:** Enforces strict checkout rules, unique constraints, and case-insensitive search functionality.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy (AsyncIO)
- **Validation:** Pydantic V2
- **Network/AI:** HTTPX & Userfacet LLM API (`gpt-4o-mini`)

## Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manas-0/E-Library.git
   cd E_library

Create and activate a virtual environment:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt

## Configure Environment Variables:
Create a .env file in the root directory based on .env.example:

Code snippet
AI_API_TOKEN=your_token_here
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/elibrary
Run the application:

Bash
uvicorn app.main:app --reload
Access the interactive documentation at http://127.0.0.1:8000/docs.
   
