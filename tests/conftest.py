import pytest
from app import create_app, db
from app.models import User, Habit, HabitLog, RelapseEvent


@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    from app.services import AuthService
    user = AuthService.create_user(
        email='test@example.com',
        username='testuser',
        password='password123'
    )
    return user


@pytest.fixture
def test_admin(app):
    from app.services import AuthService
    user = AuthService.create_user(
        email='admin@example.com',
        username='admin',
        password='adminpass123'
    )
    user.is_admin = True
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def test_habit(app, test_user):
    from app.services import HabitService
    habit = HabitService.create_habit(
        user_id=test_user.id,
        name='Exercise',
        description='Daily exercise',
        frequency='daily'
    )
    return habit
