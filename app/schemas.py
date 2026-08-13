from pydantic import BaseModel, ConfigDict, Field

class BookBase(BaseModel):
    """Base schema containing common attributes for a Book."""
    title: str = Field(..., description="The title of the book", examples=["The Pragmatic Programmer"])
    author: str = Field(..., description="The primary author of the book", examples=["Andrew Hunt"])
    isbn: str = Field(..., description="Unique International Standard Book Number", examples=["978-0135957059"])
    published_year: int = Field(..., description="The year the book was published", examples=[1999])
    total_copies: int = Field(..., description="Total physical or digital copies owned by the library", examples=[5])

class BookCreate(BookBase):
    """Schema for creating a new book. Inherits all fields from BookBase."""
    pass

class BookResponse(BookBase):
    """Schema for returning book data, including dynamically tracked inventory."""
    id: int = Field(..., description="The internal database ID of the book")
    available_copies: int = Field(..., description="Current number of copies available for checkout")
    
    # Required in Pydantic V2 to automatically convert SQLAlchemy ORM objects into JSON dictionaries
    model_config = ConfigDict(from_attributes=True)

class BookSummaryResponse(BaseModel):
    """Schema for returning the AI-generated book summary."""
    book_id: int = Field(..., description="The internal database ID of the summarized book")
    summary_text: str = Field(..., description="The AI-generated text or the cached summary")

class UserCreate(BaseModel):
    """Schema for registering a new library member."""
    name: str = Field(..., description="Full name of the user", examples=["Alice"])
    email: str = Field(..., description="Unique email address for the user", examples=["alice@example.com"])

class UserResponse(UserCreate):
    """Schema for returning registered user data."""
    id: int = Field(..., description="The internal database ID of the user")
    
    model_config = ConfigDict(from_attributes=True)

class BorrowRequest(BaseModel):
    """Schema for a user requesting to borrow or return a book."""
    user_id: int = Field(..., description="The internal database ID of the user performing the action", examples=[1])

class BorrowResponse(BaseModel):
    """Schema for the response payload after a successful borrow or return transaction."""
    message: str = Field(..., description="Status message confirming the action")
    book_title: str = Field(..., description="Title of the affected book for UI confirmation")
    available_copies_left: int = Field(..., description="The updated available inventory count after the transaction")