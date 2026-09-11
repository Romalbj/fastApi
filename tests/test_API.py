import pytest

# библиотека для того, чтобы тестировать FastApi н запуская сервер uvicorn
from httpx import AsyncClient, ASGITransport

from main import app

@pytest.mark.asyncio
async def test_get_all_books(app_with_test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_test_db),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/books/api/all")
        data = response.json()

        print(response.status_code, data)

        assert response.status_code == 200
        assert isinstance(data, list)
        
        if data:
            assert "id" in data[0]
            assert "title" in data[0]
            assert "author" in data[0]


@pytest.mark.asyncio
async def test_get_book_by_id(app_with_test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_test_db),
        base_url="http://test"
    ) as ac:

        test_book = {
            "title": "test_book",
            "author": "test_author"
        }

        resp_create = await ac.post("/books/api/add", json=test_book)
        assert resp_create.status_code == 200
        data_create = resp_create.json()
        test_book_id = data_create['book']['id']
        print('-----------------------------------------', data_create)


        resp_get_by_id = await ac.get(f"/books/api/get/{test_book_id}")
        assert resp_get_by_id.status_code == 200

        data_get = resp_get_by_id.json()
        assert data_get['id'] == test_book_id
        assert data_get["title"] == test_book["title"]
        assert data_get["author"] == test_book["author"]

@pytest.mark.asyncio
async def test_add_book(app_with_test_db):
    async with AsyncClient(
        transport=ASGITransport(app_with_test_db),
        base_url="http://test"
    ) as ac:
        new_book = {
            "title": "test_book",
            "author": "me"
        }

        response = await ac.post("/books/api/add", json=new_book)
        data = response.json()

        print(response.status_code, data)

        assert response.status_code == 200
        assert data["status"] == "success"
        assert "book" in data
        assert data["book"]["title"] == "test_book"
        assert data["book"]["author"] == "me"
        assert "id" in data["book"]



@pytest.mark.asyncio
async def test_show_all_posts(app_with_test_db):
    async with AsyncClient(
        transport=ASGITransport(app_with_test_db),
        base_url='http://test'
    ) as ac:
        query = await ac.get('/post/api/show_posts')
        result = query.json()

        assert 'posts' in result
        assert len(result['posts']) > 0
        assert result['posts'] is not None

def some_func(num):
    return 1 / num

def test_some_func():
    assert some_func(1) == 1
    # assert some_func(0) == 0.5


 