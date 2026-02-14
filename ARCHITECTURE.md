# Sovereign - Addiction Recovery Application

## Database Schema

### PostgreSQL with SQLAlchemy ORM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐       ┌──────────────────┐                          │
│  │      users       │       │    habits         │                          │
│  ├──────────────────┤       ├──────────────────┤                          │
│  │ id (PK)          │       │ id (PK)          │                          │
│  │ email (UK)       │       │ user_id (FK)     │◄──────┐                  │
│  │ username (UK)     │       │ name             │       │                  │
│  │ password_hash    │       │ description      │       │                  │
│  │ is_active        │       │ frequency        │       │                  │
│  │ created_at       │       │ created_at       │       │                  │
│  │ updated_at       │       │ is_active        │       │                  │
│  └────────┬─────────┘       │ updated_at       │       │                  │
│           │                 └──────────────────┘       │                  │
│           │                           │                │                  │
│           │                 ┌─────────▼─────────┐      │                  │
│           │                 │  habit_logs       │      │                  │
│           │                 ├───────────────────┤      │                  │
│           │                 │ id (PK)           │      │                  │
│           └────────────┐   │ habit_id (FK)     │◄─────┘                  │
│                        │   │ user_id (FK)      │                          │
│           ┌───────────▼───┤ completed_at       │◄── millisecond precision │
│           │               │ streak_count       │                          │
│  ┌────────▼────────┐      │ notes              │                          │
│  │ relapse_events │      │ created_at         │                          │
│  ├────────────────┤      └─────────────────────┘                          │
│  │ id (PK)        │                                                        │
│  │ user_id (FK)   │                                                        │
│  │ occurred_at    │◄── millisecond precision                              │
│  │ trigger_type   │                                                        │
│  │ severity       │                                                        │
│  │ notes          │                                                        │
│  │ created_at     │                                                        │
│  └────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Table Definitions

#### 1. users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email address |
| username | VARCHAR(80) | UNIQUE, NOT NULL, INDEX | Display name |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

#### 2. habits
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique habit identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| name | VARCHAR(100) | NOT NULL | Habit name |
| description | TEXT | NULLABLE | Habit description |
| frequency | VARCHAR(20) | NOT NULL, DEFAULT 'daily' | daily/weekly/monthly |
| is_active | BOOLEAN | DEFAULT TRUE | Habit active status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

#### 3. habit_logs
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique log identifier |
| habit_id | UUID | FK -> habits(id), NOT NULL, INDEX | Related habit |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| completed_at | TIMESTAMP | NOT NULL, INDEX | **Millisecond precision** completion time |
| streak_count | INTEGER | DEFAULT 0 | Consecutive completion count |
| notes | TEXT | NULLABLE | Optional completion notes |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |

**Index on completed_at**: `idx_habit_logs_completed_at` for streak calculations

#### 4. relapse_events
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique event identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| occurred_at | TIMESTAMP | NOT NULL, INDEX | **Millisecond precision** event time |
| trigger_type | VARCHAR(50) | NOT NULL | Trigger category |
| severity | INTEGER | NOT NULL, CHECK (1-10) | Severity rating 1-10 |
| notes | TEXT | NULLABLE | Event description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |

**Index on occurred_at**: `idx_relapse_occurred_at` for timeline queries

### Millisecond Precision Implementation

```python
# Python datetime with microsecond precision (PostgreSQL supports microseconds)
from datetime import datetime, timezone

# Store as timezone-aware UTC timestamps
completed_at = datetime.now(timezone.utc)  # Includes microseconds
# Example: 2026-02-14 10:30:45.123456+00:00
```

### Trigger Types (Enum)
- `emotional_distress`
- `social_situation`
- `environmental_cue`
- `stress`
- `peer_pressure`
- `other`

---

