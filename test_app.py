import pytest
from app import app, db
from flask import url_for


# -----------------------------
# 1. Pytest fixture for test client
# -----------------------------
@pytest.fixture
def client():
    # Use Flask's test client
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # If using Flask-WTF forms
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for tests

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # create tables in memory
        yield client
        with app.app_context():
            db.drop_all()  # cleanup DB


# -----------------------------
# 2. Test homepage
# -----------------------------
def test_homepage_redirect(client):
    """
    Test that '/' redirects (302) if user not logged in.
    """
    response = client.get("/")
    assert response.status_code == 302  # redirect to /login or another route


def test_homepage_follow_redirect(client):
    """
    Test homepage after following redirect.
    """
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data or b"Welcome" in response.data  # check content


# -----------------------------
# 3. Test login functionality (example)
# -----------------------------
def test_login(client):
    # Example: POST to login route
    response = client.post("/login", data=dict(
        username="testuser",
        password="testpass"
    ), follow_redirects=True)

    # If login successful, you should see homepage content
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Dashboard" in response.data
