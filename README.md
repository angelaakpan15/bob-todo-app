# Flask & JavaScript Todo Application

A lightweight, full-stack Todo application built with Python (Flask, SQLite, SQLAlchemy) and Vanilla JavaScript (HTML5, modern CSS3).

---

## Features

- **Create Tasks**: Add task title and optional notes/description.
- **View Tasks**: Real-time list of all tasks sorted newest first.
- **Filter**: Filter by *All*, *Active*, and *Completed* tasks.
- **Complete/Toggle**: Check off tasks with visual strikethrough.
- **Delete**: Instant removal with optimistic UI update.
- **Responsive Design**: Clean UI optimized for mobile, tablet, and desktop screens.
- **RESTful API**: Standard JSON API with input validation and HTTP error codes.
- **Test Suite**: 33 unit tests with >94% code coverage using `pytest`.

---

## Project Structure

```
.
├── backend/
│   ├── app.py             # Flask application & REST API routes
│   ├── database.py        # SQLAlchemy database initialization
│   ├── models.py          # Todo database model
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html         # Main application UI
│   ├── styles.css         # Modern, responsive styling
│   └── app.js             # API client & DOM event handling
├── tests/
│   ├── conftest.py        # Pytest fixtures & in-memory DB configuration
│   └── test_api.py        # Comprehensive unit tests
├── pytest.ini             # Pytest configuration
├── todo-app-plan.md       # Implementation plan & architecture
└── README.md              # Project documentation
```

---

## Getting Started

### 1. Backend Setup

```bash
# Navigate to project root
cd /path/to/Bobathon\ Ingram

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the Flask backend (runs on port 5001 by default to avoid macOS AirPlay conflict)
python backend/app.py
```

The backend API will be live at `http://localhost:5001/api`.

### 2. Frontend Setup

You can open [`frontend/index.html`](frontend/index.html) directly in any browser or serve it with Python:

```bash
# In a new terminal window:
python3 -m http.server 3000 --directory frontend
```

Open your browser at **`http://localhost:3000`** (or open [`frontend/index.html`](frontend/index.html)).

---

## Running Unit Tests & Coverage

```bash
# Run pytest with code coverage report
pytest --cov=backend --cov-report=term-missing tests/
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/todos` | List all todos |
| `GET` | `/api/todos/<id>` | Get single todo by ID |
| `POST` | `/api/todos` | Create a new todo |
| `PUT` | `/api/todos/<id>` | Update title, description, or completed status |
| `DELETE` | `/api/todos/<id>` | Delete todo by ID |
