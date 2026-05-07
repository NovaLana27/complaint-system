from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app import db
from app.models import Complaint, User
from flask_login import login_required, current_user
from datetime import datetime

bp = Blueprint('complaints', __name__, url_prefix='/complaints')

# Helper function to send email notifications
def send_notification_email(to_email, subject, message):
    """Send notification email. Extend this to integrate with actual email service."""
    try:
        # This is a placeholder - in production, use Flask-Mail or similar
        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Message: {message}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

# Valid complaint categories for university system
VALID_CATEGORIES = [
    'Academic',
    'Facilities',
    'Administration',
    'Staff Conduct',
    'Student Services',
    'Safety/Security',
    'Harassment/Bullying',
    'Food/Cafeteria',
    'Library Services',
    'Other'
]

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of valid complaint categories"""
    return jsonify({'categories': VALID_CATEGORIES}), 200

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')

        if not title or not description or not category:
            flash('Please complete all fields before submitting.', 'error')
            return redirect(url_for('complaints.user_dashboard'))

        if category not in VALID_CATEGORIES:
            flash('Please select a valid category.', 'error')
            return redirect(url_for('complaints.user_dashboard'))

        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            user_id=current_user.id
        )
        db.session.add(complaint)
        db.session.commit()
        flash('Complaint submitted successfully.', 'success')
        return redirect(url_for('complaints.user_dashboard'))

    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    return render_template('complaints.html', categories=VALID_CATEGORIES, complaints=complaints)

@bp.route('/', methods=['GET'])
@login_required
def get_complaints():
    # Filtering parameters
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Complaint.query.filter_by(user_id=current_user.id)
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    
    complaints = query.all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'status': c.status,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None
    } for c in complaints]), 200

@bp.route('/', methods=['POST'])
@login_required
def create_complaint():
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('description') or not data.get('category'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate category
    if data.get('category') not in VALID_CATEGORIES:
        return jsonify({
            'error': 'Invalid category',
            'valid_categories': VALID_CATEGORIES
        }), 400
    
    complaint = Complaint(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        user_id=current_user.id
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    # Send notification email to admins
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        send_notification_email(
            admin.email,
            f"New Complaint Submitted - {data['category']}",
            f"A new complaint has been submitted by {current_user.username}:\n\n"
            f"Title: {data['title']}\n"
            f"Category: {data['category']}\n"
            f"Description: {data['description']}"
        )
    
    return jsonify({
        'message': 'Complaint created successfully',
        'complaint_id': complaint.id,
        'status': complaint.status
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