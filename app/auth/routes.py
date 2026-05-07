from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app import db, login_manager
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json() if request.is_json else request.form
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        if request.is_json:
            return jsonify({'error': 'Missing required fields'}), 400
        flash('Missing required fields.', 'error')
        return redirect(url_for('auth.register'))
    
    if User.query.filter_by(email=data['email']).first():
        if request.is_json:
            return jsonify({'error': 'Email already registered'}), 400
        flash('Email already registered.', 'error')
        return redirect(url_for('auth.register'))
    
    if User.query.filter_by(username=data['username']).first():
        if request.is_json:
            return jsonify({'error': 'Username already taken'}), 400
        flash('Username already taken.', 'error')
        return redirect(url_for('auth.register'))
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'student')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()

    if request.is_json:
        return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201

    flash('Account created successfully. Please login.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json() if request.is_json else request.form
    
    if not data or not data.get('email') or not data.get('password'):
        if request.is_json:
            return jsonify({'error': 'Missing email or password'}), 400
        flash('Missing email or password.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        if request.is_json:
            return jsonify({'error': 'Invalid email or password'}), 401
        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.login'))
    
    login_user(user)
    
    if request.is_json:
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }), 200

    return redirect(url_for('complaints.user_dashboard'))

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    if request.is_json:
        return jsonify({'message': 'Logged out successfully'}), 200
    return redirect(url_for('auth.login'))

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    }), 200