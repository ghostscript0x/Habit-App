# Sovereign - Addiction Recovery Tracker

A high-reliability Flask application for tracking addiction recovery progress, habits, and relapse events.

## Features

- **User Authentication** - Secure login/registration with bcrypt password hashing
- **Habit Tracking** - Create and track daily/weekly/monthly habits with streak counting
- **Relapse Event Logging** - Track relapse events with triggers, severity, and notes
- **Streak System** - Automatic streak calculation with millisecond precision timestamps
- **Admin Dashboard** - Platform owner can manage users and view analytics
- **Real-time Updates** - HTMX for seamless UI updates without page refreshes
- **Responsive Design** - Bootstrap 5 mobile-responsive interface

## Tech Stack

- **Backend**: Flask 3.x, Python 3.12
- **Database**: SQLite (dev) / PostgreSQL (prod) with SQLAlchemy
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Forms**: Flask-WTF with CSRF protection
- **Frontend**: Bootstrap 5, HTMX
- **Testing**: Pytest

## Installation

```bash
# Clone and setup
git clone <repo-url>
cd sovereign
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env - DATABASE_URL=sqlite:///sovereign.db

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
python -c "from app import create_app, db; from app.services import AuthService; app = create_app(); 
with app.app_context(): 
    u = AuthService.create_user('admin@example.com', 'admin', 'adminpass123')
    u.is_admin = True
    db.session.commit()"

# Run the app
python run.py
```

## Usage

1. Register a new account at `/auth/register`
2. Login at `/auth/login`
3. Create habits at `/habits/create`
4. Log relapse events at `/relapse/create`
5. View your dashboard at `/dashboard`
6. Admin panel at `/admin` (requires admin account)

## Project Structure

```
sovereign/
├── app/
│   ├── blueprints/       # Route handlers
│   ├── models/           # SQLAlchemy models
│   ├── services/        # Business logic
│   ├── templates/       # Jinja2 templates
│   └── utils/           # Utilities
├── migrations/          # Flask-Migrate
├── tests/               # Pytest tests
├── run.py               # Entry point
└── requirements.txt     # Dependencies
```

## Testing

```bash
pytest
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment | development |
| `SECRET_KEY` | Flask secret key | dev-secret-key |
| `DATABASE_URL` | Database connection | sqlite:///sovereign.db |

## License

MIT
