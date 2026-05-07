class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration (optional - can be set via environment variables)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = None  # Set via environment variable: MAIL_USERNAME
    MAIL_PASSWORD = None  # Set via environment variable: MAIL_PASSWORD
    MAIL_DEFAULT_SENDER = "noreply@complaint-system.com"