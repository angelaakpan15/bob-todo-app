from unittest.mock import patch
from backend.app import create_app
from backend.database import db
from backend.models import Todo


def test_health_check(client):
    """Test health check endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


# --- GET /api/todos ---

def test_get_todos_empty(client):
    """Test GET /api/todos returns an empty list when no todos exist."""
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_todos_multiple(client, app):
    """Test GET /api/todos returns all todos ordered newest first."""
    with app.app_context():
        todo1 = Todo(title="Task 1", completed=False)
        todo2 = Todo(title="Task 2", completed=True)
        db.session.add_all([todo1, todo2])
        db.session.commit()

    response = client.get("/api/todos")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert {d["title"] for d in data} == {"Task 1", "Task 2"}


def test_get_todos_exception(client):
    """Test GET /api/todos handles database query failure with 500 status."""
    with patch("backend.models.Todo.query") as mock_query:
        mock_query.order_by.side_effect = Exception("DB error")
        response = client.get("/api/todos")
        assert response.status_code == 500
        assert "Failed to retrieve todos" in response.get_json()["error"]


# --- GET /api/todos/<id> ---

def test_get_todo_by_id_success(client, sample_todo):
    """Test GET /api/todos/<id> retrieves an existing todo."""
    response = client.get(f"/api/todos/{sample_todo}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == sample_todo
    assert data["title"] == "Sample Task"
    assert data["description"] == "Sample description"
    assert data["completed"] is False
    assert data["created_at"] is not None


def test_get_todo_by_id_not_found(client):
    """Test GET /api/todos/<id> returns 404 when ID does not exist."""
    response = client.get("/api/todos/9999")
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


# --- POST /api/todos ---

def test_create_todo_minimal_success(client):
    """Test POST /api/todos with title only creates todo with defaults."""
    response = client.post("/api/todos", json={"title": "Buy groceries"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] is not None
    assert data["title"] == "Buy groceries"
    assert data["description"] == ""
    assert data["completed"] is False
    assert data["created_at"] is not None


def test_create_todo_full_payload_success(client):
    """Test POST /api/todos with all fields provided."""
    payload = {
        "title": "Complete assignment",
        "description": "Finish math and science homework",
        "completed": True,
    }
    response = client.post("/api/todos", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Complete assignment"
    assert data["description"] == "Finish math and science homework"
    assert data["completed"] is True


def test_create_todo_invalid_json(client):
    """Test POST /api/todos with non-JSON body returns 400."""
    response = client.post(
        "/api/todos",
        data="not a json",
        content_type="text/plain",
    )
    assert response.status_code == 400
    assert "Invalid request body" in response.get_json()["error"]


def test_create_todo_missing_title(client):
    """Test POST /api/todos without title returns 400."""
    response = client.post("/api/todos", json={"description": "No title here"})
    assert response.status_code == 400
    assert "Field 'title' is required" in response.get_json()["error"]


def test_create_todo_empty_title(client):
    """Test POST /api/todos with empty/whitespace title returns 400."""
    response = client.post("/api/todos", json={"title": "   "})
    assert response.status_code == 400
    assert "Field 'title' is required" in response.get_json()["error"]


def test_create_todo_invalid_description_type(client):
    """Test POST /api/todos with non-string description returns 400."""
    response = client.post(
        "/api/todos",
        json={"title": "Test", "description": 12345},
    )
    assert response.status_code == 400
    assert "Field 'description' must be a string" in response.get_json()["error"]


def test_create_todo_invalid_completed_type(client):
    """Test POST /api/todos with non-boolean completed returns 400."""
    response = client.post(
        "/api/todos",
        json={"title": "Test", "completed": "yes"},
    )
    assert response.status_code == 400
    assert "Field 'completed' must be a boolean" in response.get_json()["error"]


def test_create_todo_commit_error(client):
    """Test POST /api/todos rolls back and returns 500 when db.session.commit fails."""
    with patch("backend.app.db.session.commit", side_effect=Exception("DB write error")):
        response = client.post("/api/todos", json={"title": "Test Task"})
        assert response.status_code == 500
        assert "Failed to create todo" in response.get_json()["error"]


# --- PUT /api/todos/<id> ---

def test_update_todo_title(client, sample_todo):
    """Test PUT /api/todos/<id> updates title successfully."""
    response = client.put(f"/api/todos/{sample_todo}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Sample description"


def test_update_todo_description(client, sample_todo):
    """Test PUT /api/todos/<id> updates description successfully."""
    response = client.put(
        f"/api/todos/{sample_todo}",
        json={"description": "Updated Description"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["description"] == "Updated Description"


def test_update_todo_completed(client, sample_todo):
    """Test PUT /api/todos/<id> updates completed status successfully."""
    response = client.put(f"/api/todos/{sample_todo}", json={"completed": True})
    assert response.status_code == 200
    data = response.get_json()
    assert data["completed"] is True


def test_update_todo_all_fields(client, sample_todo):
    """Test PUT /api/todos/<id> updates all fields at once."""
    response = client.put(
        f"/api/todos/{sample_todo}",
        json={
            "title": "All New Title",
            "description": "All New Description",
            "completed": True,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "All New Title"
    assert data["description"] == "All New Description"
    assert data["completed"] is True


def test_update_todo_not_found(client):
    """Test PUT /api/todos/<id> returns 404 for non-existent ID."""
    response = client.put("/api/todos/9999", json={"title": "New Title"})
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_update_todo_invalid_json(client, sample_todo):
    """Test PUT /api/todos/<id> with non-JSON body returns 400."""
    response = client.put(
        f"/api/todos/{sample_todo}",
        data="not a json",
        content_type="text/plain",
    )
    assert response.status_code == 400
    assert "Invalid request body" in response.get_json()["error"]


def test_update_todo_empty_title(client, sample_todo):
    """Test PUT /api/todos/<id> with empty/whitespace title returns 400."""
    response = client.put(f"/api/todos/{sample_todo}", json={"title": "   "})
    assert response.status_code == 400
    assert "Field 'title' cannot be empty" in response.get_json()["error"]


def test_update_todo_invalid_description_type(client, sample_todo):
    """Test PUT /api/todos/<id> with non-string description returns 400."""
    response = client.put(f"/api/todos/{sample_todo}", json={"description": 999})
    assert response.status_code == 400
    assert "Field 'description' must be a string" in response.get_json()["error"]


def test_update_todo_invalid_completed_type(client, sample_todo):
    """Test PUT /api/todos/<id> with non-boolean completed returns 400."""
    response = client.put(f"/api/todos/{sample_todo}", json={"completed": "not_bool"})
    assert response.status_code == 400
    assert "Field 'completed' must be a boolean" in response.get_json()["error"]


def test_update_todo_commit_error(client, sample_todo):
    """Test PUT /api/todos/<id> rolls back and returns 500 when commit fails."""
    with patch("backend.app.db.session.commit", side_effect=Exception("DB update error")):
        response = client.put(f"/api/todos/{sample_todo}", json={"title": "New Title"})
        assert response.status_code == 500
        assert "Failed to update todo" in response.get_json()["error"]


# --- DELETE /api/todos/<id> ---

def test_delete_todo_success(client, sample_todo):
    """Test DELETE /api/todos/<id> removes the todo successfully."""
    response = client.delete(f"/api/todos/{sample_todo}")
    assert response.status_code == 200
    assert response.get_json()["id"] == sample_todo

    # Confirm it is no longer retrievable
    get_res = client.get(f"/api/todos/{sample_todo}")
    assert get_res.status_code == 404


def test_delete_todo_not_found(client):
    """Test DELETE /api/todos/<id> returns 404 for non-existent ID."""
    response = client.delete("/api/todos/9999")
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_delete_todo_commit_error(client, sample_todo):
    """Test DELETE /api/todos/<id> rolls back and returns 500 when commit fails."""
    with patch("backend.app.db.session.commit", side_effect=Exception("DB delete error")):
        response = client.delete(f"/api/todos/{sample_todo}")
        assert response.status_code == 500
        assert "Failed to delete todo" in response.get_json()["error"]


# --- Model and Error Handlers ---

def test_todo_model_repr(app):
    """Test Todo model __repr__ method."""
    with app.app_context():
        todo = Todo(id=1, title="Test Repr")
        assert repr(todo) == "<Todo 1: Test Repr>"


def test_todo_to_dict_none_fields(app):
    """Test Todo.to_dict handles None description and created_at gracefully."""
    with app.app_context():
        todo = Todo(id=1, title="Test", description=None, created_at=None)
        d = todo.to_dict()
        assert d["description"] == ""
        assert d["created_at"] is None


def test_http_404_json_error(client):
    """Test requesting a non-existent route returns JSON 404."""
    response = client.get("/api/unknown_route")
    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()
    assert data["status_code"] == 404


def test_http_405_json_error(client):
    """Test using unsupported HTTP method returns JSON 405."""
    response = client.patch("/api/health")
    assert response.status_code == 405
    assert response.is_json
    data = response.get_json()
    assert data["status_code"] == 405


def test_generic_exception_handler(app):
    """Test generic exception handler returns 500 JSON for unexpected errors."""
    with app.test_client() as client:
        # Register a temporary route that raises an unhandled generic exception
        @app.route("/api/crash-test")
        def crash():
            raise RuntimeError("Unexpected failure")

        response = client.get("/api/crash-test")
        assert response.status_code == 500
        assert response.is_json
        data = response.get_json()
        assert data["error"] == "Internal server error"
        assert "Unexpected failure" in data["details"]


def test_create_app_oserror_handling():
    """Test create_app handles OSError during instance folder creation."""
    with patch("os.makedirs", side_effect=OSError("Permission denied")):
        test_app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
        assert test_app is not None
