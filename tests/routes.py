# Admin routes
from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import db
from app.models import Complaint, User
from app.auth.routes import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/complaints/', methods=['GET'])
@admin_required
def get_complaints():
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Complaint.query.filter_by(department_id=current_user.department_id)

    if status:
        query = query.filter_by(status=status)

    complaints = query.paginate(page=page, per_page=per_page, error_out=False)

    result = []
    for complaint in complaints.items:
        student = User.query.get(complaint.user_id)
        result.append({
            'id': complaint.id,
            'title': complaint.title,
            'description': complaint.description,
            'status': complaint.status,
            'student_username': student.username if student else None,
            'created_at': complaint.created_at,
            'updated_at': complaint.updated_at
        })

    return jsonify({
        'message': 'Complaints retrieved successfully',
        'data': result,
        'page': complaints.page,
        'total_pages': complaints.pages,
        'total_complaints': complaints.total
    }), 200


@bp.route('/complaints/<int:id>/status', methods=['PUT'])
@admin_required
def update_status(id):
    complaint = Complaint.query.get(id)

    if not complaint:
        return jsonify({'error': 'Not Found', 'message': 'Complaint not found'}), 404

    if complaint.department_id != current_user.department_id:
        return jsonify({'error': 'Forbidden', 'message': 'You can only update complaints in your department'}), 403

    data = request.get_json()
    new_status = data.get('status')

    valid_statuses = ['Pending', 'In Review', 'Resolved']
    if new_status not in valid_statuses:
        return jsonify({'error': 'Bad Request', 'message': 'Status must be Pending, In Review, or Resolved'}), 400

    complaint.status = new_status

    try:
        db.session.commit()
        return jsonify({
            'message': 'Status updated successfully',
            'data': {
                'id': complaint.id,
                'title': complaint.title,
                'status': complaint.status,
                'updated_at': complaint.updated_at
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server Error', 'message': 'Database error occurred'}), 500


@bp.route('/complaints/<int:id>/reply', methods=['PUT'])
@admin_required
def reply_complaint(id):
    complaint = Complaint.query.get(id)

    if not complaint:
        return jsonify({'error': 'Not Found', 'message': 'Complaint not found'}), 404

    if complaint.department_id != current_user.department_id:
        return jsonify({'error': 'Forbidden', 'message': 'You can only reply to complaints in your department'}), 403

    data = request.get_json()
    reply = data.get('reply')

    if not reply:
        return jsonify({'error': 'Bad Request', 'message': 'Reply cannot be empty'}), 400

    complaint.admin_reply = reply

    try:
        db.session.commit()
        return jsonify({
            'message': 'Reply added successfully',
            'data': {
                'id': complaint.id,
                'title': complaint.title,
                'status': complaint.status,
                'admin_reply': complaint.admin_reply,
                'updated_at': complaint.updated_at
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server Error', 'message': 'Database error occurred'}), 500