## System Architecture Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────────────┐                                │
│                              │   Browser   │                                │
│                              │  (Bootstrap │                                │
│                              │     5 +     │                                │
│                              │    HTMX)    │                                │
│                              └──────┬──────┘                                │
│                                     │                                        │
│                                     │ HTTP/HTTPS                             │
│                                     ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      FLASK APPLICATION                              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                  APPLICATION FACTORY                         │   │   │
│  │  │              (create_app / extensions)                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  │         ┌────────────────────┼────────────────────┐                │   │
│  │         │                    │                    │                │   │
│  │         ▼                    ▼                    ▼                │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│  │  │   ROUTES    │    │  SERVICES   │    │   MODELS    │              │   │
│  │  │  (Blueprints)│    │  (Business  │    │ (SQLAlchemy │              │   │
│  │  │             │    │   Logic)    │    │   Entities) │              │   │
│  │  │ - auth/     │    │ - AuthService│    │ - User      │              │   │
│  │  │ - habits/   │    │ - HabitService│   │ - Habit     │              │   │
│  │  │ - relapse/ │    │ - RelapseService│ │ - HabitLog  │              │   │
│  │  │ - dashboard/   │ - StreakCalculator│ │ - RelapseEvent│            │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘              │   │
│  │         │                    │                    │                │   │
│  │         └────────────────────┼────────────────────┘                │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    EXTENSIONS                               │   │   │
│  │  │  - SQLAlchemy (db)      - Flask-Login (auth)               │   │   │
│  │  │  - Flask-WTF (CSRF)     - Flask-Migrate (migrations)       │   │   │
│  │  │  - Flask-Bcrypt (hash)  - Flask-DebugToolbar (dev)        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  └──────────────────────────────┼───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    POSTGRESQL DATABASE                               │  │
│  │              (Tables, Indexes, Constraints)                         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DIRECTORY STRUCTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  sovereign/                          # Project Root                         │
│  ├── app/                            # Application Package                   │
│  │   ├── __init__.py                 # App Factory + Extensions             │
│  │   ├── config.py                   # Configuration Classes                 │
│  │   ├── models/                     # SQLAlchemy Models                     │
│  │   │   ├── __init__.py                                                  │
│  │   │   ├── user.py                                                     │
│  │   │   ├── habit.py                                                     │
│  │   │   ├── habit_log.py                                                │
│  │   │   └── relapse_event.py                                            │
│  │   ├── blueprints/                # Flask Blueprints                      │
│  │   │   ├── __init__.py                                                  │
│  │   │   ├── auth.py                                                     │
│  │   │   ├── habits.py                                                   │
│  │   │   ├── relapse.py                                                  │
│  │   │   └── dashboard.py                                                │
│  │   ├── services/                  # Business Logic                        │
│  │   │   ├── __init__.py                                                  │
│  │   │   ├── auth_service.py                                             │
│  │   │   ├── habit_service.py                                            │
│  │   │   ├── relapse_service.py                                          │
│  │   │   └── streak_service.py                                           │
│  │   ├── templates/                 # Jinja2 Templates                      │
│  │   │   ├── base.html                                                  │
│  │   │   ├── auth/                                                      │
│  │   │   ├── habits/                                                    │
│  │   │   ├── relapse/                                                   │
│  │   │   └── dashboard/                                                 │
│  │   ├── static/                    # CSS/JS/Images                         │
│  │   │   ├── css/                                                         │
│  │   │   └── js/                                                          │
│  │   └── utils/                      # Utility Functions                     │
│  │       ├── __init__.py                                                  │
│  │       └── errors.py                                                   │
│  ├── migrations/                    # Flask-Migrate                          │
│  ├── tests/                         # Pytest Test Suite                      │
│  │   ├── __init__.py                                                    │
│  │   ├── conftest.py                                                     │
│  │   ├── test_models/                                                     │
│  │   ├── test_services/                                                   │
│  │   └── test_blueprints/                                                 │
│  ├── .env                          # Environment Variables                   │
│  ├── .env.example                                                        │
│  ├── requirements.txt             # Python Dependencies                     │
│  ├── pytest.ini                    # Pytest Configuration                    │
│  └── run.py                       # Application Entry Point                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        REQUEST FLOW (HTMX)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. User clicks "Complete Habit" button                                   │
│     │                                                                       │
│     ▼                                                                       │
│  2. HTMX sends POST /habits/1/complete                                     │
│     │                                                                       │
│     ▼                                                                       │
│  3. Flask Blueprint processes request + CSRF validation                   │
│     │                                                                       │
│     ▼                                                                       │
│  4. Service layer calculates streak + logs completion                      │
│     │                                                                       │
│     ▼                                                                       │
│  5. Database updates with millisecond-precision timestamp                   │
│     │                                                                       │
│     ▼                                                                       │
│  6. Service returns HTML fragment (updated streak card)                     │
│     │                                                                       │
│     ▼                                                                       │
│  7. HTMX swaps content without page refresh                                │
│     │                                                                       │
│     ▼                                                                       │
│  8. User sees updated streak in real-time                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY IMPLEMENTATIONS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. CSRF Protection                                                         │
│     - Flask-WTF form tokens on all POST forms                              │
│     - HTMX: X-CSRFToken header on AJAX requests                            │
│                                                                             │
│  2. Authentication                                                          │
│     - Flask-Login session management                                        │
│     - Bcrypt password hashing                                              │
│     - Login required decorators                                             │
│                                                                             │
│  3. Global Error Handling                                                   │
│     - Custom error handlers (400, 404, 500)                                │
│     - @app.errorhandler decorators                                          │
│     - Structured error logging                                             │
│                                                                             │
│  4. Input Validation                                                        │
│     - WTForms for form validation                                          │
│     - SQLAlchemy parameterized queries (ORM prevents SQLi)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3.x |
| Database | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.x |
| Migrations | Flask-Migrate |
| Authentication | Flask-Login + Flask-Bcrypt |
| Forms | Flask-WTF |
| Frontend | Bootstrap 5.3 + HTMX |
| Testing | Pytest + Fixtures |
| Deploy | Gunicorn (production) |

---

*Document Version: 1.0*
*Project: Sovereign - Addiction Recovery Application*
