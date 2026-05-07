# Complaint Management System

A Flask-based web application for managing user complaints in an educational institution. The system allows students to submit complaints, track their status, and provides administrators with tools to manage, analyze, and respond to complaints.

## Features

### User Features
- **User Registration & Authentication**: Secure account creation and login system
- **Complaint Submission**: Submit complaints with title, description, and category
- **Complaint Tracking**: View all submitted complaints and their current status
- **Complaint Management**: Edit or delete own complaints
- **Dashboard**: User-friendly interface to manage complaints

### Admin Features
- **Complaint Management**: View all complaints across the system
- **Status Updates**: Change complaint status (pending, in_progress, resolved, rejected, closed)
- **Advanced Filtering**: Filter complaints by category, status, and date range
- **Analytics**: View statistics on complaints by status and category
- **CSV Export**: Export complaints data for external analysis
- **User Management**: View all users and remove non-admin users
- **Email Notifications**: Automatic notifications on complaint updates (placeholder implementation)

### Complaint Categories
- Academic
- Facilities
- Administration
- Staff Conduct
- Student Services
- Safety/Security
- Harassment/Bullying
- Food/Cafeteria
- Library Services
- Other

## Tech Stack

- **Backend**: Flask 3.1.3
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Form Handling**: Flask WTF
- **Testing**: pytest

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone/Navigate to the project directory**
   ```bash
   cd Project-complaint-system-1
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Start the Flask Server
```bash
python run.py
```

The application will start at `http://localhost:5000`

**Development Features**:
- Auto-reload enabled (changes apply without restarting)
- Debug mode enabled for detailed error messages

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models.py                # Database models (User, Complaint)
│   ├── config.py                # Configuration settings
│   ├── auth/                    # Authentication routes
│   │   ├── __init__.py
│   │   └── routes.py            # Login, register, logout endpoints
│   ├── complaints/              # Complaint management routes
│   │   ├── __init__.py
│   │   └── routes.py            # Complaint CRUD operations
│   ├── admin/                   # Admin-only routes
│   │   ├── __init__.py
│   │   └── routes.py            # Admin management endpoints
│   └── main/                    # Main/home routes
│       ├── __init__.py
│       └── routes.py
├── instance/
│   └── app.db                   # SQLite database (auto-created)
├── templates/                   # HTML templates
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Database Models

### User Model
```python
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)
- role (String) - 'student' or 'admin'
- complaints (Relationship) - User's submitted complaints
```

### Complaint Model
```python
- id (Integer, Primary Key)
- title (String)
- description (Text)
- category (String) - One of the valid categories
- status (String) - Default: 'pending'
- user_id (Foreign Key) - Links to User
- created_at (DateTime) - Auto-timestamp
- updated_at (DateTime) - Auto-timestamp
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/auth/register` | Register new user |
| GET/POST | `/auth/login` | User login |
| GET/POST | `/auth/logout` | User logout |
| GET | `/auth/me` | Get current user info |

### Complaint Endpoints (User)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/complaints/categories` | Get valid complaint categories |
| GET/POST | `/complaints/dashboard` | User dashboard (HTML) |
| GET | `/complaints/` | Get user's complaints (JSON) |
| POST | `/complaints/` | Create new complaint |
| GET | `/complaints/<id>` | Get specific complaint |
| PUT | `/complaints/<id>` | Update complaint |
| DELETE | `/complaints/<id>` | Delete complaint |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/complaints` | Get all complaints (admin only) |
| PUT | `/admin/complaints/<id>` | Update complaint status (admin only) |
| GET | `/admin/analytics` | Get complaint analytics (admin only) |
| GET | `/admin/export/csv` | Export complaints as CSV (admin only) |
| GET | `/admin/users` | Get all users (admin only) |
| DELETE | `/admin/users/<id>` | Delete user (admin only) |

## User Roles

### Student
- Submit complaints
- View and manage own complaints
- View complaint status
- Edit/delete own submissions

### Admin
- View all complaints system-wide
- Update complaint status
- Export data
- Manage users
- View analytics and statistics

## Testing

Run tests with pytest:
```bash
pytest
```

## Configuration

Key configuration settings in `app/__init__.py`:
- `SECRET_KEY`: Session encryption key (change in production)
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `SQLALCHEMY_TRACK_MODIFICATIONS`: SQLAlchemy modification tracking

## Email Notifications

The system includes a placeholder for email notifications. Currently, notifications are logged to console. To integrate with an actual email service:
1. Install Flask-Mail: `pip install Flask-Mail`
2. Update `send_notification_email()` functions in `complaints/routes.py` and `admin/routes.py`

## Security Notes

- Passwords are hashed using werkzeug's security utilities
- Session management via Flask-Login
- CSRF protection available (add to forms as needed)
- Change `SECRET_KEY` in production
- Use environment variables for sensitive configuration

## Future Enhancements

- Email service integration
- Attachment support for complaints
- Complaint comment/reply system
- Advanced search and filtering UI
- Automated status workflows
- User profile customization
- Complaint escalation levels
- File upload support

## Troubleshooting

### Database Issues
If you encounter database errors, delete `instance/app.db` and restart the app to recreate it.

### Port Already in Use
If port 5000 is occupied:
```bash
python run.py --port 5001
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Support

For issues or questions, check the following:
1. Ensure Python 3.8+ is installed
2. Verify all dependencies are installed
3. Check that the database file has write permissions
4. Review application logs in console output

---


