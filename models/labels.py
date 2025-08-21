
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Label(db.Model):
    __tablename__ = 'labels'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    chain_id = db.Column(db.Integer)
    rpc_url = db.Column(db.String(500))
    fallback = db.Column(db.String(500))
    is_preset = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)