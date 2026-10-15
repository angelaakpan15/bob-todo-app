from datetime import datetime, timezone

try:
    from backend.database import db
except ImportError:
    from database import db


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True, default="")
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self):
        """Serialize Todo model instance to JSON-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Todo {self.id}: {self.title}>"
