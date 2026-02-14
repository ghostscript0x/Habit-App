import pytest


class TestAuthBlueprint:
    
    def test_login_page_loads(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_register_page_loads(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_success(self, client, test_user):
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_failure(self, client, test_user):
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_register_success(self, client):
        response = client.post('/auth/register', data={
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_logout(self, authenticated_client):
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


class TestHabitsBlueprint:
    
    def test_habits_index_requires_login(self, client):
        response = client.get('/habits/')
        assert response.status_code == 302
    
    def test_habits_index_loads(self, authenticated_client):
        response = authenticated_client.get('/habits/')
        assert response.status_code == 200
    
    def test_create_habit(self, authenticated_client):
        response = authenticated_client.post('/habits/create', data={
            'name': 'Test Habit',
            'description': 'Test Description',
            'frequency': 'daily'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Test Habit' in response.data
    
    def test_complete_habit(self, authenticated_client, test_habit):
        response = authenticated_client.post(f'/habits/{test_habit.id}/complete')
        assert response.status_code == 302


class TestRelapseBlueprint:
    
    def test_relapse_index_requires_login(self, client):
        response = client.get('/relapse/')
        assert response.status_code == 302
    
    def test_relapse_index_loads(self, authenticated_client):
        response = authenticated_client.get('/relapse/')
        assert response.status_code == 200
    
    def test_create_relapse(self, authenticated_client):
        response = authenticated_client.post('/relapse/create', data={
            'trigger_type': 'stress',
            'severity': '5',
            'notes': 'Test note'
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestDashboardBlueprint:
    
    def test_dashboard_requires_login(self, client):
        response = client.get('/dashboard')
        assert response.status_code == 302
    
    def test_dashboard_loads(self, authenticated_client):
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data


class TestAdminBlueprint:
    
    def test_admin_requires_admin(self, authenticated_client):
        response = authenticated_client.get('/admin/')
        assert response.status_code == 302
    
    def test_admin_loads_for_admin(self, app, client, test_admin):
        client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })
        
        response = client.get('/admin/')
        assert response.status_code == 200
