from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class User(Base):
    """Represents a library member who can borrow books."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)

class Book(Base):
    """Represents a physical or digital book in the library catalog."""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True)
    published_year = Column(Integer)
    
    # Inventory tracking parameters
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)

class BorrowRecord(Base):
    """Tracks the borrowing lifecycle (checkout and return) of a book by a user."""
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    
    # Automatically stamps the exact time the database row is created
    borrow_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # A Null return_date indicates the book is currently checked out
    return_date = Column(DateTime(timezone=True), nullable=True) 

class BookSummary(Base):
    """Caching layer for AI-generated book summaries to minimize API costs/latency."""
    __tablename__ = "book_summaries"

    id = Column(Integer, primary_key=True, index=True)
    
    # unique=True ensures we only ever cache one summary per book
    book_id = Column(Integer, ForeignKey("books.id"), unique=True)
    summary_text = Column(String, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Establishes an ORM relationship back to the Book table
    book = relationship("Book")