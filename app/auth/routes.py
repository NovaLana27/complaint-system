from flask import Blueprint, request, jsonify, session
from app import db, login_manager
from app.models import User, Department
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    """Decorator to ensure only admins can access specific routes."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Forbidden', 'message': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'No input data provided'}), 400

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Bad Request', 'message': 'Missing required fields (username, email, password)'}), 400
    
    email = data.get('email').lower().strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'error': 'Bad Request', 'message': 'Invalid email format'}), 400

    role = data.get('role', 'student').lower()
    if role not in ['student', 'admin']:
        return jsonify({'error': 'Bad Request', 'message': 'Role must be student or admin'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Conflict', 'message': 'Email already registered'}), 409
  
    department_id = None
    if role == 'admin':
        department_id = data.get('department_id')
        if not department_id:
            return jsonify({'error': 'Bad Request', 'message': 'department_id is required for admin registration'}), 400
        if not Department.query.get(department_id):

    new_user = User(
        username=data['username'].strip(),
        email=email,
        role=role,
        department_id=department_id
    )
    new_user.set_password(data['password'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server Error', 'message': 'Database error occurred'}), 500

@bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'message': 'Already logged in', 'role': current_user.role}), 200

    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Bad Request', 'message': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email'].lower().strip()).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid email or password'}), 401
    
    login_user(user)
    session.modified = True # Security: Session fixation prevention
    
    return jsonify({
        'message': 'Login successful',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'department_id': user.department_id
        }
    }), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'message': 'Profile retrieved',
        'data': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'department_id': current_user.department_id
        }
    }), 200
