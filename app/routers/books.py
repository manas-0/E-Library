from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.database import get_db
from app.models import Book, BookSummary, User, BorrowRecord
from app.schemas import (
    BookCreate, BookResponse, BookSummaryResponse, 
    BorrowRequest, BorrowResponse, UserCreate, UserResponse 
)
from app.services.ai_service import generate_book_summary

router = APIRouter(prefix="/api/books", tags=["Books"])

# Modern Dependency Injection: Define once, use everywhere
DbSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, summary="Add a new book")
async def create_book(book: BookCreate, db: DbSession):
    """
    Creates a new book entry in the catalog. 
    Initializes available copies to match the total copies provided.
    """
    db_book = Book(**book.model_dump(), available_copies=book.total_copies)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookResponse], summary="Search and list books")
async def get_books(db: DbSession, title: Optional[str] = None, author: Optional[str] = None):
    """
    Fetch all books. Optionally filter by title or author using case-insensitive partial matching.
    """
    query = select(Book)
    
    # ilike provides case-insensitive partial matching for robust search functionality
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"], summary="Register a new user")
async def create_user(user: UserCreate, db: DbSession):
    """
    Registers a user so they can borrow books. Enforces unique email addresses.
    """
    db_user = User(**user.model_dump())
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception:
        # Rollback the transaction if the email already exists to prevent a database crash
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

@router.get("/{book_id}/summary", response_model=BookSummaryResponse, summary="Get AI-generated book summary")
async def get_book_summary(book_id: int, db: DbSession):
    """
    Retrieves a book summary. Utilizes a database caching layer to minimize external LLM API calls and reduce latency.
    """
    # 1. Verify the book exists in the catalog
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    # 2. Check Database Cache to avoid redundant LLM requests
    cache_result = await db.execute(select(BookSummary).where(BookSummary.book_id == book_id))
    cached_summary = cache_result.scalars().first()
    
    if cached_summary:
        return {"book_id": book.id, "summary_text": cached_summary.summary_text}
        
    # 3. Cache Miss: Request new summary from the external AI Service
    summary_text = await generate_book_summary(book.title, book.author)
    
    # 4. Save the generated summary to the cache for future requests
    new_summary = BookSummary(book_id=book.id, summary_text=summary_text)
    db.add(new_summary)
    await db.commit()
    
    return {"book_id": book.id, "summary_text": summary_text}

@router.post("/{book_id}/borrow", response_model=BorrowResponse, summary="Borrow a book")
async def borrow_book(book_id: int, request: BorrowRequest, db: DbSession):
    """
    Checks out a book for a user. Validates that the book has available inventory before proceeding.
    """
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    # Prevent checkout if the book is currently out of stock
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies currently available")

    # Log the checkout transaction
    borrow_record = BorrowRecord(user_id=request.user_id, book_id=book.id)
    db.add(borrow_record)
    
    # Dynamically decrement the available inventory
    book.available_copies -= 1
    
    await db.commit()
    await db.refresh(book)
    
    return {
        "message": "Book successfully borrowed",
        "book_title": book.title,
        "available_copies_left": book.available_copies
    }

@router.post("/{book_id}/return", response_model=BorrowResponse, summary="Return a borrowed book")
async def return_book(book_id: int, request: BorrowRequest, db: DbSession):
    """
    Returns a checked-out book. Validates that the user actually has an active, unreturned record for this book.
    """
    # Search for an active borrow record (where return_date is explicitly null)
    result = await db.execute(
        select(BorrowRecord)
        .where(BorrowRecord.book_id == book_id)
        .where(BorrowRecord.user_id == request.user_id)
        .where(BorrowRecord.return_date == None)
    )
    record = result.scalars().first()
    
    if not record:
        raise HTTPException(status_code=404, detail="No active borrow record found for this user and book")
        
    # Close the borrow record by stamping the current timestamp
    record.return_date = func.now()
    
    # Restore the inventory count
    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalars().first()
    book.available_copies += 1
    
    await db.commit()
    await db.refresh(book)
    
    return {
        "message": "Book successfully returned",
        "book_title": book.title,
        "available_copies_left": book.available_copies
    }