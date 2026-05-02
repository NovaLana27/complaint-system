import pytest
from app import create_app, db
from app.models import User, Complaint, Department


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()

        # Seed a department
        department = Department(name='Hostel')
        db.session.add(department)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# Test 1 - Student Registration
def test_student_registration(client):
    response = client.post('/auth/register', json={
        'username': 'teststudent',
        'email': 'teststudent@gmail.com',
        'password': 'password123',
        'role': 'student'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'user_id' in data


# Test 2 - Student Login
def test_student_login(client):
    # First register
    client.post('/auth/register', json={
        'username': 'teststudent',
        'email': 'teststudent@gmail.com',
        'password': 'password123',
        'role': 'student'
    })

    # Then login
    response = client.post('/auth/login', json={
        'email': 'teststudent@gmail.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['role'] == 'student'


# Test 3 - Submit a Complaint
def test_submit_complaint(client, app):
    # Register and login as student
    client.post('/auth/register', json={
        'username': 'teststudent',
        'email': 'teststudent@gmail.com',
        'password': 'password123',
        'role': 'student'
    })
    client.post('/auth/login', json={
        'email': 'teststudent@gmail.com',
        'password': 'password123'
    })

    # Get department id
    with app.app_context():
        department = Department.query.filter_by(name='Hostel').first()
        dept_id = department.id

    # Submit complaint
    response = client.post('/complaints/', json={
        'title': 'No water in hostel',
        'description': 'Water has been out for 3 days',
        'department_id': dept_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['data']['status'] == 'pending'


# Test 4 - Block Edit After Status Change
def test_block_edit_after_status_change(client, app):
    # Register and login as student
    client.post('/auth/register', json={
        'username': 'teststudent',
        'email': 'teststudent@gmail.com',
        'password': 'password123',
        'role': 'student'
    })
    client.post('/auth/login', json={
        'email': 'teststudent@gmail.com',
        'password': 'password123'
    })

    # Get department id
    with app.app_context():
        department = Department.query.filter_by(name='Hostel').first()
        dept_id = department.id

    # Submit complaint
    response = client.post('/complaints/', json={
        'title': 'No water in hostel',
        'description': 'Water has been out for 3 days',
        'department_id': dept_id
    })
    complaint_id = response.get_json()['data']['id']

    # Manually change status to In Review
    with app.app_context():
        complaint = Complaint.query.get(complaint_id)
        complaint.status = 'In Review'
        db.session.commit()

    # Try to edit complaint
    response = client.put(f'/complaints/{complaint_id}', json={
        'title': 'Updated title'
    })
    assert response.status_code == 403


# Test 5 - Admin Status Update
def test_admin_status_update(client, app):
    # Get department id
    with app.app_context():
        department = Department.query.filter_by(name='Hostel').first()
        dept_id = department.id

    # Register and login as admin
    client.post('/auth/register', json={
        'username': 'testadmin',
        'email': 'testadmin@gmail.com',
        'password': 'password123',
        'role': 'admin',
        'department_id': dept_id
    })
    client.post('/auth/login', json={
        'email': 'testadmin@gmail.com',
        'password': 'password123'
    })

    # Create a complaint directly in database
    with app.app_context():
        student = User(
            username='student1',
            email='student1@gmail.com',
            role='student'
        )
        student.set_password('password123')
        db.session.add(student)
        db.session.commit()

        complaint = Complaint(
            title='No water',
            description='Water is out',
            category='Hostel',
            status='pending',
            user_id=student.id,
            department_id=dept_id
        )
        db.session.add(complaint)
        db.session.commit()
        complaint_id = complaint.id

    # Admin updates status
    response = client.put(f'/admin/complaints/{complaint_id}/status', json={
        'status': 'Resolved'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['status'] == 'Resolved'
