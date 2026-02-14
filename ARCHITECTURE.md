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
│  │ username (UK)    │       │ name             │       │                  │
│  │ password_hash    │       │ description      │       │                  │
│  │ is_active        │       │ frequency        │       │                  │
│  │ is_admin         │       │ created_at       │       │                  │
│  │ created_at       │       │ is_active        │       │                  │
│  │ updated_at       │       │ updated_at       │       │                  │
│  └────────┬─────────┘       └──────────────────┘       │                  │
│           │                                         │                  │
│           │     ┌────────────────────────────────────┼────────────────────┐│
│           │     │                                    │                    ││
│           │     │  ┌─────────────┐    ┌─────────────▼─────────┐          ││
│           │     │  │    habits   │    │     habit_logs        │          ││
│           │     │  ├─────────────┤    ├──────────────────────┤          ││
│           │     │  │ id (PK)     │    │ id (PK)              │          ││
│           │     │  │ user_id(FK) │    │ habit_id (FK)        │◄─────────┘│
│           │     │  └─────────────┘    │ user_id (FK)        │          ││
│           │     │                      │ completed_at         │          ││
│  ┌────────▼────────┐                  │ streak_count         │          ││
│  │ relapse_events  │                  │ notes                │          ││
│  ├─────────────────┤                  │ created_at           │          ││
│  │ id (PK)         │                  └──────────────────────┘          ││
│  │ user_id (FK)    │                                                      ││
│  │ occurred_at      │    ┌─────────────┐    ┌─────────────────────────────┤
│  │ trigger_type     │    │   triggers  │    │   partnerships              │
│  │ severity         │    ├─────────────┤    ├─────────────────────────────┤
│  │ notes            │    │ id (PK)     │    │ id (PK)                    │
│  │ created_at       │    │ user_id(FK) │    │ user1_id (FK)              │
│  └──────────────────┘    │ name        │    │ user2_id (FK)              │
│                           │ category    │    │ status                     │
│  ┌─────────────┐         │ is_active   │    │ created_at                │
│  │   journal   │         │ times_enc...│    │ updated_at                │
│  ├─────────────┤         │ times_over..│    └─────────────┬─────────────┤
│  │ id (PK)     │         └─────────────┘                  │              │
│  │ user_id(FK) │                                       ┌──▼──────────────┐│
│  │ title        │    ┌─────────────┐    ┌────────────┤ shared_goals   ││
│  │ content      │    │ mood_entries│    │            ├────────────────┤│
│  │ created_at   │    ├─────────────┤    │            │ id (PK)        ││
│  │ updated_at   │    │ id (PK)     │    │            │ partnership_id ││
│  └─────────────┘    │ user_id(FK) │────┼────────────│ title          ││
│                      │ mood         │    │            │ description    ││
│  ┌─────────────┐    │ notes       │    │            │ target_date    ││
│  │ achievements│    │ created_at   │    │            │ is_completed   ││
│  ├─────────────┤    └─────────────┘    │            │ completed_at   ││
│  │ id (PK)     │                       │            │ created_at     ││
│  │ name        │    ┌─────────────────┐│            └──────────────────┘│
│  │ description │    │ consistency     ││                                    │
│  │ icon        │    │ builders        ││    ┌─────────────────────────────┤
│  └─────────────┘    ├─────────────────┤    │ shared_goal_progress         │
│                      │ id (PK)         │    ├─────────────────────────────┤
│  ┌─────────────┐    │ user_id (FK)    │    │ id (PK)                    │
│  │ addiction   │    │ name            │    │ shared_goal_id (FK)         │
│  │ killers     │    │ target_days     │    │ user_id (FK)               │
│  ├─────────────┤    │ completed_days  │    │ progress                    │
│  │ id (PK)    │    │ is_active      │    │ notes                       │
│  │ user_id(FK)│    │ created_at      │    │ created_at                  │
│  │ name       │    └─────────────────┘    └─────────────────────────────┘
│  │ technique  │
│  │ created_at │
│  └─────────────┘
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
| is_admin | BOOLEAN | DEFAULT FALSE | Admin flag |
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
| completed_at | TIMESTAMP | NOT NULL, INDEX | **Microsecond precision** completion time |
| streak_count | INTEGER | DEFAULT 0 | Consecutive completion count |
| notes | TEXT | NULLABLE | Optional completion notes |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |

