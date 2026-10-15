/**
 * Todo Application Client
 * Handles API communication, UI state management, and DOM updates.
 */

// Configuration - Detect API URL (supports port 5001 or 5000)
const API_BASE_URL = window.API_BASE_URL || "http://localhost:5001/api";

// App State
const state = {
  todos: [],
  currentFilter: "all",
  isLoading: false,
};

// DOM Elements
const elements = {
  form: document.getElementById("todo-form"),
  titleInput: document.getElementById("todo-title"),
  descInput: document.getElementById("todo-description"),
  addBtn: document.getElementById("add-btn"),
  todoList: document.getElementById("todo-list"),
  emptyState: document.getElementById("empty-state"),
  emptyTitle: document.getElementById("empty-title"),
  emptySubtitle: document.getElementById("empty-subtitle"),
  loadingSpinner: document.getElementById("loading-spinner"),
  notification: document.getElementById("notification"),
  activeCount: document.getElementById("active-count"),
  filterButtons: document.querySelectorAll(".filter-btn"),
};

// ==========================================================================
// API Service Layer
// ==========================================================================

async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
      },
      ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMessage = data.error || `Request failed with status ${response.status}`;
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    // If connection refused on 5001, try port 5000 fallback
    if (error.message.includes("Failed to fetch") && API_BASE_URL.includes("5001")) {
      try {
        const fallbackUrl = API_BASE_URL.replace("5001", "5000");
        const fallbackResponse = await fetch(`${fallbackUrl}${endpoint}`, {
          headers: { "Content-Type": "application/json" },
          ...options,
        });
        if (fallbackResponse.ok) {
          return await fallbackResponse.json();
        }
      } catch {
        // Ignore fallback error and rethrow original
      }
    }
    throw error;
  }
}

async function apiGetTodos() {
  return await apiRequest("/todos");
}

async function apiCreateTodo(title, description = "") {
  return await apiRequest("/todos", {
    method: "POST",
    body: JSON.stringify({ title, description }),
  });
}

