# Notes App — Flask Backend (Session Auth)

A secure Flask REST API backend for a productivity app. Users can sign up,
log in, and manage their own private notes. Authentication is handled with
Flask's server-side sessions (cookie-based) and passwords are hashed with
`flask-bcrypt`. Every notes endpoint is protected so that a user can only
ever see or modify their own records.

Built to pair with the session-based version of the provided React client.

## Features

- Signup / login / logout / check-session (`/me`) endpoints
- Passwords hashed with bcrypt, never returned in any response
- Unique usernames enforced at the model and database level
- A `Note` resource (title, content, timestamps) owned by a `User`
- Full CRUD on notes, scoped to the logged-in user
- Pagination on the notes index route (`?page=&per_page=`)
- Request validation with Marshmallow schemas
- Seed script using Faker for realistic sample data

## Project Structure
├── app.py # entry point ("flask run" target)
├── seed.py # populates the database with sample data
├── requirements.txt
├── migrations/ # flask-migrate/alembic migrations
├── server/
│ ├── init.py # application factory (create_app)
│ ├── config.py # DB URI / secret key config
│ ├── extensions.py # shared db, migrate, bcrypt instances
│ ├── models.py # User and Note SQLAlchemy models
│ ├── schemas.py # Marshmallow request-validation schemas
│ ├── auth.py # current_user() + login_required decorator
│ └── routes/
│ ├── init.py
│ ├── auth_routes.py # /signup /login /logout /me
│ └── note_routes.py # /notes CRUD + pagination
└── tests/
└── test_app.py # pytest suite for auth + notes ownership


## Installation

1. Clone the repo and create a virtual environment:

```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

2. Set the Flask app environment variable:

```bash
   export FLASK_APP=app.py      # Windows (cmd): set FLASK_APP=app.py
```

3. Create the database and run migrations:

```bash
   flask db init          # only the very first time
   flask db migrate -m "initial migration"
   flask db upgrade
```

4. Seed the database with example users and notes:

```bash
   python seed.py
```

   This creates a demo account you can log in with immediately:
   - **username:** `demo`
   - **password:** `password123`

## Running the app

```bash
flask run --port 5555
```

The API will be available at `http://127.0.0.1:5555`.

Point the **session-based** version of the provided frontend client at this
URL. Because auth relies on a session cookie, the frontend must send
requests with `credentials: "include"`.

## Running tests

```bash
pytest
```

## API Endpoints

### Auth

| Method | Endpoint   | Description                                             | Auth required |
|--------|------------|------------------------------------------------------------|----------------|
| POST   | `/signup`  | Create a new user (`username`, `password`), logs them in   | No             |
| POST   | `/login`   | Log in with `username` + `password`                        | No             |
| DELETE | `/logout`  | Clear the current session                                   | Yes            |
| GET    | `/me`      | Return the logged-in user, or 401 if not logged in           | Yes            |

### Notes

All notes endpoints require a valid session (send the session cookie) and
only ever operate on notes owned by the current user. Requesting or
modifying another user's note returns `404`.

| Method | Endpoint          | Description                                              |
|--------|-------------------|--------------------------------------------------------------|
| GET    | `/notes`          | List the current user's notes. Supports `?page=` and `?per_page=` (defaults 1 / 10, max 100) |
| POST   | `/notes`          | Create a note. Body: `{ "title": str, "content": str }`       |
| GET    | `/notes/<id>`     | Get a single note owned by the current user                    |
| PATCH  | `/notes/<id>`     | Update `title` and/or `content` of an owned note                 |
| DELETE | `/notes/<id>`     | Delete an owned note                                             |

#### Example: paginated index response

```json
{
  "notes": [ { "id": 1, "title": "...", "content": "...", "user_id": 1, "created_at": "...", "updated_at": null } ],
  "page": 1,
  "per_page": 10,
  "total": 25,
  "total_pages": 3
}
```

## Notes on security

- Passwords are never stored or returned in plaintext; only a bcrypt hash
  is persisted, and the `password_hash` property raises an error if read.
- Every notes route is wrapped in a `login_required` decorator that checks
  `session["user_id"]` and injects the current `User` into the view.
- Ownership is enforced at the query level (`Note.query.filter_by(id=..., user_id=user.id)`),
  so a user can't access another user's note even if they know its id.