#### 4. relapse_events
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique event identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| occurred_at | TIMESTAMP | NOT NULL, INDEX | **Microsecond precision** event time |
| trigger_type | VARCHAR(50) | NOT NULL | Trigger category |
| severity | INTEGER | NOT NULL, CHECK (1-10) | Severity rating 1-10 |
| notes | TEXT | NULLABLE | Event description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |

#### 5. journal_entries
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique entry identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| title | VARCHAR(200) | NOT NULL | Entry title |
| content | TEXT | NOT NULL | Entry content |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

#### 6. mood_entries
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique entry identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| mood | INTEGER | NOT NULL | Mood rating 1-5 |
| notes | TEXT | NULLABLE | Entry notes |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

#### 7. triggers
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique trigger identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| name | VARCHAR(100) | NOT NULL | Trigger name |
| description | TEXT | NULLABLE | Trigger description |
| category | VARCHAR(50) | NULLABLE | Trigger category |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| times_encountered | INTEGER | DEFAULT 0 | Times encountered |
| times_overcome | INTEGER | DEFAULT 0 | Times overcome |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

#### 8. achievements
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique achievement identifier |
| name | VARCHAR(100) | NOT NULL | Achievement name |
| description | TEXT | NULLABLE | Achievement description |
| icon | VARCHAR(50) | NULLABLE | Icon class |
| requirement_type | VARCHAR(50) | NOT NULL | Type of requirement |
| requirement_value | INTEGER | NOT NULL | Target value |

#### 9. user_achievements
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique record identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| achievement_id | UUID | FK -> achievements(id), NOT NULL | Achievement |
| earned_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When earned |

#### 10. consistency_builders
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique builder identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| name | VARCHAR(100) | NOT NULL | Builder name |
| target_days | INTEGER | NOT NULL | Target days to complete |
| completed_days | INTEGER | DEFAULT 0 | Days completed |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

#### 11. addiction_killers
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique killer identifier |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| name | VARCHAR(100) | NOT NULL | Technique name |
| description | TEXT | NULLABLE | How it works |
| technique | VARCHAR(50) | NOT NULL | CRAFT technique type |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

#### 12. addiction_sessions
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique session identifier |
| killer_id | UUID | FK -> addiction_killers(id), NOT NULL | Related killer |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | Owner user |
| used_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When used |
| effectiveness | INTEGER | NULLABLE | Rating 1-5 |
| notes | TEXT | NULLABLE | Session notes |

#### 13. partnerships
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique partnership identifier |
| user1_id | UUID | FK -> users(id), NOT NULL, INDEX | First user |
| user2_id | UUID | FK -> users(id), NOT NULL, INDEX | Second user |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending/accepted |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

#### 14. shared_goals
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique goal identifier |
| partnership_id | UUID | FK -> partnerships(id), NOT NULL, INDEX | Related partnership |
| title | VARCHAR(200) | NOT NULL | Goal title |
| description | TEXT | NULLABLE | Goal description |
| target_date | DATE | NULLABLE | Target completion date |
| is_completed | BOOLEAN | DEFAULT FALSE | Completion status |
| completed_at | TIMESTAMP | NULLABLE | When completed |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |

#### 15. shared_goal_progress
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique progress identifier |
| shared_goal_id | UUID | FK -> shared_goals(id), NOT NULL, INDEX | Related goal |
| user_id | UUID | FK -> users(id), NOT NULL, INDEX | User who added progress |
| notes | TEXT | NULLABLE | Progress notes |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

### PostgreSQL Compatibility

The application is fully compatible with PostgreSQL. Configuration is handled via environment variables:

