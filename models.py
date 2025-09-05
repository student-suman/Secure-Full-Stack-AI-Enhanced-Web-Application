from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, student, recruiter
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    certificates = db.relationship('Certificate', backref='issuer', lazy=True, foreign_keys='Certificate.issuer_id')
    verifications = db.relationship('Verification', backref='verifier', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(120), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash
    blockchain_hash = db.Column(db.String(64), nullable=False)  # Mock blockchain hash
    previous_hash = db.Column(db.String(64), nullable=True)  # For blockchain simulation
    qr_code_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='issued')  # issued, verified, revoked
    issuer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    verifications = db.relationship('Verification', backref='certificate', lazy=True)

    def __repr__(self):
        return f'<Certificate {self.certificate_id}>'

class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificate.id'), nullable=False)
    verifier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verification_method = db.Column(db.String(20), nullable=False)  # qr_scan, manual_id
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    verification_result = db.Column(db.String(20), nullable=False)  # valid, invalid, revoked
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Verification {self.id}>'

class BlockchainBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_number = db.Column(db.Integer, unique=True, nullable=False)
    block_hash = db.Column(db.String(64), unique=True, nullable=False)
    previous_hash = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    certificate_count = db.Column(db.Integer, default=0)
    merkle_root = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        return f'<Block {self.block_number}>'
