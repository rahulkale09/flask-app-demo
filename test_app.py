import pytest
from app import app, db, User  # Import directly from app.py


# -----------------------------
# 1. Pytest fixture for test client
# -----------------------------
@pytest.fixture
def client():
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # create tables in memory
        yield client
        with app.app_context():
            db.drop_all()  # cleanup DB


# -----------------------------
# 2. Pytest fixture to create a test user
# -----------------------------
@pytest.fixture
def test_user(client):
    with client.application.app_context():
        user = User(username="testuser")
        # Use your password hashing method
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
    return user


# -----------------------------
# 3. Homepage tests
# -----------------------------
def test_homepage_redirect(client):
    """Test that '/' redirects (302) if user not logged in."""
    response = client.get("/")
    assert response.status_code == 302


def test_homepage_follow_redirect(client):
    """Test homepage after following redirect."""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data or b"Welcome" in response.data


# -----------------------------
# 4. Login tests
# -----------------------------
def test_login_success(client, test_user):
    """Login with correct credentials should succeed."""
    response = client.post("/login", data=dict(
        username="testuser",
        password="testpass"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Dashboard" in response.data


def test_login_fail(client):
    """Login with wrong credentials should fail."""
    response = client.post("/login", data=dict(
        username="wronguser",
        password="wrongpass"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid credentials" in response.data
