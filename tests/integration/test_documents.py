import pytest

from async_search_client.errors import MeiliSearchApiError, MeiliSearchError


@pytest.mark.asyncio
async def test_get_documents_default(empty_index):
    index = await empty_index()
    response = await index.get_documents()
    assert response is None


@pytest.mark.asyncio
async def test_add_documents(empty_index, small_movies):
    index = await empty_index()
    response = await index.add_documents(small_movies)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == "id"
    assert update.status == "processed"


@pytest.mark.asyncio
async def test_add_documents_with_primary_key(test_client, small_movies):
    primary_key = "release_date"
    index = test_client.index("movies")
    response = await index.add_documents(small_movies, primary_key=primary_key)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == primary_key
    assert update.status == "processed"


@pytest.mark.asyncio
async def test_add_documents_from_file(test_client, small_movies_path):
    index = test_client.index("movies")
    response = await index.add_documents_from_file(small_movies_path)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == "id"
    assert update.status == "processed"


@pytest.mark.asyncio
async def test_add_documents_from_file_string_path(test_client, small_movies_path):
    string_path = str(small_movies_path)
    index = test_client.index("movies")
    response = await index.add_documents_from_file(string_path)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == "id"
    assert update.status == "processed"


@pytest.mark.asyncio
async def test_add_documents_from_file_with_primary_key(test_client, small_movies_path):
    primary_key = "release_date"
    index = test_client.index("movies")
    response = await index.add_documents_from_file(small_movies_path, primary_key=primary_key)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == primary_key
    assert update.status == "processed"


@pytest.mark.asyncio
async def test_add_documents_from_file_invalid_extension(test_client):
    index = test_client.index("movies")

    with pytest.raises(MeiliSearchError):
        await index.add_documents_from_file("test.csv")


@pytest.mark.asyncio
async def test_get_document(index_with_documents):
    index = await index_with_documents()
    response = await index.get_document("500682")
    assert response["title"] == "The Highwaymen"


@pytest.mark.asyncio
async def test_get_document_inexistent(empty_index):
    with pytest.raises(MeiliSearchApiError):
        index = await empty_index()
        await index.get_document("123")


@pytest.mark.asyncio
async def test_get_documents_populated(index_with_documents):
    index = await index_with_documents()
    response = await index.get_documents()
    assert len(response) == 20


@pytest.mark.asyncio
async def test_get_documents_offset_optional_params(index_with_documents):
    index = await index_with_documents()
    response = await index.get_documents()
    assert len(response) == 20
    response_offset_limit = await index.get_documents(
        limit=3, offset=1, attributes_to_retrieve="title"
    )
    assert len(response_offset_limit) == 3
    assert response_offset_limit[0]["title"] == response[1]["title"]


@pytest.mark.asyncio
async def test_update_documents(index_with_documents, small_movies):
    index = await index_with_documents()
    response = await index.get_documents()
    response[0]["title"] = "Some title"
    update = await index.update_documents([response[0]])
    await index.wait_for_pending_update(update.update_id)
    response = await index.get_documents()
    assert response[0]["title"] == "Some title"
    update = await index.update_documents(small_movies)
    await index.wait_for_pending_update(update.update_id)
    response = await index.get_documents()
    assert response[0]["title"] != "Some title"


@pytest.mark.asyncio
async def test_update_documents_with_primary_key(test_client, small_movies):
    primary_key = "release_date"
    index = test_client.index("movies")
    update = await index.update_documents(small_movies, primary_key=primary_key)
    await index.wait_for_pending_update(update.update_id)
    assert await index.get_primary_key() == primary_key


@pytest.mark.asyncio
async def test_update_documents_from_file(test_client, small_movies, small_movies_path):
    small_movies[0]["title"] = "Some title"
    index = test_client.index("movies")
    response = await index.add_documents(small_movies)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == "id"
    response = await index.get_documents()
    assert response[0]["title"] == "Some title"
    update = await index.update_documents_from_file(small_movies_path)
    update = await index.wait_for_pending_update(update.update_id)
    assert update.status == "processed"
    response = await index.get_documents()
    assert response[0]["title"] != "Some title"


@pytest.mark.asyncio
async def test_update_documents_from_file_string_path(test_client, small_movies, small_movies_path):
    string_path = str(small_movies_path)
    small_movies[0]["title"] = "Some title"
    index = test_client.index("movies")
    response = await index.add_documents(small_movies)
    update = await index.wait_for_pending_update(response.update_id)
    assert await index.get_primary_key() == "id"
    response = await index.get_documents()
    assert response[0]["title"] == "Some title"
    update = await index.update_documents_from_file(string_path)
    update = await index.wait_for_pending_update(update.update_id)
    assert update.status == "processed"
    response = await index.get_documents()
    assert response[0]["title"] != "Some title"


@pytest.mark.asyncio
async def test_update_documents_from_file_with_primary_key(
    test_client, small_movies, small_movies_path
):
    primary_key = "release_date"
    index = test_client.index("movies")
    update = await index.update_documents_from_file(small_movies_path, primary_key=primary_key)
    await index.wait_for_pending_update(update.update_id)
    assert await index.get_primary_key() == primary_key


@pytest.mark.asyncio
async def test_update_documents_from_file_invalid_extension(test_client):
    index = test_client.index("movies")

    with pytest.raises(MeiliSearchError):
        await index.update_documents_from_file("test.csv")


@pytest.mark.asyncio
async def test_delete_document(index_with_documents):
    index = await index_with_documents()
    response = await index.delete_document("500682")
    await index.wait_for_pending_update(response.update_id)
    with pytest.raises(MeiliSearchApiError):
        await index.get_document("500682")


@pytest.mark.asyncio
async def test_delete_documents(index_with_documents):
    to_delete = ["522681", "450465", "329996"]
    index = await index_with_documents()
    response = await index.delete_documents(to_delete)
    await index.wait_for_pending_update(response.update_id)
    documents = await index.get_documents()
    ids = [x["id"] for x in documents]
    assert to_delete not in ids


@pytest.mark.asyncio
async def test_delete_all_documents(index_with_documents):
    index = await index_with_documents()
    response = await index.delete_all_documents()
    await index.wait_for_pending_update(response.update_id)
    response = await index.get_documents()
    assert response is None
