import os
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Certificate, Verification, BlockchainBlock
from utils import (
    generate_certificate_id, calculate_file_hash, calculate_blockchain_hash,
    get_previous_hash, generate_qr_code, save_uploaded_file, verify_certificate_integrity,
    create_blockchain_block, get_blockchain_info
)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user-specific data based on role
    if current_user.role == 'admin':
        certificates = Certificate.query.all()
        verifications = Verification.query.all()
    elif current_user.role == 'student':
        certificates = Certificate.query.filter_by(student_email=current_user.email).all()
        verifications = []
    else:  # recruiter
        certificates = []
        verifications = Verification.query.filter_by(verifier_id=current_user.id).all()
    
    # Get blockchain info
    blockchain_info = get_blockchain_info()
    
    # Get recent activity
    recent_verifications = Verification.query.order_by(Verification.verified_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         certificates=certificates,
                         verifications=verifications,
                         blockchain_info=blockchain_info,
                         recent_verifications=recent_verifications)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_certificate():
    if current_user.role != 'admin':
        flash('Only university administrators can upload certificates', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form['title']
            student_name = request.form['student_name']
            student_email = request.form['student_email']
            institution = request.form['institution']
            issue_date = datetime.strptime(request.form['issue_date'], '%Y-%m-%d').date()
            
            # Handle file upload
            file = request.files['certificate_file']
            if not file or file.filename == '':
                flash('Please select a file', 'error')
                return render_template('upload.html')
            
            # Save file
            file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            if not file_path:
                flash('Invalid file type. Please upload PDF, PNG, JPG, JPEG, or GIF files.', 'error')
                return render_template('upload.html')
            
            # Generate certificate data
            certificate_id = generate_certificate_id()
            file_hash = calculate_file_hash(file_path)
            previous_hash = get_previous_hash()
            blockchain_hash = calculate_blockchain_hash(certificate_id, file_hash, previous_hash)
            
            # Generate QR code
            qr_code_path = os.path.join(app.config['UPLOAD_FOLDER'], f'qr_{certificate_id}.png')
            generate_qr_code(certificate_id, qr_code_path)
            
            # Create certificate record
            certificate = Certificate(
                certificate_id=certificate_id,
                title=title,
                student_name=student_name,
                student_email=student_email,
                institution=institution,
                issue_date=issue_date,
                file_path=file_path,
                file_hash=file_hash,
                blockchain_hash=blockchain_hash,
                previous_hash=previous_hash,
                qr_code_path=qr_code_path,
                issuer_id=current_user.id
            )
            
            db.session.add(certificate)
            db.session.commit()
            
            # Create blockchain block periodically (every 10 certificates)
            if Certificate.query.count() % 10 == 0:
                create_blockchain_block()
            
            flash(f'Certificate uploaded successfully! ID: {certificate_id}', 'success')
            return redirect(url_for('certificate_detail', cert_id=certificate_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading certificate: {str(e)}', 'error')
            app.logger.error(f"Certificate upload error: {str(e)}")
    
    return render_template('upload.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_certificate():
    if request.method == 'POST':
        certificate_id = request.form.get('certificate_id', '').strip().upper()
        verification_method = request.form.get('method', 'manual_id')
        
        if not certificate_id:
            flash('Please enter a certificate ID', 'error')
            return render_template('verify.html')
        
        # Find certificate
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()
        
        # Record verification attempt
        verification_result = 'invalid'
        if certificate:
            # Verify file integrity
            if verify_certificate_integrity(certificate):
                if certificate.status == 'issued':
                    verification_result = 'valid'
                elif certificate.status == 'revoked':
                    verification_result = 'revoked'
            else:
                verification_result = 'tampered'
        
        # Log verification
        verification = Verification(
            certificate_id=certificate.id if certificate else None,
            verifier_id=current_user.id if current_user.is_authenticated else None,
            verification_method=verification_method,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            verification_result=verification_result
        )
        db.session.add(verification)
        db.session.commit()
        
        # Return result
        if verification_result == 'valid':
            flash('Certificate is valid and authentic!', 'success')
            return render_template('verify.html', certificate=certificate, result='valid')
        elif verification_result == 'revoked':
            flash('Certificate has been revoked!', 'warning')
            return render_template('verify.html', certificate=certificate, result='revoked')
        elif verification_result == 'tampered':
            flash('Certificate file has been tampered with!', 'error')
            return render_template('verify.html', certificate=certificate, result='tampered')
        else:
            flash('Certificate not found or invalid!', 'error')
            return render_template('verify.html', result='invalid')
    
    return render_template('verify.html')

@app.route('/certificate/<cert_id>')
def certificate_detail(cert_id):
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    verifications = Verification.query.filter_by(certificate_id=certificate.id).order_by(Verification.verified_at.desc()).all()
    
    # Check if user can view this certificate
    can_view = (
        current_user.is_authenticated and (
            current_user.role == 'admin' or
            current_user.email == certificate.student_email or
            current_user.role == 'recruiter'
        )
    )
    
    if not can_view:
        flash('You do not have permission to view this certificate', 'error')
        return redirect(url_for('verify_certificate'))
    
    return render_template('certificate_detail.html', certificate=certificate, verifications=verifications)

@app.route('/api/verify/<cert_id>')
def api_verify_certificate(cert_id):
    """API endpoint for QR code verification"""
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first()
    
    if not certificate:
        return jsonify({'status': 'invalid', 'message': 'Certificate not found'})
    
    # Verify file integrity
    if not verify_certificate_integrity(certificate):
        return jsonify({'status': 'tampered', 'message': 'Certificate file has been tampered with'})
    
    if certificate.status == 'revoked':
        return jsonify({'status': 'revoked', 'message': 'Certificate has been revoked'})
    
    # Log verification
    verification = Verification(
        certificate_id=certificate.id,
        verifier_id=current_user.id if current_user.is_authenticated else None,
        verification_method='qr_scan',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        verification_result='valid'
    )
    db.session.add(verification)
    db.session.commit()
    
    return jsonify({
        'status': 'valid',
        'message': 'Certificate is valid and authentic',
        'certificate': {
            'id': certificate.certificate_id,
            'title': certificate.title,
            'student_name': certificate.student_name,
            'institution': certificate.institution,
            'issue_date': certificate.issue_date.isoformat(),
            'blockchain_hash': certificate.blockchain_hash
        }
    })

@app.route('/qr/<cert_id>')
def serve_qr_code(cert_id):
    """Serve QR code image"""
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    return send_file(certificate.qr_code_path, mimetype='image/png')

@app.route('/download/<cert_id>')
@login_required
def download_certificate(cert_id):
    """Download certificate file"""
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    
    # Check permissions
    can_download = (
        current_user.role == 'admin' or
        current_user.email == certificate.student_email
    )
    
    if not can_download:
        flash('You do not have permission to download this certificate', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(certificate.file_path, as_attachment=True)

@app.route('/revoke/<cert_id>')
@login_required
def revoke_certificate(cert_id):
    """Revoke a certificate (admin only)"""
    if current_user.role != 'admin':
        flash('Only administrators can revoke certificates', 'error')
        return redirect(url_for('dashboard'))
    
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    certificate.status = 'revoked'
    db.session.commit()
    
    flash(f'Certificate {cert_id} has been revoked', 'warning')
    return redirect(url_for('certificate_detail', cert_id=cert_id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
