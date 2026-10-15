import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

try:
    from backend.database import db, init_db
    from backend.models import Todo
except ImportError:
    from database import db, init_db
    from models import Todo


def create_app(test_config=None):
    """Application factory for Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'todos.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Enable CORS for all routes
    CORS(app)

    # Initialize database
    init_db(app)

    # --- Error Handlers ---

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        return (
            jsonify({"error": e.description, "status_code": e.code}),
            e.code,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Catch-all error handler for unexpected server errors."""
        return (
            jsonify({"error": "Internal server error", "details": str(e)}),
            500,
        )

    # --- Routes ---

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route("/api/todos", methods=["GET"])
    def get_todos():
        """List all todos, ordered by creation date descending."""
        try:
            todos = Todo.query.order_by(Todo.created_at.desc()).all()
            return jsonify([todo.to_dict() for todo in todos]), 200
        except Exception as e:
            return jsonify({"error": "Failed to retrieve todos", "details": str(e)}), 500

    @app.route("/api/todos/<int:todo_id>", methods=["GET"])
    def get_todo(todo_id):
        """Retrieve a single todo by its ID."""
        todo = db.session.get(Todo, todo_id)
        if not todo:
            return jsonify({"error": f"Todo with id {todo_id} not found"}), 404
        return jsonify(todo.to_dict()), 200

    @app.route("/api/todos", methods=["POST"])
    def create_todo():
        """Create a new todo item."""
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return (
                jsonify({"error": "Invalid request body. JSON object expected."}),
                400,
            )

        title = data.get("title")
        if not title or not isinstance(title, str) or not title.strip():
            return (
                jsonify({"error": "Field 'title' is required and cannot be empty."}),
                400,
            )

        description = data.get("description", "")
        if description is not None and not isinstance(description, str):
            return (
                jsonify({"error": "Field 'description' must be a string."}),
                400,
            )

        completed = data.get("completed", False)
        if not isinstance(completed, bool):
            return (
                jsonify({"error": "Field 'completed' must be a boolean."}),
                400,
            )

        new_todo = Todo(
            title=title.strip(),
            description=description.strip() if description else "",
            completed=completed,
        )

        try:
            db.session.add(new_todo)
            db.session.commit()
            return jsonify(new_todo.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to create todo", "details": str(e)}), 500

    @app.route("/api/todos/<int:todo_id>", methods=["PUT"])
    def update_todo(todo_id):
        """Update an existing todo item."""
        todo = db.session.get(Todo, todo_id)
        if not todo:
            return jsonify({"error": f"Todo with id {todo_id} not found"}), 404

        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return (
                jsonify({"error": "Invalid request body. JSON object expected."}),
                400,
            )

        # Validate title if present
        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                return (
                    jsonify({"error": "Field 'title' cannot be empty."}),
                    400,
                )
            todo.title = title.strip()

        # Validate description if present
        if "description" in data:
            description = data["description"]
            if description is not None and not isinstance(description, str):
                return (
                    jsonify({"error": "Field 'description' must be a string."}),
                    400,
                )
            todo.description = description.strip() if description else ""

        # Validate completed if present
        if "completed" in data:
            completed = data["completed"]
            if not isinstance(completed, bool):
                return (
                    jsonify({"error": "Field 'completed' must be a boolean."}),
                    400,
                )
            todo.completed = completed

        try:
            db.session.commit()
            return jsonify(todo.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to update todo", "details": str(e)}), 500

    @app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
    def delete_todo(todo_id):
        """Delete a todo item."""
        todo = db.session.get(Todo, todo_id)
        if not todo:
            return jsonify({"error": f"Todo with id {todo_id} not found"}), 404

        try:
            db.session.delete(todo)
            db.session.commit()
            return (
                jsonify({"message": f"Todo with id {todo_id} successfully deleted", "id": todo_id}),
                200,
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to delete todo", "details": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
