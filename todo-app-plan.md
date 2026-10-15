# Todo Application Plan

## Top-Level Overview

Build a lightweight, full-stack Todo application using a Python Flask REST API backend, SQLite for data persistence with SQLAlchemy ORM, and a responsive Vanilla JavaScript, HTML5, and CSS3 frontend. The app supports essential CRUD operations (Create, Read, Update/Toggle, Delete) for tasks without user authentication.

---

## Architecture & Technology Stack Recommendations

### Technology Stack
- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-CORS
- **Database**: SQLite (file-based `todos.db`, no external server required)
- **Frontend**: Vanilla JavaScript (ES6+ `fetch` API), Semantic HTML5, Modern CSS (Flexbox/CSS Grid)
- **Environment Management**: `venv` / `pip` (`requirements.txt`)

---

## Database Schema

### Table: `todos`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each todo |
| `title` | TEXT / VARCHAR(200) | NOT NULL | Title or description of the task |
| `is_completed` | BOOLEAN | NOT NULL, DEFAULT 0 / FALSE | Completion status |
| `created_at` | DATETIME / TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp when the task was created |
| `updated_at` | DATETIME / TIMESTAMP | NULLABLE / DEFAULT CURRENT_TIMESTAMP | Timestamp when the task was last updated |

---

## REST API Specification

| HTTP Method | Endpoint | Request Body | Response Status | Response Body | Description |
|---|---|---|---|---|---|
| `GET` | `/api/todos` | None | `200 OK` | `[ { "id": 1, "title": "Buy groceries", "is_completed": false, "created_at": "..." } ]` | List all todos |
| `POST` | `/api/todos` | `{"title": "Buy groceries"}` | `201 Created` / `400 Bad Request` | `{ "id": 1, "title": "Buy groceries", "is_completed": false, "created_at": "..." }` | Create a new todo |
| `GET` | `/api/todos/<id>` | None | `200 OK` / `404 Not Found` | `{ "id": 1, "title": "Buy groceries", "is_completed": false, "created_at": "..." }` | Retrieve a single todo |
| `PUT` | `/api/todos/<id>` | `{"title": "...", "is_completed": true}` | `200 OK` / `400 Bad Request` / `404 Not Found` | `{ "id": 1, "title": "...", "is_completed": true, "updated_at": "..." }` | Update title or completion status |
| `DELETE` | `/api/todos/<id>` | None | `200 OK` / `204 No Content` / `404 Not Found` | `{"message": "Todo deleted successfully"}` | Delete a todo item |

---

## Directory Structure

```
todo-app/
├── backend/
│   ├── app.py             # Flask application entry point and routes
│   ├── models.py          # SQLAlchemy Todo model definition
│   ├── database.py        # Database setup and session configuration
│   ├── requirements.txt   # Python dependencies
│   └── instance/          # SQLite database storage directory (instance/todos.db)
├── frontend/
│   ├── index.html         # Main single-page application interface
│   ├── css/
│   │   └── style.css      # Styling for clean, modern todo UI
│   └── js/
│       └── app.js         # DOM manipulation, API client, event handlers
├── .gitignore             # Git ignore file (__pycache__, instance/, *.db, venv/)
└── README.md              # Setup and run instructions
```

---

## Sub-Tasks

### Sub-Task 1: Backend Setup & Database Layer
- **Intent**: Establish the Python backend project structure, dependencies, and database model.
- **Expected Outcomes**:
  - `requirements.txt` with Flask, Flask-SQLAlchemy, Flask-CORS.
  - SQLAlchemy `Todo` model and database initialization script in `backend/`.
- **Todo List**:
  1. [x] Create directory structure for backend and frontend.
  2. [x] Create `backend/requirements.txt`.
  3. [x] Implement `backend/models.py` with `Todo` model and serialization helper.
  4. [x] Implement `backend/database.py` for database instance creation.
- **Relevant Context**: `backend/models.py`, `backend/database.py`
- **Status**: [x] done

### Sub-Task 2: Flask REST API Implementation
- **Intent**: Implement CRUD endpoints to handle todo operations and serve requests.
- **Expected Outcomes**:
  - Flask app running on port 5000 with `/api/todos` CRUD endpoints.
  - CORS enabled to allow requests from frontend.
  - Proper validation and JSON error handling.
- **Todo List**:
  1. [x] Implement Flask routes in `backend/app.py` (`GET`, `POST`, `PUT`, `DELETE`).
  2. [x] Add request validation (non-empty title, boolean status checks).
  3. [x] Enable CORS support for frontend access.
- **Relevant Context**: `backend/app.py`
- **Status**: [x] done

### Sub-Task 3: Frontend Interface & Styling
- **Intent**: Build a clean and responsive user interface for displaying and managing todos.
- **Expected Outcomes**:
  - HTML structure with input form, filter controls (all/active/completed), and todo list container.
  - Modern CSS styling for todo items, completed task strikethrough, and action buttons.
- **Todo List**:
  1. [x] Create `frontend/index.html` with semantic structure.
  2. [x] Create `frontend/styles.css` with responsive layout and interactive states.
- **Relevant Context**: `frontend/index.html`, `frontend/styles.css`
- **Status**: [x] done

### Sub-Task 4: Frontend JavaScript API Integration
- **Intent**: Connect the UI to the Flask backend via `fetch` API.
- **Expected Outcomes**:
  - Todo list renders on page load.
  - Submitting form adds a new item immediately.
  - Clicking checkbox toggles completion status.
  - Clicking delete button removes the item.
- **Todo List**:
  1. [x] Implement API service helper functions in `frontend/app.js`.
  2. [x] Implement UI rendering and event handlers for create, toggle, and delete.
  3. [x] Add basic error feedback / loading indicators.
- **Relevant Context**: `frontend/app.js`
- **Status**: [x] done

### Sub-Task 5: Documentation & End-to-End Verification
- **Intent**: Provide documentation and verify end-to-end functionality.
- **Expected Outcomes**:
  - `README.md` with step-by-step instructions for setup and running.
  - Verified CRUD workflow between frontend and backend.
- **Todo List**:
  1. [x] Create `README.md` with startup commands.
  2. [x] Test API and unit test coverage.
- **Relevant Context**: `README.md`, `tests/test_api.py`
- **Status**: [x] done
