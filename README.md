# Café Employee Manager

A full-stack web application for managing cafes and their employees.

## Tech Stack

| Layer     | Technology                                     |
|-----------|------------------------------------------------|
| Frontend  | React 18 (Vite), Ant Design, AG Grid, TanStack Query |
| Backend   | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| Database  | PostgreSQL 15                                  |
| Infra     | Docker, Docker Compose, Nginx                  |

## Architecture

The backend follows **Clean Architecture** with:
- **CQRS** — `commands/` for writes, `queries/` for reads; route handlers never touch the DB directly
- **Mediator Pattern** — `mediator.py` dispatches commands/queries; routes are fully decoupled from handlers
- **Dependency Injection** — FastAPI's `Depends()` injects the `Mediator` into each route (Python equivalent of Autofac)

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2 (bundled with Docker Desktop)

---

## Running the Application

```bash
# Clone or unzip the project
cd cafe-manager

# Build images and start all services (db + backend + frontend)
docker-compose up --build
```

Services start in this order: **PostgreSQL → Backend (runs `alembic upgrade head`) → Frontend**.

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost             |
| Backend API | http://localhost:8000     |
| API Docs | http://localhost:8000/docs   |

Frontend API/static calls are routed through the frontend host:
- `/api/*` → backend API
- `/static/*` → backend static files

For local Vite development, this is handled by the Vite proxy.
For Docker/Nginx, this is handled by `frontend/nginx.conf`.

---

## Seeding the Database

After the containers are running, seed with sample data:

```bash
docker-compose exec backend python seed.py
```

This inserts:
- **4 cafes**: The Daily Grind (Orchard), Brew & Co (Marina Bay), Kopi Corner (Tampines), Bean There (Jurong)
- **8 employees**: 6 assigned to cafes (with varying start dates), 2 unassigned

The script is **startup-safe**:
- If cafes already exist, it skips seeding.
- Use `--force` to wipe and re-seed everything.

```bash
docker-compose exec backend python seed.py --force
```

---

## API Reference

Base URL: `http://localhost:8000`

### Cafes

| Method | Path              | Description                                      |
|--------|-------------------|--------------------------------------------------|
| GET    | `/cafes`          | List all cafes, sorted by employee count desc    |
| GET    | `/cafes?location=Orchard` | Filter cafes by location (case-insensitive) |
| POST   | `/cafes`          | Create a new cafe (multipart/form-data)          |
| PUT    | `/cafes/{id}`     | Update a cafe (multipart/form-data)              |
| DELETE | `/cafes/{id}`     | Delete a cafe, all assignments, and employees assigned to that cafe |

### Employees

| Method | Path                  | Description                                  |
|--------|-----------------------|----------------------------------------------|
| GET    | `/employees`          | List all employees, sorted by days_worked desc |
| GET    | `/employees?cafe=Name` | Filter employees by cafe name               |
| POST   | `/employees`          | Create employee + optional cafe assignment   |
| PUT    | `/employees/{id}`     | Update employee + cafe assignment            |
| DELETE | `/employees/{id}`     | Delete an employee                           |

Interactive API docs: **http://localhost:8000/docs**

---

## Running Tests

Backend tests are written with **pytest**.

```bash
docker-compose exec backend pytest -q
```

---

## Project Structure

```
cafe-manager/
├── backend/
│   ├── app/
│   │   ├── api/            # Route handlers (HTTP only — no DB logic)
│   │   │   ├── cafes.py
│   │   │   └── employees.py
│   │   ├── commands/       # CQRS writes
│   │   │   ├── cafe_commands.py
│   │   │   └── employee_commands.py
│   │   ├── queries/        # CQRS reads
│   │   │   ├── cafe_queries.py
│   │   │   └── employee_queries.py
│   │   ├── mediator.py     # Mediator pattern dispatcher
│   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── cafe.py
│   │   │   ├── employee.py
│   │   │   └── __init__.py
│   │   ├── schemas/        # Pydantic validation schemas
│   │   │   ├── cafe.py
│   │   │   ├── employee.py
│   │   │   └── __init__.py
│   │   ├── db.py           # DB session setup
│   │   └── main.py         # FastAPI app + CORS + static files
│   ├── alembic/            # Database migrations
│   ├── static/logos/       # Uploaded cafe logos
│   ├── seed.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios API clients
│   │   ├── components/     # TextInput reusable component
│   │   └── pages/          # CafesPage, EmployeesPage, AddEdit pages
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

---

## Stopping the Application

```bash
docker-compose down          # stop containers
docker-compose down -v       # stop and remove the database volume
```
