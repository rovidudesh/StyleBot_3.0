from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from pathlib import Path

db = SQLAlchemy()

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    body_type = db.Column(db.String(50))
    height = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    style_preferences = db.Column(db.String(200))
    color_preferences = db.Column(db.String(200))
    
    def __repr__(self):
        return f"<UserSession {self.session_id}>"

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('user_session.session_id'))
    message = db.Column(db.Text)
    is_bot = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_session = db.relationship('UserSession', backref=db.backref('messages', lazy=True))

def init_db(app):
    # Create database directory if it doesn't exist
    db_dir = Path(__file__).parent / 'database'
    db_dir.mkdir(exist_ok=True)
    
    db.init_app(app)
    with app.app_context():
        db.create_all()