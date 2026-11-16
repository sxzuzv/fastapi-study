from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_list():
    res = client.get('/api/posts')

    assert res.status_code == 200