# FlyRank Tiny Task API

A simple REST API for managing tasks, built with FastAPI and Pydantic. It supports full create, read, update, and delete (CRUD) operations, input validation, and automatically generated interactive documentation.

## Features

- Retrieve all tasks or a single task by ID.
- Create tasks with a required title.
- Update a task's title or completion status.
- Delete tasks by ID.
- Return `400` for invalid data and `404` when a task cannot be found.
- Provide automatic Swagger UI and ReDoc documentation.

> [!NOTE]
> Data is currently stored in memory. All changes are lost and the initial sample tasks are restored whenever the server restarts.

## Requirements

- Python 3.10 or later
- `pip`

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/tranhau2005/flyrank_tiny_api.git
cd flyrank_tiny_api
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the application

```bash
uvicorn main:app --reload --port 8000
```

The server runs at `http://127.0.0.1:8000` by default.

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

| Method | Endpoint | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/` | Return basic API information | `200` |
| `GET` | `/health` | Check the server status | `200` |
| `GET` | `/tasks` | Return all tasks | `200` |
| `GET` | `/tasks/{id}` | Return a task by ID | `200` |
| `POST` | `/tasks` | Create a task | `201` |
| `PUT` | `/tasks/{id}` | Update one or more task fields | `200` |
| `DELETE` | `/tasks/{id}` | Delete a task by ID | `204` |

Each task has the following structure:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "done": false
}
```

## Usage examples

### Retrieve all tasks

```bash
curl http://127.0.0.1:8000/tasks
```

### Retrieve a task by ID

```bash
curl http://127.0.0.1:8000/tasks/1
```

If the ID does not exist, the API returns `404`:

```json
{
  "detail": "Task 999 was not found"
}
```

### Create a task

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write project documentation"}'
```

Response:

```json
{
  "id": 4,
  "title": "Write project documentation",
  "done": false
}
```

The `title` field cannot be empty. Leading and trailing whitespace is removed before the task is stored.

### Update a task

The request may include `title`, `done`, or both fields:

```bash
curl -X PUT http://127.0.0.1:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"title":"Finish project documentation","done":true}'
```

The request must contain at least one field. `title` cannot be empty, and `done` cannot be `null` or an empty string.

### Delete a task

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/4
```

After a successful deletion, the API returns `204 No Content` with an empty response body.

### Check the server status

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "oke"
}
```

## Project structure

```text
flyrank_tiny_api/
├── main.py           # Application, schemas, and API endpoints
├── requirements.txt  # Python dependencies
└── README.md          # Project documentation
```
