import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app

client = TestClient(app)


def login(username, password):
    res = client.post('/api/auth/login', data={'username': username, 'password': password})
    token = res.json()['access_token']

    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def alice_headers():
    return login('alice', 'pw1234')


@pytest.fixture
def cleanup(alice_headers):
    """테스트가 만든 글과 업로드 파일을 모아 두었다가, 테스트가 끝나면 지운다."""
    post_ids = []
    image_urls = []

    yield post_ids, image_urls

    for pid in post_ids:
        client.delete(f'/api/posts/{pid}', headers=alice_headers)

    for url in image_urls:
        # '/media/abc.jpg' → 서버가 저장한 'media/abc.jpg' 파일
        Path(url.lstrip('/')).unlink(missing_ok=True)


def make_png_bytes():
    """테스트용 가짜 사진(빨간 100x100 PNG)을 메모리에서 만든다."""
    buf = io.BytesIO()
    Image.new('RGB', (100, 100), 'red').save(buf, format='PNG')
    buf.seek(0)

    return buf


def upload_photo(headers=None):
    return client.post(
        '/api/uploads',
        files={'photo': ('test.png', make_png_bytes(), 'image/png')},
        headers=headers,
    )


# 1. 사진을 올리면(POST /api/uploads) 201이고, image_url이 /media/로 시작한다
def test_upload_photo(alice_headers, cleanup):
    _, image_urls = cleanup

    res = upload_photo(alice_headers)
    assert res.status_code == 201

    image_url = res.json()['image_url']
    image_urls.append(image_url)
    assert image_url.startswith('/media/')

    # 올린 사진이 실제로 /media 로 내려받아진다
    assert client.get(image_url).status_code == 200


# 2. 사진이 아닌 파일을 올리면 400
def test_upload_not_photo_400(alice_headers):
    res = client.post(
        '/api/uploads',
        files={'photo': ('memo.txt', io.BytesIO(b'this is not an image'), 'text/plain')},
        headers=alice_headers,
    )
    assert res.status_code == 400


# 3. 토큰 없이 올리면 401
def test_upload_without_token_401():
    res = upload_photo()
    assert res.status_code == 401


# 4. 올려서 받은 image_url로 글을 쓰면 201이고, 그 글의 image_url이 같은 주소다
def test_post_with_image_url(alice_headers, cleanup):
    post_ids, image_urls = cleanup

    res = upload_photo(alice_headers)
    assert res.status_code == 201
    image_url = res.json()['image_url']
    image_urls.append(image_url)

    res = client.post(
        '/api/posts',
        json={'content': 'photo post test', 'image_url': image_url},
        headers=alice_headers,
    )
    assert res.status_code == 201
    post_id = res.json()['id']
    post_ids.append(post_id)

    res = client.get(f'/api/posts/{post_id}')
    assert res.status_code == 200
    assert res.json()['image_url'] == image_url
