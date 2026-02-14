# Sovereign - Recovery Tracker

<p align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap" alt="Bootstrap">
  <img src="https://img.shields.io/badge/PWA-5A0FC0?style=for-the-badge" alt="PWA">
</p>

A powerful, privacy-focused addiction recovery tracker built with Flask. Track your habits, monitor progress, stay accountable, and achieve your recovery goals.

## ✨ Features

### Core Tracking
- **Habit Tracking** - Create daily/weekly/monthly habits with automatic streak counting
- **Relapse Logging** - Track events with triggers, severity ratings, and notes
- **Mood Tracking** - Daily mood entries with trend analysis
- **Journal** - Personal diary for reflections and thoughts
- **Trigger Management** - Identify and track personal triggers

### Advanced Features
- **Partner Goals** - Set shared recovery goals with an accountability partner
- **Leaderboard** - Compete with other users (completions, streaks, sobriety days)
- **Achievements** - Gamified badges and milestones
- **Consistency Builder** - Focus on one habit at a time
- **Addiction Killer** - CRAFT technique library for cravings
- **Calendar View** - Visual habit calendar
- **Data Export** - Download all your data as CSV

### Technical
- **PWA Support** - Install as a native app on any device
- **Mobile Responsive** - Works perfectly on phones, tablets, and desktops
- **Dark Mode** - Easy on the eyes
- **HTMX** - Fast, seamless updates without page reloads
- **PostgreSQL Ready** - Production-grade database support

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (optional, SQLite for development)

### Installation

```bash
# Clone the repository
git clone https://github.com/ghostscript0x/Habit-App.git
cd habit-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env - DATABASE_URL=sqlite:///sovereign.db (or your PostgreSQL URL)

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
python -c "from app import create_app, db; from app.models import User; app = create_app(); 
with app.app_context(): 
    u = User(email='admin@example.com', username='admin', password_hash='\$2b\$12\$hashedpassword')
    u.is_admin = True
    db.session.add(u)
    db.session.commit()"

# Run the app
python run.py
```

Visit `http://localhost:5000` to access the application.

## 📖 Documentation

### User Guide

#### Getting Started
1. Register an account at `/auth/register`
2. Login at `/auth/login`
3. Create your first habit at `/habits/create`
4. Start tracking daily!

#### Key Pages
| Route | Description |
|-------|-------------|
| `/dashboard` | Overview of your progress |
| `/habits` | Manage your habits |
| `/relapse` | Log and track relapse events |
| `/mood` | Track daily mood |
| `/journal` | Write journal entries |
| `/partner` | Manage partner goals |
| `/leaderboard` | See rankings |

### Configuration

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment | `development` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `DATABASE_URL` | Database connection | `sqlite:///sovereign.db` |

#### PostgreSQL Setup

```bash
# Create database
createdb sovereign

# Set environment variable
export DATABASE_URL="postgresql://username:password@localhost/sovereign"
```

## 🛠️ Development

### Project Structure

```
app/
├── blueprints/       # Route handlers (auth, habits, relapse, etc.)
├── models/          # SQLAlchemy database models
├── services/        # Business logic layer
├── templates/       # Jinja2 HTML templates
├── static/          # CSS, JS, PWA assets
│   ├── sw.js        # Service worker
│   ├── manifest.json # PWA manifest
│   └── icons/       # App icons
└── utils/           # Utility functions

migrations/          # Database migrations
tests/               # Test suite
```

### Running Tests

```bash
pytest
```

### Adding Features

1. Create model in `app/models/`
2. Create service in `app/services/`
3. Create blueprint in `app/blueprints/`
4. Create templates in `app/templates/`
5. Run migration: `flask db migrate -m "Add feature"`
6. Update ARCHITECTURE.md

## 🔒 Security

- CSRF protection via Flask-WTF
- Bcrypt password hashing
- SQLAlchemy ORM (prevents SQL injection)
- Session-based authentication
- Input validation with WTForms

## 📱 PWA

The app is installable as a native application:

1. Visit the app in a modern browser
2. Look for the install icon in the address bar
3. Click to install as a standalone app
4. Works offline with cached data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- UI by [Bootstrap](https://getbootstrap.com/)
- Interactivity by [HTMX](https://htmx.org/)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com/)

---

<p align="center">Made with 💚 for recovery</p>
