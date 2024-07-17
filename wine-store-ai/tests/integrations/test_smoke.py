import pytest
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "hello world"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    """
    Test the Flask endpoint that returns 'hello world'.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "hello world"

if __name__ == "__main__":
    pytest.main()
