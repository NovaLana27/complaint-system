from flask import Blueprint, request, jsonify
from app import db
from app.models import Complaint, User
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
import csv
from io import StringIO

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Valid statuses for complaints
VALID_STATUSES = ['pending', 'in_progress', 'resolved', 'rejected', 'closed']

# Helper function to send email notifications
def send_notification_email(to_email, subject, message):
    """Send notification email. Extend this to integrate with actual email service."""
    try:
        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Message: {message}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

@bp.route('/complaints', methods=['GET'])
@login_required
def get_all_complaints():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Filtering parameters
    category = request.args.get('category')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Complaint.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(Complaint.created_at >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(Complaint.created_at <= end)
    
    complaints = query.all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'category': c.category,
        'status': c.status,
        'user_id': c.user_id,
        'username': c.author.username,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None
    } for c in complaints]), 200

@bp.route('/complaints/<int:complaint_id>', methods=['PUT'])
@login_required
def update_complaint_status(complaint_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    complaint = Complaint.query.get_or_404(complaint_id)
    data = request.get_json()
    
    if data.get('status'):
        if data['status'] not in VALID_STATUSES:
            return jsonify({
                'error': 'Invalid status',
                'valid_statuses': VALID_STATUSES
            }), 400
        
        old_status = complaint.status
        complaint.status = data['status']
        db.session.commit()
        
        # Send notification email to user
        user = complaint.author
        send_notification_email(
            user.email,
            f"Complaint Status Update - {complaint.title}",
            f"Your complaint has been updated:\n\n"
            f"Title: {complaint.title}\n"
            f"Previous Status: {old_status}\n"
            f"New Status: {complaint.status}\n"
            f"Category: {complaint.category}\n\n"
            f"Admin Comment: {data.get('comment', 'N/A')}"
        )
        
        return jsonify({
            'message': 'Complaint status updated',
            'complaint_id': complaint.id,
            'new_status': complaint.status
        }), 200
    
    return jsonify({'error': 'No status provided'}), 400


@bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    total_complaints = Complaint.query.count()
    
    # Complaints by status
    status_stats = db.session.query(
        Complaint.status,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.status).all()
    
    # Complaints by category
    category_stats = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).group_by(Complaint.category).all()
    
    return jsonify({
        'total_complaints': total_complaints,
        'by_status': {status: count for status, count in status_stats},
        'by_category': {category: count for category, count in category_stats},
        'valid_statuses': VALID_STATUSES
    }), 200

@bp.route('/export/csv', methods=['GET'])
@login_required
def export_csv():
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Filtering parameters (same as GET /complaints)
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Complaint.query
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    
    complaints = query.all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Description', 'Category', 'Status', 'User', 'Created At'])
    
    for c in complaints:
        writer.writerow([
            c.id,
            c.title,
            c.description,
            c.category,
            c.status,
            c.author.username,
            c.created_at.isoformat() if c.created_at else ''
        ])
    
    return output.getvalue(), 200, {
        'Content-Disposition': 'attachment; filename=complaints.csv',
        'Content-Type': 'text/csv'
    }

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