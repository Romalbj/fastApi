from fastapi import APIRouter, HTTPException, Path, Query, Request, Response
from sqlalchemy import select

from src.dependences import SessionDep
from src.models.models import BookModel
from src.schemas.books import NewBookChema


router = APIRouter(
    prefix='/books/api',
    tags=['API_Books 📚']
)


@router.get('/all', summary='Получить список книг')
async def get_all_books_json(session: SessionDep, response: Response, request: Request):
    query = await session.execute(select(BookModel))
    result = query.scalars().all()

    # просто отправляю кастомный заголовок
    response.headers['custom_header'] = 'header'

    # установим куки
    response.set_cookie(key='my-cookie', value='love cookies')
    response.set_cookie(key='my-cookie', value='love cookies')
    
    return result


# Возвращаем книги по запрошенному автору с помощью строки запроса
@router.get('/books_by_author', summary='Получить список книг по автору')
async def get_books_by_athor(
    session: SessionDep, 
    author_list: list[str] = Query(default=None, alias="author", max_length=100),
    ):
    query = select(BookModel)

    if author_list:
        query = query.where(BookModel.author.in_(author_list))

    result = await session.execute(query)
    books = result.scalars().all()
    return books

# Возвращаем книгу по запрошенному id
@router.get('/get/{id}', summary='Получить книгу по id')
async def get_book_by_id(session: SessionDep, id: int = Path(gt=0)):
    query = select(BookModel).where(BookModel.id == id)
    result = await session.execute(query)
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail='Книга не найдена')

    return book


@router.get('/books', summary='Получить список книг')
async def get_all_books_page(session: SessionDep, response: Response, request: Request):
    query = await session.execute(select(BookModel))
    result = query.scalars().all()

    # просто отправляю кастомный заголовок
    response.headers['custom_header'] = 'header'

    # установим куки
    response.set_cookie(key='my-cookie', value='love cookies')
    response.set_cookie(key='my-cookie', value='love cookies')
    
    # return templates.TemplateResponse(request, 'all_books.html', {'books': result})
    return result


# Добавить одну книгу
@router.post('/add', summary='Добавить одну книгу')
async def add_book(newBook: NewBookChema, session: SessionDep):
    new_book = BookModel(
        title = newBook.title,
        author = newBook.author            
    )
    session.add(new_book)
    await session.commit()
    return {'status': 'success', 'book': new_book}


# Добавить несколько книг
@router.post('/books_multiple', summary='Добавить несколько книг')
async def add_books(new_books: list[NewBookChema], session: SessionDep):
    for book in new_books:
        session.add(BookModel(
            title = book.title,
            author = book.author   
        ))

    await session.commit()
    return {'new_books': new_books}


@router.put('/book/edit/{id}', summary='Редактировать информацию о книге')
async def edit_book_info(session: SessionDep, id: int, new_data: NewBookChema):
    query = await session.execute(select(BookModel).where(BookModel.id == id))
    book = query.scalars().first()

    if not book:
        raise HTTPException(status_code=404, detail={'message:': 'Книга с таким id не найдена'})


    book.title = new_data.title 
    book.author = new_data.author 

    await session.commit()
    await session.refresh(book)

    return book


@router.delete('/book/delete/{id}', summary='Удалить книгу')
async def delete_book(session: SessionDep, id: int):
    query = await session.execute(select(BookModel).where(BookModel.id == id))
    book = query.scalar_one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail={'message:': 'Книга с таким id не найдена'})

    await session.delete(book)
    await session.commit()

    return {'status_code':200, 'detail': {'message': 'Книга удалена', 'book': book}}