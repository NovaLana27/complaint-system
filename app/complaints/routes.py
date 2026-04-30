from flask import Blueprint, request, jsonify
from app import db
from app.models import Complaint, User
from flask_login import login_required, current_user

bp = Blueprint('complaints', __name__, url_prefix='/complaints')

@bp.route('/', methods=['GET'])
@login_required
def get_complaints():
    complaints = Complaint.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'status': c.status,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in complaints]), 200

@bp.route('/', methods=['POST'])
@login_required
def create_complaint():
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('description') or not data.get('category'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    complaint = Complaint(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        user_id=current_user.id
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    return jsonify({
        'message': 'Complaint created successfully',
        'complaint_id': complaint.id
    }), 201

@bp.route('/<int:complaint_id>', methods=['GET'])
@login_required
def get_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': complaint.id,
        'title': complaint.title,
        'description': complaint.description,
        'category': complaint.category,
        'status': complaint.status,
        'created_at': complaint.created_at.isoformat() if complaint.created_at else None
    }), 200

@bp.route('/<int:complaint_id>', methods=['PUT'])
@login_required
def update_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if data.get('title'):
        complaint.title = data['title']
    if data.get('description'):
        complaint.description = data['description']
    if data.get('category'):
        complaint.category = data['category']
    
    db.session.commit()
    
    return jsonify({'message': 'Complaint updated successfully'}), 200

@bp.route('/<int:complaint_id>', methods=['DELETE'])
@login_required
def delete_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if complaint.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(complaint)
    db.session.commit()
    
    return jsonify({'message': 'Complaint deleted successfully'}), 200