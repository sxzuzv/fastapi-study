import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from deps import SECRET_KEY, ALGORITHM
from main import app

client = TestClient(app)


def login(username, password):
    res = client.post('/api/auth/login', data={'username': username, 'password': password})
    token = res.json()['access_token']

    return {'Authorization': f'Bearer {token}'}


def unique_username():
    # username은 3~20자 제한 → 'u_' + 12자리 = 14자
    return f'u_{uuid.uuid4().hex[:12]}'


def make_token(sub, key=SECRET_KEY, expires_in=timedelta(minutes=30)):
    exp = datetime.now(timezone.utc) + expires_in
    return jwt.encode({'sub': str(sub), 'exp': exp}, key, algorithm=ALGORITHM)


@pytest.fixture
def alice_post():
    """alice가 쓴 게시글을 만들어 주고, 테스트가 끝나면 삭제한다."""
    headers = login('alice', 'pw1234')
    # 참고: 현재 PostCreate 스키마가 user_id를 필수로 요구해서 같이 보낸다 (alice = 1번)
    me = client.get('/api/auth/me', headers=headers).json()
    res = client.post(
        '/api/posts',
        json={'content': 'rules test post', 'user_id': me['id']},
        headers=headers,
    )
    assert res.status_code == 201
    post_id = res.json()['id']

    yield post_id

    # 이미 지워졌어도(404) 에러 없이 넘어간다
    client.delete(f'/api/posts/{post_id}', headers=headers)


# 1. 가입 → 로그인 → /api/auth/me 가 가입한 나를 돌려준다
def test_signup_login_me():
    username = unique_username()

    res = client.post('/api/auth/signup', json={'username': username, 'password': 'pw1234'})
    assert res.status_code == 200
    user_id = res.json()['id']

    res = client.get('/api/auth/me', headers=login(username, 'pw1234'))
    assert res.status_code == 200
    assert res.json()['id'] == user_id
    assert res.json()['username'] == username


# 2. 같은 아이디로 두 번 가입하면 409
def test_signup_duplicate_409():
    username = unique_username()
    body = {'username': username, 'password': 'pw1234'}

    assert client.post('/api/auth/signup', json=body).status_code == 200
    assert client.post('/api/auth/signup', json=body).status_code == 409


# 3. 아이디가 3글자보다 짧으면 422
def test_signup_short_username_422():
    res = client.post('/api/auth/signup', json={'username': 'ab', 'password': 'pw1234'})
    assert res.status_code == 422


# 4. 틀린 비밀번호로 로그인하면 401
def test_login_wrong_password_401():
    res = client.post('/api/auth/login', data={'username': 'alice', 'password': 'wrong-pw'})
    assert res.status_code == 401


# 5. 토큰 없이 글을 쓰면 401
def test_post_create_without_token_401():
    res = client.post('/api/posts', json={'content': 'no token'})
    assert res.status_code == 401


# 6. 남의 글을 고치거나(PATCH) 지우면(DELETE) 403
def test_other_user_patch_403(alice_post):
    res = client.patch(
        f'/api/posts/{alice_post}',
        json={'content': 'hacked by bob'},
        headers=login('bob', 'pw1234'),
    )
    assert res.status_code == 403


def test_other_user_delete_403(alice_post):
    res = client.delete(f'/api/posts/{alice_post}', headers=login('bob', 'pw1234'))
    assert res.status_code == 403

    # 지워지지 않고 그대로 남아 있어야 한다
    assert client.get(f'/api/posts/{alice_post}').status_code == 200


# 7. 서명이 틀린 토큰으로 /api/auth/me 를 부르면 401
def test_me_with_bad_signature_401():
    token = make_token(sub=1, key='wrong-secret-key')
    res = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 401


# 8. 만료된 토큰으로 /api/auth/me 를 부르면 401
def test_me_with_expired_token_401():
    token = make_token(sub=1, expires_in=timedelta(minutes=-1))
    res = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 401
