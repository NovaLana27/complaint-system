from flask import Blueprint, request, jsonify
from app import db
from app.models import Complaint, User
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/complaints', methods=['GET'])
@login_required
def get_all_complaints():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    complaints = Complaint.query.all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'status': c.status,
        'user_id': c.user_id,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in complaints]), 200

@bp.route('/complaints/<int:complaint_id>', methods=['PUT'])
@login_required
def update_complaint_status(complaint_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    if data.get('status'):
        complaint.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': 'Complaint status updated'}), 200

@bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role
    } for u in users]), 200

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting other admins
    if user.role == 'admin':
        return jsonify({'error': 'Cannot delete admin users'}), 403
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200