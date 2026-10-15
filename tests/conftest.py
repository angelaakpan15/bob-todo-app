import pytest
from backend.app import create_app
from backend.database import db
from backend.models import Todo


@pytest.fixture
def app():
    """Create and configure a fresh Flask app instance for each test."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for issuing requests."""
    return app.test_client()


@pytest.fixture
def sample_todo(app):
    """Create a sample todo in the test database."""
    with app.app_context():
        todo = Todo(
            title="Sample Task",
            description="Sample description",
            completed=False,
        )
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    return todo_id
