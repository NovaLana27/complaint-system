# Student Complaint Management System

## Project Description
A backend API built with Flask that allows students to submit complaints
and administrative staff to review and respond to them.
The system routes each complaint to the correct department.

## Team Members
- Person 1 - Project Lead (App structure, database, models)
- Person 2 - Authentication Engineer (Login, registration, session management)
- Mercy - Complaints Engineer (Student complaint features)
- Esther - Admin and QA Engineer (Admin features, testing, documentation)

## Requirements
- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug
- pytest

## Setup Instructions

### Step 1 - Clone the repository
git clone https://github.com/NovaLana27
### Step 2 - Create a virtual environment
python -m venv venv
### Step 3 - Activate the virtual environment
venv\Scripts\activate
### Step 4 - Install dependencies
pip install -r requirements.txt

### Step 5 - Run the application
python run.py

### Step 6 - Run the tests
pytest

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register a new student account |
| POST | /auth/login | Log in and start a session |
| POST | /auth/logout | Log out and end the session |
| GET | /auth/me | Get current logged in user details |

### Student Complaints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /complaints/ | Submit a new complaint |
| GET | /complaints/ | View all your complaints |
| GET | /complaints/<id> | View a single complaint |
| PUT | /complaints/<id> | Edit a complaint |
| DELETE | /complaints/<id> | Delete a complaint |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /admin/complaints/ | View all complaints in your department |
| PUT | /admin/complaints/<id>/status | Update a complaint status |
| PUT | /admin/complaints/<id>/reply | Reply to a complaint |
