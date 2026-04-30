# Admin routes
from flask import Blueprint, request, jsonify
from flask_login import current_user

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/complaints/', methods=['GET'])
def get_complaints():
    pass


@admin_bp.route('/complaints/<int:id>/status', methods=['PUT'])
def update_status(id):
    pass


@admin_bp.route('/complaints/<int:id>/reply', methods=['PUT'])
def reply_complaint(id):
    pass