```bash
# For PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/sovereign

# For SQLite (development)
DATABASE_URL=sqlite:///sovereign.db
```

The app uses SQLAlchemy ORM which abstracts database differences. All models use UUID primary keys and timezone-aware timestamps, which PostgreSQL handles natively.

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
│                              │    HTMX +   │                                │
│                              │     PWA)    │                                │
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
│  │  │  (Blueprints│    │  (Business  │    │ (SQLAlchemy │              │   │
│  │  │             │    │   Logic)    │    │   Entities) │              │   │
│  │  │ - auth/     │    │ - AuthService│    │ - User      │              │   │
│  │  │ - habits/   │    │ - HabitService│   │ - Habit     │              │   │
│  │  │ - relapse/  │    │ - RelapseService│  │ - HabitLog  │              │   │
│  │  │ - dashboard/│    │ - StreakCalculator│ │ - Partnership│            │   │
│  │  │ - journal/  │    │ - ExportService │   │ - SharedGoal │             │   │
│  │  │ - mood/     │    │ - MoodService   │   └─────────────┘              │   │
│  │  │ - trigger/  │    └─────────────┘                                    │   │
│  │  │ - leaderboard/                                                     │   │
│  │  │ - partner/                                                        │   │
│  │  └─────────────┘         │                    │                        │   │
│  │         │                 └────────────────────┼────────────────────┘   │   │
│  │         │                                   │                          │   │
│  │         │                                   ▼                          │   │
│  │  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  │                    EXTENSIONS                               │   │   │
│  │  │  │  - SQLAlchemy (db)      - Flask-Login (auth)               │   │   │
│  │  │  │  - Flask-WTF (CSRF)     - Flask-Migrate (migrations)       │   │   │
│  │  │  │  - Flask-Bcrypt (hash)  - Flask-DebugToolbar (dev)        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                       │   │
│  └──────────────────────────────┼───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    POSTGRESQL DATABASE                               │  │
│  │              (Tables, Indexes, Constraints)                         │  │
│  │                                                                       │  │
│  │   - UUID primary keys                                                │  │
│  │   - Timezone-aware timestamps                                        │  │
│  │   - Foreign key constraints                                          │  │
│  │   - Indexes for performance                                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DIRECTORY STRUCTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  app/                              # Application Package                     │
│  ├── __init__.py                 # App Factory + Extensions                │
│  ├── config.py                   # Configuration Classes                    │
│  ├── models/                     # SQLAlchemy Models                        │
│  │   ├── __init__.py                                                  │
│  │   ├── user.py                    # User model                           │
│  │   ├── habit.py                   # Habit model                          │
│  │   ├── habit_log.py               # Habit completion logs               │
│  │   ├── relapse_event.py           # Relapse tracking                    │
│  │   ├── journal_entry.py           # Journal entries                     │
│  │   ├── mood_entry.py              # Mood tracking                       │
│  │   ├── trigger.py                 # Trigger management                  │
│  │   ├── achievement.py              # Achievements system                 │
│  │   ├── consistency_builder.py      # Consistency tracking                │
│  │   ├── addiction_killer.py        # Coping techniques                   │
│  │   └── partnership.py              # Partner goals                       │
│  ├── blueprints/                  # Flask Blueprints                       │
│  │   ├── __init__.py                                                   │
│  │   ├── auth.py                     # Authentication                      │
│  │   ├── habits.py                  # Habit management                    │
│  │   ├── relapse.py                 # Relapse tracking                    │
│  │   ├── dashboard.py               # Main dashboard                       │
│  │   ├── journal.py                 # Journal entries                     │
│  │   ├── mood.py                    # Mood tracking                       │
│  │   ├── trigger.py                 # Trigger management                   │
│  │   ├── achievement.py             # Achievements                         │
│  │   ├── consistency.py             # Consistency builders                 │
│  │   ├── addiction.py               # Addiction killers                   │
│  │   ├── leaderboard.py             # User rankings                        │
│  │   ├── partner.py                 # Partner goals                        │
│  │   ├── export_calendar.py         # Export + Calendar                   │
│  │   ├── admin.py                   # Admin panel                         │
│  │   └── help.py                    # Feature guide                       │
│  ├── services/                    # Business Logic                         │
│  │   ├── __init__.py                                                   │
│  │   ├── auth_service.py                                               │
│  │   ├── habit_service.py                                              │
│  │   ├── relapse_service.py                                            │
│  │   ├── streak_service.py                                             │
│  │   ├── export_service.py                                              │
│  │   ├── mood_service.py                                                │
│  │   └── ...                                                            │
│  ├── templates/                   # Jinja2 Templates                       │
│  │   ├── base.html                 # Base template + PWA                  │
│  │   ├── auth/                                                         │
│  │   ├── habits/                                                        │
│  │   ├── relapse/                                                      │
│  │   ├── dashboard/                                                    │
│  │   ├── journal/                                                      │
│  │   ├── mood/                                                         │
│  │   ├── trigger/                                                      │
│  │   ├── achievement/                                                  │
│  │   ├── consistency/                                                │
│  │   ├── addiction/                                                   │
│  │   ├── leaderboard/                                                 │
│  │   ├── partner/                                                     │
│  │   ├── calendar/                                                    │
│  │   ├── export/                                                      │
│  │   ├── admin/                                                       │
│  │   └── help/                                                        │
│  ├── static/                      # CSS/JS/Images + PWA                   │
│  │   ├── sw.js                 # Service worker                          │
│  │   ├── manifest.json         # PWA manifest                            │
│  │   └── icons/                # PWA icons                                │
│  └── utils/                      # Utility Functions                       │
│      ├── __init__.py                                                   │
│      └── errors.py                                                      │
│                                                                             │
│  migrations/                    # Flask-Migrate                            │
│  tests/                         # Pytest Test Suite                        │
│  .env                           # Environment Variables                     │
│  requirements.txt               # Python Dependencies                      │
│  pytest.ini                     # Pytest Configuration                      │
│  run.py                         # Application Entry Point                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Features

### Core Features
- **Habit Tracking** - Create and track daily/weekly/monthly habits
- **Streak System** - Automatic streak calculation with best streak tracking
- **Relapse Tracking** - Log relapse events with severity and triggers
- **Journal** - Personal diary with entries
- **Mood Tracker** - Daily mood logging with trend analysis

### Advanced Features
- **Triggers** - Identify and track personal triggers
- **Achievements** - Gamification with badges and milestones
- **Consistency Builder** - Focus on one habit at a time
- **Addiction Killer** - CRAFT technique library for coping
- **Calendar View** - Visual habit calendar
- **Data Export** - CSV export for all data

### Social Features
- **Leaderboard** - Compete with other users (completions, streaks, sobriety)
- **Partner Goals** - Set shared goals with a partner

### Technical Features
- **PWA Support** - Installable as native app
- **Mobile Responsive** - Works on all devices
- **Dark Mode** - Theme toggle
- **HTMX** - Fast, SPA-like experience without JavaScript
- **PostgreSQL Ready** - Production-ready database support

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask |
| Database | PostgreSQL / SQLite (dev) |
| ORM | SQLAlchemy |
| Migrations | Flask-Migrate |
| Authentication | Flask-Login + Flask-Bcrypt |
| Forms | Flask-WTF |
| Frontend | Bootstrap 5 + HTMX |
| PWA | Service Worker + Manifest |
| Testing | Pytest |
| Deploy | Gunicorn |

---

## Security

1. **CSRF Protection**
   - Flask-WTF form tokens on all POST forms
   - HTMX: X-CSRFToken header on AJAX requests

2. **Authentication**
   - Flask-Login session management
   - Bcrypt password hashing
   - Login required decorators

3. **Global Error Handling**
   - Custom error handlers (400, 404, 500)
   - Structured error logging

4. **Input Validation**
   - WTForms for form validation
   - SQLAlchemy parameterized queries (ORM prevents SQLi)

---

*Document Version: 2.0*
*Project: Sovereign - Addiction Recovery Application*
