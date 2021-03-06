import asyncio
import json
from pathlib import Path

import pytest

from async_search_client.client import Client

MASTER_KEY = "masterKey"
BASE_URL = "http://127.0.0.1:7700"
INDEX_UID = "indexUID"
INDEX_UID2 = "indexUID2"
INDEX_UID3 = "indexUID3"
INDEX_UID4 = "indexUID4"

INDEX_FIXTURE = [
    {"uid": INDEX_UID},
    {"uid": INDEX_UID2, "primary_key": "book_id"},
]

ROOT_PATH = Path().absolute()
SMALL_MOVIES_PATH = ROOT_PATH / "datasets" / "small_movies.json"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def test_client():
    async with Client(BASE_URL, MASTER_KEY) as client:
        yield client


@pytest.mark.asyncio
@pytest.fixture(autouse=True)
async def clear_indexes(test_client):
    """
    Auto-clears the indexes after each test function run.
    Makes all the test functions independent.
    """
    yield
    indexes = await test_client.get_indexes()
    if indexes:
        for index in indexes:
            await test_client.index(index.uid).delete()


@pytest.fixture(scope="session")
def master_key():
    return MASTER_KEY


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def index_uid():
    return INDEX_UID


@pytest.fixture
def index_uid2():
    return INDEX_UID2


@pytest.fixture
def index_uid3():
    return INDEX_UID3


@pytest.fixture
def index_uid4():
    return INDEX_UID4


@pytest.mark.asyncio
@pytest.fixture
async def indexes_sample(test_client):
    indexes = []
    for index_args in INDEX_FIXTURE:
        index = await test_client.create_index(**index_args)
        indexes.append(index)
    yield indexes


@pytest.fixture(scope="session")
def small_movies():
    """
    Runs once per session. Provides the content of small_movies.json.
    """

    with open(SMALL_MOVIES_PATH, "r") as movie_file:
        yield json.loads(movie_file.read())


@pytest.fixture(scope="session")
def small_movies_path():
    return SMALL_MOVIES_PATH


@pytest.mark.asyncio
@pytest.fixture
async def empty_index(test_client):
    async def index_maker(index_name=INDEX_UID):
        return await test_client.create_index(uid=index_name)

    return index_maker


@pytest.mark.asyncio
@pytest.fixture
async def index_with_documents(empty_index, small_movies, index_uid):
    async def index_maker(index_name=index_uid, documents=small_movies):
        index = await empty_index(index_name)
        response = await index.add_documents(documents)
        await index.wait_for_pending_update(response.update_id)
        return index

    return index_maker
