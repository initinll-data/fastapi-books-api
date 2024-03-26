from typing import Any

from fastapi import Body, FastAPI, HTTPException

app = FastAPI()

BOOKS = [
    {'title': 'Title 1', 'author': 'Author 1', 'category': 'category 1'},
    {'title': 'Title 2', 'author': 'Author 2', 'category': 'category 2'},
    {'title': 'Title 3', 'author': 'Author 3', 'category': 'category 3'},
    {'title': 'Title 4', 'author': 'Author 4', 'category': 'category 4'}
]


@app.get("/books/list")
async def get_books() -> list[dict]:
    return BOOKS


@app.get("/books/search")
async def search_books(title: str | None = None, author: str | None = None) -> list[dict]:
    books = []
    try:
        if title is None and author is None:
            return BOOKS

        for book in BOOKS:
            if title and author:
                if title.casefold() in book['title'].casefold() and author.casefold() in book['author'].casefold():
                    books.append(book)
            elif title:
                if title.casefold() in book['title'].casefold():
                    books.append(book)
            elif author:
                if author.casefold() in book['author'].casefold():
                    books.append(book)

        if len(books) > 0:
            return books

        if title and author:
            raise HTTPException(
                status_code=404, detail=f"Book with title {title} and author {author} not found")
        elif title:
            raise HTTPException(
                status_code=404, detail=f"Book with title {title} not found")
        elif author:
            raise HTTPException(
                status_code=404, detail=f"Book with author {author} not found")
    except:
        raise


@app.post("/books/create")
async def create_book(created_book: dict = Body()):
    BOOKS.append(created_book)


@app.put("/books/update")
async def update_book(updated_book: dict = Body()):
    for i, book in enumerate(BOOKS):
        if book.get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
            break


@app.delete("/books/delete/{title}")
async def delete_book(title: str):
    for i, book in enumerate(BOOKS):
        if book.get('title').casefold() == title.casefold():
            BOOKS.pop(i)
            break
