from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

app = FastAPI()


class BookRequest(BaseModel):
    id: Optional[int] = Field(title="id is not needed", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    # setting an example for openapi docs
    # https://fastapi.tiangolo.com/tutorial/schema-extra-example/?h=pydantic#extra-json-schema-data-in-pydantic-models
    model_config = {
        'json_schema_extra': {
            'example': {
                'title': 'Harry Porter',
                'author': 'JK Rowling',
                'description': 'Magical world',
                'rating': 5,
                'published_date': 2029
            }
        }
    }


@dataclass
class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int


BOOKS: list[Book] = [
    Book(1, "Book 1", "Author 1", "Description 1", 1, 2030),
    Book(2, "Book 2", "Author 2", "Description 2", 2, 2030),
    Book(3, "Book 3", "Author 3", "Description 3", 3, 2032),
    Book(4, "Book 4", "Author 4", "Description 4", 4, 2032),
    Book(5, "Book 5", "Author 5", "Description 5", 5, 2034)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    new_book.id = get_new_book_id()
    BOOKS.append(new_book)


@app.get("/books/by-book-id/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Book by id {book_id} not found")


@app.get("/books/by-rating/{rating}", status_code=status.HTTP_200_OK)
async def read_books_by_rating(rating: int = Path(gt=0, lt=6)):
    books_to_return: list[Book] = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)

    if len(books_to_return) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book by rating {rating} not found")

    return books_to_return


@app.get("/books/by-published-date/{published_date}", status_code=status.HTTP_200_OK)
async def read_books_by_published_date(published_date: int = Path(gt=1999, lt=2031)):
    books_to_return: list[Book] = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    if len(books_to_return) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book by published date {published_date} not found")

    return books_to_return


@app.get("/books/by-author", status_code=status.HTTP_200_OK)
async def read_books_by_author(author: str = Query(min_length=1)):
    books_to_return: list[Book] = []
    for book in BOOKS:
        if author.casefold() in book.author.casefold():
            books_to_return.append(book)

    if len(books_to_return) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book by author date {author} not found")

    return books_to_return


@app.put("/books", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(updated_book: BookRequest):
    book_changed = False

    if updated_book.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="id is required")

    for i, book in enumerate(BOOKS):
        if book.id == updated_book.id:
            BOOKS[i] = book
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"book with id {updated_book.id} not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False

    for i, book in enumerate(BOOKS):
        if book.id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"book with id {book_id} not found")


def get_new_book_id():
    if len(BOOKS) > 0:
        # take last book id and increment by 1
        new_id = BOOKS[-1].id + 1
        return new_id
    # no books so return 1 as id
    return 1
