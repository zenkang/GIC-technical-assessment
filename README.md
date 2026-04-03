# Cafe Employee Manager

A cafe-and-employee management app built for the GIC Digital Platform internship assessment. The backend uses Python/FastAPI with Clean Architecture patterns (CQRS, Mediator, DI); the frontend is React with Ant Design, AG Grid, and TanStack Query. Everything runs in Docker Compose.

**Live demo:** [_\[Railway URL here\]_](https://cafe-manager.up.railway.app/)

---

## Tech Stack

| Layer    | Technology                                            |
| -------- | ----------------------------------------------------- |
| Frontend | React 18 (Vite), Ant Design 5, AG Grid 32, TanStack Query 5 |
| Backend  | Python 3.11, FastAPI, SQLAlchemy (async), Alembic     |
| Database | PostgreSQL 15                                         |
| Infra    | Docker Compose, Nginx (reverse proxy + SPA), Railway  |

---

## Architecture

The backend follows **Clean Architecture** with three patterns the assessment asks for:

- **CQRS** -- `commands/` for writes, `queries/` for reads. Each command/query has an `execute(db)` method. Route handlers never touch the DB directly.
- **Mediator** -- `mediator.py` dispatches commands and queries. Routes call `mediator.send(SomeCommand(...))`, keeping the HTTP layer decoupled from business logic.
- **Dependency Injection** -- FastAPI's `Depends()` injects the `Mediator` (and its DB session) into each route. This is the Python equivalent of Autofac.

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) >= 24
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2 (bundled with Docker Desktop)

### Run locally

```bash
cd cafe-manager
docker-compose up --build
```

Services start in order: **PostgreSQL -> Backend (runs migrations + seed) -> Frontend**.

| Service     | URL                        |
| ----------- | -------------------------- |
| Frontend    | http://localhost            |
| Backend API | http://localhost:8000       |
| API Docs    | http://localhost:8000/docs  |

Frontend API and static file requests are proxied through nginx:
- `/api/*` -> backend API
- `/static/*` -> backend static files (logos)

### Seed data

The seed script runs automatically on first startup. If the `cafes` table already has rows, it skips entirely -- it won't overwrite your data.

To force a full re-seed (wipes everything and re-inserts):

```bash
docker-compose exec backend python seed.py --force
```

Sample data: 4 cafes (Orchard, Marina Bay, Tampines, Jurong) and 8 employees (6 assigned, 2 unassigned).

---

## API Endpoints

Base URL: `http://localhost:8000`

### Cafes

| Method | Path            | Description                                              |
| ------ | --------------- | -------------------------------------------------------- |
| GET    | `/cafes`        | List all cafes, sorted by employee count desc            |
| GET    | `/cafes?location=X` | Filter by location (case-insensitive exact match)   |
| POST   | `/cafes`        | Create a cafe (multipart/form-data for logo upload)      |
| PUT    | `/cafes/{id}`   | Update a cafe                                            |
| DELETE | `/cafes/{id}`   | Delete a cafe, its assignments, and employees assigned to it |

### Employees

| Method | Path               | Description                                       |
| ------ | ------------------ | ------------------------------------------------- |
| GET    | `/employees`       | List all employees, sorted by days_worked desc    |
| GET    | `/employees?cafe=X`| Filter by cafe name                               |
| POST   | `/employees`       | Create employee + optional cafe assignment        |
| PUT    | `/employees/{id}`  | Update employee + cafe assignment                 |
| DELETE | `/employees/{id}`  | Delete an employee                                |

Interactive docs at **/docs** (Swagger UI).

---

## Project Structure

```
cafe-manager/
├── backend/
│   ├── app/
│   │   ├── api/              # Route handlers (HTTP layer only)
│   │   │   ├── cafes.py
│   │   │   └── employees.py
│   │   ├── commands/         # CQRS write operations
│   │   │   ├── cafe_commands.py
│   │   │   └── employee_commands.py
│   │   ├── queries/          # CQRS read operations
│   │   │   ├── cafe_queries.py
│   │   │   └── employee_queries.py
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── cafe.py
│   │   │   └── employee.py
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   ├── cafe.py
│   │   │   └── employee.py
│   │   ├── mediator.py       # Mediator pattern dispatcher
│   │   ├── db.py             # DB engine + session setup
│   │   └── main.py           # FastAPI app, CORS, static mount
│   ├── alembic/              # Database migrations
│   ├── tests/                # pytest test suite
│   ├── static/logos/         # Uploaded cafe logos
│   ├── seed.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios HTTP clients
│   │   ├── components/       # Reusable TextInput component
│   │   ├── pages/            # CafesPage, EmployeesPage, Add/Edit pages
│   │   └── styles/           # Custom CSS (dark theme, GIC-inspired palette)
│   │       └── app.css
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Running Tests

```bash
docker-compose exec backend pytest -v
```

---

## Trade-offs and Limitations

Things I'd do differently in a production setting or with more time:

- **No GET /employees/:id endpoint.** The edit page fetches all employees and filters client-side, but I'd add a dedicated endpoint at scale.
- **AG Grid is heavy for this table size.** A plain Antd Table would be simpler for 4-8 rows, but the assignment specifically requires AG Grid.
- **No authentication.** This is a demo app. In production, every mutation endpoint would sit behind auth middleware.
- **No Tailwind CSS.** The assessment mentions it as a nice-to-have. I considered adding it, but with only 6 components, a single custom CSS file with CSS variables achieves the same result with less tooling overhead.
- **Logo storage is local disk.** Logos are saved to `/static/logos/` and served through nginx. A production system would use cloud object storage (S3/GCS) with a CDN.

---

## Stopping the App

```bash
docker-compose down          # stop containers
docker-compose down -v       # stop + delete the database volume
```
