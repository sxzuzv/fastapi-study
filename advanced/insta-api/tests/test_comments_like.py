import pytest
from fastapi.testclient import TestClient

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
def bob_headers():
    return login('bob', 'pw1234')


@pytest.fixture
def post_id(alice_headers):
    """alice가 글을 하나 만들어 주고, 테스트가 끝나면 글을 삭제한다.
    글을 지우면 그 글의 댓글·하트도 같이 지워진다(cascade).
    """
    res = client.post('/api/posts', json={'content': 'comment/like test'}, headers=alice_headers)
    assert res.status_code == 201
    pid = res.json()['id']

    yield pid

    client.delete(f'/api/posts/{pid}', headers=alice_headers)


def create_comment(post_id, headers, content='첫 댓글'):
    res = client.post(f'/api/posts/{post_id}/comments', json={'content': content}, headers=headers)
    assert res.status_code == 201
    return res.json()['id']


def comment_ids(post_id):
    res = client.get(f'/api/posts/{post_id}/comments')
    assert res.status_code == 200
    return [c['id'] for c in res.json()]


def like_user_ids(post_id):
    res = client.get(f'/api/posts/{post_id}')
    assert res.status_code == 200
    return [like['user_id'] for like in res.json()['likes']]


def my_id(headers):
    return client.get('/api/auth/me', headers=headers).json()['id']


# 1. 댓글을 쓰면 201이고, 그 글의 댓글 목록에 보인다
def test_comment_create(post_id, bob_headers):
    res = client.post(
        f'/api/posts/{post_id}/comments',
        json={'content': '좋은 글이네요'},
        headers=bob_headers,
    )
    assert res.status_code == 201
    comment_id = res.json()['id']

    assert comment_id in comment_ids(post_id)


# 2. 내 댓글을 고치면 200이고, 내용이 바뀐다
def test_comment_update_mine(post_id, bob_headers):
    comment_id = create_comment(post_id, bob_headers, '수정 전')

    res = client.patch(
        f'/api/posts/comments/{comment_id}',
        json={'content': '수정 후'},
        headers=bob_headers,
    )
    assert res.status_code == 200
    assert res.json()['content'] == '수정 후'

    # 목록에서도 바뀐 내용이 보인다
    comments = client.get(f'/api/posts/{post_id}/comments').json()
    assert [c['content'] for c in comments if c['id'] == comment_id] == ['수정 후']


# 3. 남의 댓글을 고치거나(PATCH) 지우면(DELETE) 403
def test_comment_update_other_403(post_id, alice_headers, bob_headers):
    comment_id = create_comment(post_id, bob_headers)

    res = client.patch(
        f'/api/posts/comments/{comment_id}',
        json={'content': 'alice가 몰래 수정'},
        headers=alice_headers,
    )
    assert res.status_code == 403


def test_comment_delete_other_403(post_id, alice_headers, bob_headers):
    comment_id = create_comment(post_id, bob_headers)

    res = client.delete(f'/api/posts/comments/{comment_id}', headers=alice_headers)
    assert res.status_code == 403

    # 지워지지 않고 그대로 남아 있어야 한다
    assert comment_id in comment_ids(post_id)


# 4. 없는 댓글을 고치면 404
def test_comment_update_404(bob_headers):
    res = client.patch(
        '/api/posts/comments/99999999',
        json={'content': '없는 댓글'},
        headers=bob_headers,
    )
    assert res.status_code == 404


# 5. 내 댓글을 지우면 204이고, 목록에서 사라진다
def test_comment_delete_mine(post_id, bob_headers):
    comment_id = create_comment(post_id, bob_headers)

    res = client.delete(f'/api/posts/comments/{comment_id}', headers=bob_headers)
    assert res.status_code == 204

    assert comment_id not in comment_ids(post_id)


# 6. 하트를 누르면 201이고, 글의 likes에 내가 있다
def test_like_create(post_id, bob_headers):
    res = client.post(f'/api/posts/{post_id}/likes', headers=bob_headers)
    assert res.status_code == 201

    assert my_id(bob_headers) in like_user_ids(post_id)


# 7. 이미 누른 하트를 또 누르면 409
def test_like_twice_409(post_id, bob_headers):
    assert client.post(f'/api/posts/{post_id}/likes', headers=bob_headers).status_code == 201

    res = client.post(f'/api/posts/{post_id}/likes', headers=bob_headers)
    assert res.status_code == 409


# 8. 하트를 취소하면 200이고, likes에서 내가 빠진다
def test_like_cancel(post_id, bob_headers):
    assert client.post(f'/api/posts/{post_id}/likes', headers=bob_headers).status_code == 201

    res = client.delete(f'/api/posts/{post_id}/likes', headers=bob_headers)
    assert res.status_code == 200

    assert my_id(bob_headers) not in like_user_ids(post_id)