async function apiUpdateTodo(id, updates) {
  return await apiRequest(`/todos/${id}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

async function apiDeleteTodo(id) {
  return await apiRequest(`/todos/${id}`, {
    method: "DELETE",
  });
}

// ==========================================================================
// UI Notifications & Feedback
// ==========================================================================

let notificationTimer = null;

function showNotification(message, type = "error") {
  if (!elements.notification) return;

  clearTimeout(notificationTimer);
  elements.notification.textContent = message;
  elements.notification.className = `notification ${type}`;

  notificationTimer = setTimeout(() => {
    elements.notification.className = "notification hidden";
    elements.notification.textContent = "";
  }, 4000);
}

function setLoading(isLoading) {
  state.isLoading = isLoading;
  if (elements.loadingSpinner) {
    elements.loadingSpinner.classList.toggle("hidden", !isLoading);
  }
  if (elements.addBtn) {
    elements.addBtn.disabled = isLoading;
  }
}

// ==========================================================================
// Rendering & DOM Management
// ==========================================================================

function formatTimestamp(isoString) {
  if (!isoString) return "";
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function renderTodos() {
  const { todos, currentFilter } = state;

  // Filter items
  const filtered = todos.filter((todo) => {
    if (currentFilter === "active") return !todo.completed;
    if (currentFilter === "completed") return todo.completed;
    return true;
  });

  // Update counts
  const activeCount = todos.filter((t) => !t.completed).length;
  if (elements.activeCount) {
    elements.activeCount.textContent = `${activeCount} task${activeCount === 1 ? "" : "s"} left`;
  }

  // Clear list
  elements.todoList.innerHTML = "";

  // Handle empty state
  if (filtered.length === 0) {
    elements.emptyState.classList.remove("hidden");
    if (currentFilter === "completed") {
      elements.emptyTitle.textContent = "No completed tasks yet";
      elements.emptySubtitle.textContent = "Check off tasks when you finish them!";
    } else if (currentFilter === "active") {
      elements.emptyTitle.textContent = "All caught up!";
      elements.emptySubtitle.textContent = "No active tasks remaining.";
    } else {
      elements.emptyTitle.textContent = "No tasks found";
      elements.emptySubtitle.textContent = "Add a task above to get started!";
    }
  } else {
    elements.emptyState.classList.add("hidden");

    // Populate todo items
    filtered.forEach((todo) => {
      const li = document.createElement("li");
      li.className = `todo-item ${todo.completed ? "completed" : ""}`;
      li.dataset.id = todo.id;

      // Checkbox container
      const checkboxContainer = document.createElement("label");
      checkboxContainer.className = "checkbox-container";
      checkboxContainer.setAttribute("aria-label", `Mark "${todo.title}" as ${todo.completed ? "incomplete" : "complete"}`);

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.className = "todo-checkbox";
      checkbox.checked = todo.completed;
      checkbox.addEventListener("change", () => handleToggleTodo(todo.id, checkbox.checked));
      checkboxContainer.appendChild(checkbox);

      // Content container
      const contentDiv = document.createElement("div");
      contentDiv.className = "todo-content";

      const titleSpan = document.createElement("span");
      titleSpan.className = "todo-title";
      titleSpan.textContent = todo.title;
      contentDiv.appendChild(titleSpan);

      if (todo.description) {
        const descSpan = document.createElement("span");
        descSpan.className = "todo-desc";
        descSpan.textContent = todo.description;
        contentDiv.appendChild(descSpan);
      }

      if (todo.created_at) {
        const timeSpan = document.createElement("span");
        timeSpan.className = "todo-time";
        timeSpan.textContent = formatTimestamp(todo.created_at);
        contentDiv.appendChild(timeSpan);
      }

      // Actions container
      const actionsDiv = document.createElement("div");
      actionsDiv.className = "todo-actions";

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "btn-delete";
      deleteBtn.innerHTML = "🗑️";
      deleteBtn.setAttribute("aria-label", `Delete "${todo.title}"`);
      deleteBtn.title = "Delete task";
      deleteBtn.addEventListener("click", () => handleDeleteTodo(todo.id));
      actionsDiv.appendChild(deleteBtn);

      // Assemble list item
      li.appendChild(checkboxContainer);
      li.appendChild(contentDiv);
      li.appendChild(actionsDiv);

      elements.todoList.appendChild(li);
    });
  }
}

// ==========================================================================
// Event Handlers
// ==========================================================================

async function loadTodos() {
  setLoading(true);
  try {
    const data = await apiGetTodos();
    state.todos = Array.isArray(data) ? data : [];
    renderTodos();
  } catch (error) {
    showNotification(`Could not load tasks. Ensure backend server is running. (${error.message})`, "error");
  } finally {
    setLoading(false);
  }
}

async function handleAddTodo(event) {
  event.preventDefault();

  const title = elements.titleInput.value.trim();
  const description = elements.descInput.value.trim();

  if (!title) {
    showNotification("Task title cannot be empty.", "error");
    elements.titleInput.focus();
    return;
  }

  setLoading(true);
  try {
    const newTodo = await apiCreateTodo(title, description);
    state.todos.unshift(newTodo);
    elements.form.reset();
    elements.titleInput.focus();
    renderTodos();
    showNotification("Task added successfully!", "success");
  } catch (error) {
    showNotification(`Failed to create task: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}

async function handleToggleTodo(id, completed) {
  const previousState = state.todos.map((t) => ({ ...t }));
  // Optimistic UI update
  state.todos = state.todos.map((t) => (t.id === id ? { ...t, completed } : t));
  renderTodos();

  try {
    const updated = await apiUpdateTodo(id, { completed });
    state.todos = state.todos.map((t) => (t.id === id ? updated : t));
    renderTodos();
  } catch (error) {
    // Revert state on error
    state.todos = previousState;
    renderTodos();
    showNotification(`Failed to update task: ${error.message}`, "error");
  }
}

async function handleDeleteTodo(id) {
  const previousState = state.todos.map((t) => ({ ...t }));
  // Optimistic UI update
  state.todos = state.todos.filter((t) => t.id !== id);
  renderTodos();

  try {
    await apiDeleteTodo(id);
    showNotification("Task deleted.", "success");
  } catch (error) {
    // Revert state on error
    state.todos = previousState;
    renderTodos();
    showNotification(`Failed to delete task: ${error.message}`, "error");
  }
}

function handleFilterChange(filter) {
  state.currentFilter = filter;
  elements.filterButtons.forEach((btn) => {
    const isActive = btn.dataset.filter === filter;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-selected", isActive ? "true" : "false");
  });
  renderTodos();
}

// ==========================================================================
// Initialization
// ==========================================================================

function init() {
  // Bind form submission
  if (elements.form) {
    elements.form.addEventListener("submit", handleAddTodo);
  }

  // Bind filter buttons
  elements.filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const filter = btn.dataset.filter;
      handleFilterChange(filter);
    });
  });

  // Initial fetch
  loadTodos();
}

// Run on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
