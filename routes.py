# import os
# import joblib
# import pandas as pd
# from datetime import datetime
# from datetime import datetime, date
# from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash
# from app import app, db, mail
# from models import User, Certificate, Verification, BlockchainBlock
# from flask_mail import Message
# import base64
# import json
# import requests
# import csv
# import zipfile
# import tempfile
# import shutil
# from utils import (
#     # ... your other imports ...
#     is_strong_password
# )
# from utils import (
#     generate_certificate_id, calculate_file_hash, calculate_blockchain_hash,
#     get_previous_hash, generate_qr_code, save_uploaded_file, verify_certificate_integrity,
#     create_blockchain_block, get_blockchain_info
# )

# # --- START: Helper function for sending reset email ---
# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('reset_token', token=token, _external=True)}

# If you did not make this request, simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)
# # --- END: Helper function ---



# # --- START: Load ML Model and Encoders ---
# try:
#     anomaly_model = joblib.load('anomaly_model.joblib')
#     le_method = joblib.load('encoder_method.joblib')
#     le_result = joblib.load('encoder_result.joblib')
#     le_ip = joblib.load('encoder_ip.joblib')
#     print("Anomaly detection model and encoders loaded successfully.")
# except FileNotFoundError:
#     anomaly_model = None
#     print("Anomaly detection model not found. Run train_anomaly_detector.py first.")
# # --- END: Load ML Model ---

# @app.route('/scan_certificate', methods=['POST'])
# @login_required
# def scan_certificate():
#     # --- IMPORTANT: PASTE YOUR API KEY HERE ---
#     API_KEY = "YOUR_REAL_API_KEY"

#     print(f"DEBUG: API_KEY = {API_KEY}")


#     if 'certificate_file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
    
#     file = request.files['certificate_file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if file:
#         try:
#             image_data = base64.b64encode(file.read()).decode('utf-8')
#             mime_type = file.mimetype

#             prompt = """
#             From this certificate image, extract the following details:
#             - The full name of the student.
#             - The name of the issuing institution or company.
#             - The title or name of the certificate.
#             - The date the certificate was issued, in YYYY-MM-DD format.

#             Provide the output as a single, minified JSON object with these exact keys: 
#             "student_name", "institution", "title", "issue_date".
#             If a value cannot be found, return null for that key.
#             """

#             payload = {
#                 "contents": [{"parts": [{"text": prompt}, {"inlineData": {"mimeType": mime_type, "data": image_data}}]}]
#             }
            
#             headers = {'Content-Type': 'application/json'}
#             # This is the corrected API URL with the new model name
#             api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"


#             # --- This is the REAL API call ---
#             response = requests.post(api_url, headers=headers, json=payload)
#             response.raise_for_status()

#             # --- Parse the REAL AI response ---
#             response_json = response.json()
#             ai_response_text = response_json['candidates'][0]['content']['parts'][0]['text']
#             cleaned_text = ai_response_text.strip().replace('```json', '').replace('```', '')
            
#             extracted_data = json.loads(cleaned_text)
            
#             return jsonify(extracted_data)

#         except requests.exceptions.RequestException as e:
#             app.logger.error(f"API Request Error: {str(e)}")
#             return jsonify({'error': f'Failed to communicate with AI service: {e}'}), 500
#         except Exception as e:
#             app.logger.error(f"AI scanning error: {str(e)}")
#             return jsonify({'error': 'Failed to process image with AI. The certificate might be unclear.'}), 500
            
#     return jsonify({'error': 'Invalid file'}), 400

# @app.route('/')
# def index():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
#     return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
        
#         if user and user.check_password(password):
#             login_user(user)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('dashboard'))
#         else:
#             flash('Invalid username or password', 'error')
    
#     return render_template('login.html')

# # In routes.py

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         role = request.form['role']
        
#         # --- START: New Password Strength Check ---
#         if not is_strong_password(password):
#             flash('Password is not strong enough. It must be at least 8 characters and include an uppercase letter, a lowercase letter, a number, and a special character.', 'danger')
#             # Return the data so the user doesn't have to re-type everything
#             return render_template('register.html', username=username, email=email, role=role)
#         # --- END: New Password Strength Check ---
        
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists', 'danger')
#             return render_template('register.html', email=email, role=role)
        
#         if User.query.filter_by(email=email).first():
#             flash('Email already registered', 'danger')
#             return render_template('register.html', username=username, role=role)
        
#         user = User(username=username, email=email, role=role)
#         user.set_password(password)
#         db.session.add(user)
#         db.session.commit()
        
#         # --- START: New Welcome Email Code ---
#         try:
#             msg = Message(
#                 subject="Welcome to CertVerify!",
#                 recipients=[user.email]
#             )
#             msg.html = f"""
#             <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
#                 <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
#                     <h2 style="color: #0056b3;">Thank you for registering with CertVerify!</h2>
#                     <p>Dear {user.username},</p>
#                     <p>Your account has been successfully created. You can now log in to manage and verify certificates with confidence.</p>
#                     <div style="text-align: center; margin: 30px 0;">
#                         <a href="{ app.config.get('BASE_URL', 'http://127.0.0.1:5000') }{ url_for('login') }" style="background-color: #28a745; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px;">
#                             Login to Your Account
#                         </a>
#                     </div>
#                     <p>Sincerely,</p>
#                     <p><strong>The CertVerify Team</strong></p>
#                 </div>
#             </div>
#             """
#             mail.send(msg)
#         except Exception as e:
#             app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
#         # --- END: New Welcome Email Code ---
        
#         flash('Registration successful! Please log in.', 'success')
#         return redirect(url_for('login'))
    
#     return render_template('register.html')

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     # Get user-specific data based on role
#     if current_user.role == 'admin':
#         certificates = Certificate.query.all()
#         verifications = Verification.query.all()
#     elif current_user.role == 'student':
#         certificates = Certificate.query.filter_by(student_email=current_user.email).all()
#         verifications = []
#     else:  # recruiter
#         certificates = []
#         verifications = Verification.query.filter_by(verifier_id=current_user.id).all()
    
#     blockchain_info = get_blockchain_info()
#     recent_verifications = Verification.query.order_by(Verification.verified_at.desc()).limit(5).all()
    
#     return render_template('dashboard.html', 
#                            certificates=certificates,
#                            verifications=verifications,
#                            blockchain_info=blockchain_info,
#                            recent_verifications=recent_verifications)

# @app.route('/upload', methods=['GET', 'POST'])
# @login_required
# def upload_certificate():
#     if current_user.role != 'admin':
#         flash('Only university administrators can upload certificates', 'error')
#         return redirect(url_for('dashboard'))
    
#     if request.method == 'POST':
#         try:
#             title = request.form['title']
#             student_name = request.form['student_name']
#             student_email = request.form['student_email']
#             institution = request.form['institution']
#             issue_date = datetime.strptime(request.form['issue_date'], '%Y-%m-%d').date()
            
#             file = request.files['certificate_file']
#             if not file or file.filename == '':
#                 flash('Please select a file', 'error')
#                 return render_template('upload.html')
            
#             file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
#             if not file_path:
#                 flash('Invalid file type.', 'error')
#                 return render_template('upload.html')
            
#             certificate_id = generate_certificate_id()
#             file_hash = calculate_file_hash(file_path)
#             previous_hash = get_previous_hash()
#             blockchain_hash = calculate_blockchain_hash(certificate_id, file_hash, previous_hash)
            
#             qr_code_path = os.path.join(app.config['UPLOAD_FOLDER'], f'qr_{certificate_id}.png')
#             generate_qr_code(certificate_id, qr_code_path)
            
#             certificate = Certificate(
#                 certificate_id=certificate_id, title=title, student_name=student_name,
#                 student_email=student_email, institution=institution, issue_date=issue_date,
#                 file_path=file_path, file_hash=file_hash, blockchain_hash=blockchain_hash,
#                 previous_hash=previous_hash, qr_code_path=qr_code_path, issuer_id=current_user.id
#             )
            
#             db.session.add(certificate)
#             db.session.commit()
            
#             try:
#                 msg = Message(subject="Your Certificate Has Been Issued!", recipients=[student_email])
#                 msg.html = f"""
#                 <div style="font-family: Arial, sans-serif; color: #333;">
#                 <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
#                 <h2 style="color: #0056b3;">Your New Certificate Has Been Issued!</h2>
#                 <p>Dear {student_name},</p>
#                 <p>Your certificate, '<strong>{title}</strong>', has been issued by <strong>{institution}</strong>.</p>
#                 <p>Your Certificate ID is: <strong>{certificate_id}</strong></p>
#                 <div style="text-align: center; margin: 20px 0;">
#                 <img src="cid:qrcode" alt="Certificate QR Code" style="max-width: 200px;">
#             </div>

#         <div style="text-align: center; margin: 30px 0;">
#             <a href="{ app.config.get('BASE_URL', 'http://127.0.0.1:5000') }{ url_for('login') }" style="background-color: #007bff; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px;">
#                  Login to View Certificate
#             </a>
#         </div>
        
#         <p>Sincerely,</p>
#         <p><strong>The CertVerify Team</strong></p>
#     </div>
# </div>
# """
#                 with app.open_resource(qr_code_path) as fp:
#                     msg.attach(filename=f'qr_{certificate_id}.png', content_type='image/png', data=fp.read(), disposition='inline', headers={'Content-ID': '<qrcode>'})
#                 mail.send(msg)
#                 flash(f'Certificate uploaded and notification sent to {student_email}!', 'success')
#             except Exception as e:
#                 flash(f"Certificate saved, but failed to send email: {str(e)}", "warning")

#             if Certificate.query.count() % 10 == 0:
#                 create_blockchain_block()
                
#             return redirect(url_for('certificate_detail', cert_id=certificate_id))
            
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error uploading certificate: {str(e)}', 'error')
#             app.logger.error(f"Certificate upload error: {str(e)}")
    
#     return render_template('upload.html')

# # --- REPLACE your old verify_certificate function with this ---

# @app.route('/verify', methods=['GET', 'POST'])
# def verify_certificate():
#     if request.method == 'POST':
#         certificate_id = request.form.get('certificate_id', '').strip()
#         verification_method = request.form.get('method', 'manual_id')
        
#         if not certificate_id:
#             flash('Please enter a certificate ID', 'error')
#             return render_template('verify.html')
        
#         certificate = Certificate.query.filter(Certificate.certificate_id.ilike(certificate_id)).first()
        
#         # --- START: New Security Check ---
#         if certificate and current_user.is_authenticated and current_user.role == 'student':
#             if certificate.student_email != current_user.email:
#                 # If the student email doesn't match, block access
#                 flash('You do not have permission to view this certificate.', 'danger')
#                 return redirect(url_for('dashboard'))
#         # --- END: New Security Check ---
        
#         verification_result = 'invalid'
        
#         if certificate:
#             if verify_certificate_integrity(certificate):
#                 if certificate.status == 'issued':
#                     verification_result = 'valid'
#                 elif certificate.status == 'revoked':
#                     verification_result = 'revoked'
#             else:
#                 verification_result = 'tampered'
        
#         verification = Verification(
#             certificate_id=certificate.id if certificate else None,
#             verifier_id=current_user.id if current_user.is_authenticated else None,
#             verification_method=verification_method,
#             ip_address=request.remote_addr,
#             user_agent=request.user_agent.string,
#             verification_result=verification_result
#         )
#         db.session.add(verification)
#         db.session.commit()
        
#         if verification_result == 'valid':
#             return render_template('verify.html', certificate=certificate, result='valid')
#         else:
#             flash('Certificate not found or invalid!', 'error')
#             return render_template('verify.html', result=verification_result)
    
#     return render_template('verify.html')

# @app.route('/certificate/<cert_id>')
# def certificate_detail(cert_id):
#     certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
#     verifications = Verification.query.filter_by(certificate_id=certificate.id).order_by(Verification.verified_at.desc()).all()
    
#     can_view = (
#         current_user.is_authenticated and (
#             current_user.role == 'admin' or
#             current_user.email == certificate.student_email or
#             current_user.role == 'recruiter'
#         )
#     )
    
#     if not can_view:
#         flash('You do not have permission to view this certificate', 'error')
#         return redirect(url_for('verify_certificate'))
    
#     return render_template('certificate_detail.html', certificate=certificate, verifications=verifications)

# @app.route('/api/verify/<cert_id>')
# def api_verify_certificate(cert_id):
#     certificate = Certificate.query.filter_by(certificate_id=cert_id).first()
    
#     if not certificate:
#         return jsonify({'status': 'invalid', 'message': 'Certificate not found'})
    
#     if not verify_certificate_integrity(certificate):
#         return jsonify({'status': 'tampered', 'message': 'Certificate file has been tampered with'})
    
#     if certificate.status == 'revoked':
#         return jsonify({'status': 'revoked', 'message': 'Certificate has been revoked'})
    
#     return jsonify({
#         'status': 'valid',
#         'message': 'Certificate is valid and authentic',
#         'certificate': { 'id': certificate.certificate_id, 'title': certificate.title, 'student_name': certificate.student_name }
#     })

# @app.route('/qr/<cert_id>')
# def serve_qr_code(cert_id):
#     certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
#     return send_file(certificate.qr_code_path, mimetype='image/png')

# @app.route('/download/<cert_id>')
# @login_required
# def download_certificate(cert_id):
#     certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    
#     can_download = (
#         current_user.role == 'admin' or
#         current_user.email == certificate.student_email
#     )
    
#     if not can_download:
#         flash('You do not have permission to download this certificate', 'error')
#         return redirect(url_for('dashboard'))
    
#     return send_file(certificate.file_path, as_attachment=True)

# @app.route('/revoke/<cert_id>')
# @login_required
# def revoke_certificate(cert_id):
#     if current_user.role != 'admin':
#         flash('Only administrators can revoke certificates', 'error')
#         return redirect(url_for('dashboard'))
    
#     certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
#     certificate.status = 'revoked'
#     db.session.commit()
    
#     flash(f'Certificate {cert_id} has been revoked', 'warning')
#     return redirect(url_for('certificate_detail', cert_id=cert_id))

# # --- START: New Routes for Password Reset ---
# @app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
#     if request.method == 'POST':
#         user = User.query.filter_by(email=request.form['email']).first()
#         if user:
#             send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('login'))
#     return render_template('request_reset.html')

# # In routes.py, replace your old reset_token function with this one

# @app.route("/reset_password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
        
#     user = User.verify_reset_token(token)
    
#     if user is None:
#         flash('That is an invalid or expired token.', 'warning')
#         return redirect(url_for('reset_request'))
        
#     if request.method == 'POST':
#         new_password = request.form['password']
        
#         # --- START: Debugging statements ---
#         print("--- PASSWORD RESET ---")
#         print(f"User: {user.username}")
#         print(f"Password Hash BEFORE update: {user.password_hash}")
        
#         user.set_password(new_password)
        
#         print(f"Password Hash AFTER update: {user.password_hash}")
#         # --- END: Debugging statements ---
        
#         db.session.commit()
#         flash('Your password has been updated! You can now log in.', 'success')
#         return redirect(url_for('login'))
        
#     return render_template('reset_token.html')
# # --- END: New Routes for Password Reset ---

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     return render_template('500.html'), 500


# # --- ADD THIS ENTIRE NEW FUNCTION TO routes.py ---

# @app.route('/bulk_upload', methods=['GET', 'POST'])
# @login_required
# def bulk_upload():
#     if current_user.role != 'admin':
#         flash('Only administrators can perform bulk uploads.', 'danger')
#         return redirect(url_for('dashboard'))

#     if request.method == 'POST':
#         if 'metadata_file' not in request.files or 'certificates_zip' not in request.files:
#             flash('Both a CSV and a ZIP file are required.', 'warning')
#             return redirect(request.url)

#         metadata_file = request.files['metadata_file']
#         certificates_zip = request.files['certificates_zip']

#         if metadata_file.filename == '' or certificates_zip.filename == '':
#             flash('Please select both files.', 'warning')
#             return redirect(request.url)
            
#         temp_dir = tempfile.mkdtemp()
        
#         try:
#             with zipfile.ZipFile(certificates_zip, 'r') as zip_ref:
#                 zip_ref.extractall(temp_dir)
            
#             metadata_file.stream.seek(0)
#             csv_data = metadata_file.stream.read().decode("utf-8")
#             reader = csv.DictReader(csv_data.splitlines())
            
#             success_count = 0
#             error_count = 0
            
#             for row in reader:
#                 try:
#                     filename = row['filename']
#                     file_path_in_zip = os.path.join(temp_dir, filename)
                    
#                     if not os.path.exists(file_path_in_zip):
#                         app.logger.error(f"File not found in ZIP: {filename}")
#                         error_count += 1
#                         continue

#                     certificate_id = generate_certificate_id()
#                     file_hash = calculate_file_hash(file_path_in_zip)
#                     previous_hash = get_previous_hash()
#                     blockchain_hash = calculate_blockchain_hash(certificate_id, file_hash, previous_hash)
                    
#                     final_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
#                     final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
#                     shutil.move(file_path_in_zip, final_file_path)

#                     qr_code_path = os.path.join(app.config['UPLOAD_FOLDER'], f'qr_{certificate_id}.png')
#                     generate_qr_code(certificate_id, qr_code_path)
                    
#                     certificate = Certificate(
#                         certificate_id=certificate_id,
#                         title=row['title'],
#                         student_name=row['student_name'],
#                         student_email=row['student_email'],
#                         institution=row['institution'],
#                         issue_date=datetime.strptime(row['issue_date'], '%Y-%m-%d').date(),
#                         file_path=final_file_path,
#                         file_hash=file_hash,
#                         blockchain_hash=blockchain_hash,
#                         previous_hash=previous_hash,
#                         qr_code_path=qr_code_path,
#                         issuer_id=current_user.id
#                     )
#                     db.session.add(certificate)
#                     success_count += 1
#                 except Exception as row_error:
#                     app.logger.error(f"Error processing row for {row.get('filename')}: {row_error}")
#                     error_count += 1

#             db.session.commit()
#             flash(f'Bulk upload complete! {success_count} certificates created successfully. {error_count} rows failed.', 'success')

#         except Exception as e:
#             db.session.rollback()
#             app.logger.error(f"Bulk upload failed: {e}")
#             flash('A critical error occurred during the bulk upload process.', 'danger')
#         finally:
#             shutil.rmtree(temp_dir)
            
#         return redirect(url_for('dashboard'))

#     return render_template('bulk_upload.html')

# # --- ADD THIS NEW FUNCTION TO routes.py ---

# # @app.route('/download_template')
# # @login_required
# # def download_template():
# #     try:
# #         # The path must be relative to your project's root folder
# #         return send_file('static/bulk_upload_template.csv', as_attachment=True)
# #     except FileNotFoundError:
# #         flash("Template file not found on the server.", "danger")
# #         return redirect(url_for('bulk_upload'))




import os
import base64
import json
import requests
import csv
import zipfile
import tempfile
import shutil
import joblib
import pandas as pd
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db, mail # Ensure mail is imported from app
from models import User, Certificate, Verification, BlockchainBlock
from flask_mail import Message
from utils import (
    generate_certificate_id, calculate_file_hash, calculate_blockchain_hash,
    get_previous_hash, generate_qr_code, save_uploaded_file, verify_certificate_integrity,
    create_blockchain_block, get_blockchain_info, is_strong_password
)

# --- START: Load ML Model and Encoders ---
try:
    anomaly_model = joblib.load('anomaly_model.joblib')
    le_method = joblib.load('encoder_method.joblib')
    le_result = joblib.load('encoder_result.joblib')
    le_ip = joblib.load('encoder_ip.joblib')
    print("Anomaly detection model and encoders loaded successfully.")
except FileNotFoundError:
    anomaly_model = None
    print("Anomaly detection model not found. Run train_anomaly_detector.py first.")
# --- END: Load ML Model ---

# --- START: Helper function for sending reset email ---
def send_reset_email(user):
    """Sends the password reset email."""
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    # Use _external=True to generate absolute URLs
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.
'''
    try:
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        # Optionally, flash a more specific error message if needed
# --- END: Helper function ---


@app.route('/')
def index():
    """Redirects to dashboard if logged in, otherwise to login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) # Redirect if already logged in
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) # Redirect if already logged in
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # --- Password Strength Check ---
        if not is_strong_password(password):
            flash('Password is not strong enough. It must be at least 8 characters and include an uppercase letter, a lowercase letter, a number, and a special character.', 'danger')
            return render_template('register.html', username=username, email=email, role=role)

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html', email=email, role=role)

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', username=username, role=role)

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # --- Send Welcome Email ---
        try:
            msg = Message(subject="Welcome to CertVerify!", recipients=[user.email])
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #0056b3;">Thank you for registering with CertVerify!</h2>
                    <p>Dear {user.username},</p>
                    <p>Your account has been successfully created. You can now log in to manage and verify certificates.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{ app.config.get('BASE_URL', 'http://127.0.0.1:5000') }{ url_for('login') }" style="background-color: #28a745; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px;">
                            Login to Your Account
                        </a>
                    </div>
                    <p>Sincerely,</p>
                    <p><strong>The CertVerify Team</strong></p>
                </div>
            </div>
            """
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logs the current user out."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Displays the user-specific dashboard."""
    certificates = []
    verifications = []
    if current_user.role == 'admin':
        certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
        verifications = Verification.query.order_by(Verification.verified_at.desc()).all()
    elif current_user.role == 'student':
        certificates = Certificate.query.filter_by(student_email=current_user.email).order_by(Certificate.created_at.desc()).all()
    elif current_user.role == 'recruiter':
        verifications = Verification.query.filter_by(verifier_id=current_user.id).order_by(Verification.verified_at.desc()).all()

    blockchain_info = get_blockchain_info()
    recent_verifications = Verification.query.order_by(Verification.verified_at.desc()).limit(5).all()

    return render_template('dashboard.html',
                           certificates=certificates,
                           verifications=verifications,
                           blockchain_info=blockchain_info,
                           recent_verifications=recent_verifications)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_certificate():
    """Handles single certificate uploads by admins."""
    if current_user.role != 'admin':
        flash('Only administrators can upload certificates', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            title = request.form['title']
            student_name = request.form['student_name']
            student_email = request.form['student_email']
            institution = request.form['institution']
            issue_date = datetime.strptime(request.form['issue_date'], '%Y-%m-%d').date()
            
            file = request.files['certificate_file']
            if not file or file.filename == '':
                flash('Please select a file', 'warning')
                return render_template('upload.html')
            
            file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            if not file_path:
                flash('Invalid file type or error saving file.', 'danger')
                return render_template('upload.html')
            
            certificate_id = generate_certificate_id()
            file_hash = calculate_file_hash(file_path)
            previous_hash = get_previous_hash()
            blockchain_hash = calculate_blockchain_hash(certificate_id, file_hash, previous_hash)
            
            qr_code_path = os.path.join(app.config['UPLOAD_FOLDER'], f'qr_{certificate_id}.png')
            generate_qr_code(certificate_id, qr_code_path)
            
            certificate = Certificate(
                certificate_id=certificate_id, title=title, student_name=student_name,
                student_email=student_email, institution=institution, issue_date=issue_date,
                file_path=file_path, file_hash=file_hash, blockchain_hash=blockchain_hash,
                previous_hash=previous_hash, qr_code_path=qr_code_path, issuer_id=current_user.id
            )
            
            db.session.add(certificate)
            db.session.commit()
            
            # --- Send Certificate Issuance Email ---
            try:
                msg = Message(subject="Your Certificate Has Been Issued!", recipients=[student_email])
                msg.html = f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #0056b3;">Your New Certificate Has Been Issued!</h2>
                        <p>Dear {student_name},</p>
                        <p>Your certificate, '<strong>{title}</strong>', has been issued by <strong>{institution}</strong>.</p>
                        <p>Your Certificate ID is: <strong>{certificate_id}</strong></p>
                        <div style="text-align: center; margin: 20px 0;">
                            <img src="cid:qrcode" alt="Certificate QR Code" style="max-width: 200px;">
                        </div>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{ app.config.get('BASE_URL', 'http://127.0.0.1:5000') }{ url_for('login') }" style="background-color: #007bff; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px;">
                                Login to View Certificate
                            </a>
                        </div>
                        <p>Sincerely,</p>
                        <p><strong>The CertVerify Team</strong></p>
                    </div>
                </div>
                """
                with app.open_resource(qr_code_path) as fp:
                    msg.attach(filename=f'qr_{certificate_id}.png', content_type='image/png', data=fp.read(), disposition='inline', headers={'Content-ID': '<qrcode>'})
                mail.send(msg)
                flash(f'Certificate uploaded and notification sent to {student_email}!', 'success')
            except Exception as e:
                flash(f"Certificate saved, but failed to send email: {str(e)}", "warning")

            # Create blockchain block periodically
            if Certificate.query.count() % 10 == 0:
                create_blockchain_block()
                
            return redirect(url_for('certificate_detail', cert_id=certificate_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading certificate: {str(e)}', 'danger')
            app.logger.error(f"Certificate upload error: {str(e)}")
    
    return render_template('upload.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_certificate():
    """Handles certificate verification requests (manual ID or QR)."""
    if request.method == 'POST':
        certificate_id = request.form.get('certificate_id', '').strip()
        verification_method = request.form.get('method', 'manual_id')
        
        if not certificate_id:
            flash('Please enter a certificate ID', 'warning')
            return render_template('verify.html')
        
        # Case-insensitive search
        certificate = Certificate.query.filter(Certificate.certificate_id.ilike(certificate_id)).first()
        
        # --- Security Check for Students ---
        if certificate and current_user.is_authenticated and current_user.role == 'student':
            if certificate.student_email != current_user.email:
                flash('You do not have permission to view this certificate.', 'danger')
                return redirect(url_for('dashboard'))
        
        verification_result = 'invalid'
        
        if certificate:
            if verify_certificate_integrity(certificate):
                if certificate.status == 'issued':
                    verification_result = 'valid'
                elif certificate.status == 'revoked':
                    verification_result = 'revoked'
            else:
                verification_result = 'tampered'
        
        # --- Anomaly Detection ---
        is_anomaly = False
        if anomaly_model:
            try:
                current_time = datetime.utcnow()
                current_data = pd.DataFrame({
                    'method': [verification_method],
                    'result': [verification_result],
                    'hour': [current_time.hour],
                    'ip_address': [request.remote_addr]
                })
                current_data['method_encoded'] = le_method.transform(current_data['method'])
                current_data['result_encoded'] = le_result.transform(current_data['result'])
                current_data['ip_encoded'] = current_data['ip_address'].apply(lambda x: le_ip.transform([x])[0] if x in le_ip.classes_ else -1)
                
                features = ['method_encoded', 'result_encoded', 'hour', 'ip_encoded']
                prediction = anomaly_model.predict(current_data[features])
                
                if prediction[0] == -1:
                    is_anomaly = True
                    app.logger.warning(f"ANOMALY DETECTED: Verification from IP {request.remote_addr} for cert ID {certificate_id} flagged.")
                    if current_user.is_authenticated and current_user.role == 'admin':
                        flash(f"Potential anomalous activity detected from IP: {request.remote_addr}", "warning")

            except Exception as ml_error:
                app.logger.error(f"Error during anomaly prediction: {ml_error}")
        # --- End Anomaly Detection ---

        # Log verification attempt
        verification = Verification(
            certificate_id=certificate.id if certificate else None,
            verifier_id=current_user.id if current_user.is_authenticated else None,
            verification_method=verification_method,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            verification_result=verification_result
            # Add anomaly flag if you modify the model: is_anomaly=is_anomaly
        )
        db.session.add(verification)
        db.session.commit()
        
        # Display result page
        if verification_result == 'valid':
            flash('Certificate is valid and authentic!', 'success')
            return render_template('verify.html', certificate=certificate, result='valid')
        elif verification_result == 'revoked':
             flash('Certificate has been revoked!', 'warning')
             return render_template('verify.html', certificate=certificate, result='revoked')
        elif verification_result == 'tampered':
             flash('Certificate file has been tampered with!', 'danger')
             return render_template('verify.html', certificate=certificate, result='tampered')
        else: # invalid
             flash('Certificate not found or invalid ID!', 'danger')
             return render_template('verify.html', result='invalid')
    
    return render_template('verify.html')

@app.route('/certificate/<cert_id>')
@login_required # Require login to view details
def certificate_detail(cert_id):
    """Displays the full details of a specific certificate."""
    certificate = Certificate.query.filter(Certificate.certificate_id.ilike(cert_id)).first_or_404()
    verifications = Verification.query.filter_by(certificate_id=certificate.id).order_by(Verification.verified_at.desc()).all()
    
    # Permission check (redundant with verify_certificate check, but good practice)
    can_view = (
        current_user.role == 'admin' or
        current_user.email == certificate.student_email or
        current_user.role == 'recruiter'
    )
    
    if not can_view:
        flash('You do not have permission to view this certificate.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('certificate_detail.html', certificate=certificate, verifications=verifications)

@app.route('/api/verify/<cert_id>')
def api_verify_certificate(cert_id):
    """API endpoint primarily for QR code scanner verification."""
    certificate = Certificate.query.filter(Certificate.certificate_id.ilike(cert_id)).first()
    
    if not certificate:
        return jsonify({'status': 'invalid', 'message': 'Certificate not found'})
    
    if not verify_certificate_integrity(certificate):
        return jsonify({'status': 'tampered', 'message': 'Certificate file has been tampered with'})
    
    if certificate.status == 'revoked':
        return jsonify({'status': 'revoked', 'message': 'Certificate has been revoked'})
    
    # Log this API verification attempt as well
    verification = Verification(
        certificate_id=certificate.id,
        verifier_id=current_user.id if current_user.is_authenticated else None,
        verification_method='qr_scan_api', # Differentiate API scans
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        verification_result='valid'
    )
    db.session.add(verification)
    db.session.commit()
    
    # Return limited data for security
    return jsonify({
        'status': 'valid',
        'message': 'Certificate is valid and authentic',
        'certificate': {
            'id': certificate.certificate_id,
            'title': certificate.title,
            'student_name': certificate.student_name,
            'institution': certificate.institution,
            'issue_date': certificate.issue_date.isoformat()
        }
    })

@app.route('/qr/<cert_id>')
def serve_qr_code(cert_id):
    """Serves the QR code image file for a given certificate."""
    certificate = Certificate.query.filter(Certificate.certificate_id.ilike(cert_id)).first_or_404()
    return send_file(certificate.qr_code_path, mimetype='image/png')

@app.route('/download/<cert_id>')
@login_required
def download_certificate(cert_id):
    """Allows authorized users to download the certificate file."""
    certificate = Certificate.query.filter(Certificate.certificate_id.ilike(cert_id)).first_or_404()
    
    can_download = (
        current_user.role == 'admin' or
        current_user.email == certificate.student_email
    )
    
    if not can_download:
        flash('You do not have permission to download this certificate.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Ensure file exists before sending
    if not os.path.exists(certificate.file_path):
        flash('Certificate file not found on server.', 'danger')
        return redirect(url_for('certificate_detail', cert_id=cert_id))
        
    return send_file(certificate.file_path, as_attachment=True)

@app.route('/revoke/<cert_id>')
@login_required
def revoke_certificate(cert_id):
    """Allows admins to revoke a certificate."""
    if current_user.role != 'admin':
        flash('Only administrators can revoke certificates.', 'danger')
        return redirect(url_for('dashboard'))
    
    certificate = Certificate.query.filter(Certificate.certificate_id.ilike(cert_id)).first_or_404()
    if certificate.status != 'revoked':
        certificate.status = 'revoked'
        db.session.commit()
        flash(f'Certificate {cert_id} has been revoked.', 'warning')
    else:
        flash(f'Certificate {cert_id} was already revoked.', 'info')
        
    return redirect(url_for('certificate_detail', cert_id=cert_id))

# --- Password Reset Routes ---
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """Handles the request for a password reset link."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            send_reset_email(user)
        # Show same message regardless to prevent email enumeration
        flash('If an account with that email exists, an email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('request_reset.html')

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """Handles the actual password reset using the token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    if request.method == 'POST':
        password = request.form['password']
        if not is_strong_password(password):
             flash('Password is not strong enough.', 'danger')
             return render_template('reset_token.html') # Stay on the page

        user.set_password(password)
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html')
# --- End Password Reset Routes ---

# --- AI Scan Route ---
@app.route('/scan_certificate', methods=['POST'])
@login_required
def scan_certificate():
    """Handles AI scanning of uploaded certificate images."""
    API_KEY = app.config.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE") # Get key from config or fallback
    if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
         app.logger.warning("GEMINI API KEY not configured!")
         return jsonify({'error': 'AI service not configured on the server.'}), 500

    if 'certificate_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['certificate_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            image_data = base64.b64encode(file.read()).decode('utf-8')
            mime_type = file.mimetype

            prompt = """
            From this certificate image/PDF, extract the following details:
            - The full name of the student/recipient.
            - The name of the issuing institution or company.
            - The title or name/description of the certificate/course/award.
            - The date the certificate was issued or completed, in YYYY-MM-DD format if possible, otherwise as text.

            Provide the output as a single, minified JSON object with these exact keys: 
            "student_name", "institution", "title", "issue_date".
            If a value cannot be found, return null or an empty string for that key. Ensure the output is valid JSON.
            """

            payload = {
                "contents": [{"parts": [{"text": prompt}, {"inlineData": {"mimeType": mime_type, "data": image_data}}]}]
            }
            
            headers = {'Content-Type': 'application/json'}
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

            response = requests.post(api_url, headers=headers, json=payload, timeout=30) # Add timeout
            response.raise_for_status()

            response_json = response.json()
            
            # Defensive coding to handle potential variations in API response structure
            if not response_json.get('candidates') or not response_json['candidates'][0].get('content') or not response_json['candidates'][0]['content'].get('parts'):
                 raise ValueError("Unexpected API response format")
                 
            ai_response_text = response_json['candidates'][0]['content']['parts'][0].get('text', '')
            cleaned_text = ai_response_text.strip().lstrip('```json').rstrip('```').strip()
            
            # Try to parse the JSON
            try:
                extracted_data = json.loads(cleaned_text)
            except json.JSONDecodeError:
                app.logger.error(f"Failed to parse JSON from AI response: {cleaned_text}")
                raise ValueError("AI returned non-JSON text")

            # Validate expected keys are present
            expected_keys = ["student_name", "institution", "title", "issue_date"]
            if not all(key in extracted_data for key in expected_keys):
                 app.logger.warning(f"AI response missing expected keys: {extracted_data}")
                 # Optionally try to fill missing keys with None or re-prompt

            return jsonify(extracted_data)

        except requests.exceptions.Timeout:
            app.logger.error("API Request timed out.")
            return jsonify({'error': 'AI service request timed out. Please try again.'}), 504
        except requests.exceptions.RequestException as e:
            app.logger.error(f"API Request Error: {str(e)}")
            # Check for specific API key errors if possible from e.response.text
            error_detail = "Failed to communicate with AI service."
            if e.response is not None:
                try:
                    error_json = e.response.json()
                    if 'error' in error_json and 'message' in error_json['error']:
                         error_detail = f"AI Service Error: {error_json['error']['message']}"
                except ValueError: # If response is not JSON
                    error_detail = f"AI Service Error: {e.response.status_code} {e.response.reason}"

            return jsonify({'error': error_detail}), 500
        except Exception as e:
            app.logger.error(f"AI scanning processing error: {str(e)}")
            return jsonify({'error': f'Failed to process image with AI: {str(e)}. The document might be unclear or unsupported.'}), 500
            
    return jsonify({'error': 'Invalid or no file provided'}), 400
# --- End AI Scan Route ---


# --- Bulk Upload Route ---
@app.route('/bulk_upload', methods=['GET', 'POST'])
@login_required
def bulk_upload():
    """Handles bulk certificate uploads via CSV and ZIP."""
    if current_user.role != 'admin':
        flash('Only administrators can perform bulk uploads.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if 'metadata_file' not in request.files or 'certificates_zip' not in request.files:
            flash('Both a CSV and a ZIP file are required.', 'warning')
            return redirect(request.url)

        metadata_file = request.files['metadata_file']
        certificates_zip = request.files['certificates_zip']

        if not metadata_file or metadata_file.filename == '' or not certificates_zip or certificates_zip.filename == '':
            flash('Please select both files.', 'warning')
            return redirect(request.url)
        
        # Validate file types
        if not metadata_file.filename.lower().endswith('.csv'):
             flash('Metadata file must be a CSV.', 'danger')
             return redirect(request.url)
        if not certificates_zip.filename.lower().endswith('.zip'):
             flash('Certificates file must be a ZIP archive.', 'danger')
             return redirect(request.url)
             
        # Securely create a temporary directory
        temp_dir = tempfile.mkdtemp()
        app.logger.info(f"Created temporary directory for bulk upload: {temp_dir}")
        
        processed_files = set() # To track files moved from zip
        
        try:
            # Unzip the certificate files safely
            try:
                with zipfile.ZipFile(certificates_zip, 'r') as zip_ref:
                    # Check for potentially malicious paths (e.g., ../../..)
                    for member in zip_ref.namelist():
                         if member.startswith('/') or '..' in member:
                              raise ValueError("ZIP contains invalid paths.")
                    zip_ref.extractall(temp_dir)
                app.logger.info(f"Successfully extracted ZIP file to {temp_dir}")
            except (zipfile.BadZipFile, ValueError) as zip_error:
                app.logger.error(f"Error processing ZIP file: {zip_error}")
                flash(f"Error reading ZIP file: {zip_error}", 'danger')
                return redirect(request.url)
            
            # Read and process the CSV file
            try:
                metadata_file.stream.seek(0)
                # Use stream directly to avoid loading large files into memory
                csv_content = metadata_file.stream.read().decode('utf-8-sig') # Handle potential BOM
                reader = csv.DictReader(csv_content.splitlines())
                
                # Check required columns
                required_cols = ['filename', 'title', 'student_name', 'student_email', 'institution', 'issue_date']
                if not all(col in reader.fieldnames for col in required_cols):
                    missing = [col for col in required_cols if col not in reader.fieldnames]
                    raise ValueError(f"CSV file is missing required columns: {', '.join(missing)}")
                    
            except Exception as csv_error:
                app.logger.error(f"Error reading or parsing CSV file: {csv_error}")
                flash(f"Error reading CSV file: {csv_error}", 'danger')
                return redirect(request.url)

            success_count = 0
            error_count = 0
            skipped_files = 0
            
            # Process each row in the CSV
            for i, row in enumerate(reader):
                row_num = i + 2 # Account for header row
                try:
                    # Basic validation for row data
                    filename = row.get('filename','').strip()
                    title = row.get('title','').strip()
                    student_name = row.get('student_name','').strip()
                    student_email = row.get('student_email','').strip()
                    institution = row.get('institution','').strip()
                    issue_date_str = row.get('issue_date','').strip()

                    if not all([filename, title, student_name, student_email, institution, issue_date_str]):
                         app.logger.warning(f"Row {row_num}: Skipping row due to missing required data.")
                         error_count += 1
                         continue

                    # Validate date format before parsing
                    try:
                        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        app.logger.warning(f"Row {row_num}: Invalid date format for '{issue_date_str}'. Skipping.")
                        error_count += 1
                        continue

                    # Securely join path and check if file exists in extracted temp dir
                    file_path_in_zip = os.path.normpath(os.path.join(temp_dir, filename))
                    if not file_path_in_zip.startswith(os.path.abspath(temp_dir)) or not os.path.isfile(file_path_in_zip):
                        app.logger.warning(f"Row {row_num}: File '{filename}' not found or invalid path in ZIP. Skipping.")
                        error_count += 1
                        skipped_files +=1
                        continue
                    
                    # Generate hashes and unique ID
                    certificate_id = generate_certificate_id()
                    file_hash = calculate_file_hash(file_path_in_zip)
                    previous_hash = get_previous_hash()
                    blockchain_hash = calculate_blockchain_hash(certificate_id, file_hash, previous_hash)
                    
                    # Securely create final filename and move the file
                    final_filename_base = secure_filename(filename) # Clean the filename
                    final_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{certificate_id[:8]}_{final_filename_base}"
                    final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_filename)
                    
                    shutil.move(file_path_in_zip, final_file_path)
                    processed_files.add(filename) # Mark file as processed

                    qr_code_path = os.path.join(app.config['UPLOAD_FOLDER'], f'qr_{certificate_id}.png')
                    generate_qr_code(certificate_id, qr_code_path)
                    
                    # Create DB record
                    certificate = Certificate(
                        certificate_id=certificate_id, title=title, student_name=student_name,
                        student_email=student_email, institution=institution, issue_date=issue_date,
                        file_path=final_file_path, file_hash=file_hash, blockchain_hash=blockchain_hash,
                        previous_hash=previous_hash, qr_code_path=qr_code_path, issuer_id=current_user.id
                    )
                    db.session.add(certificate)
                    success_count += 1
                    
                    # Commit in batches to improve performance for very large files
                    if success_count % 100 == 0:
                         db.session.commit()
                         app.logger.info(f"Committed batch of 100 certificates. Total successful: {success_count}")

                except KeyError as ke:
                    app.logger.warning(f"Row {row_num}: Missing column '{ke}'. Skipping.")
                    error_count += 1
                except Exception as row_error:
                    app.logger.error(f"Row {row_num}: Error processing file '{filename}': {row_error}")
                    error_count += 1
                    db.session.rollback() # Rollback this specific certificate on error

            # Final commit for any remaining certificates
            db.session.commit()
            
            if skipped_files > 0:
                 flash(f"Warning: {skipped_files} files listed in CSV were not found in the ZIP.", 'warning')
            flash(f'Bulk upload processed! {success_count} certificates created. {error_count} rows had errors.', 'success' if error_count == 0 else 'warning')

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Critical bulk upload error: {e}")
            flash(f'A critical error occurred: {e}. Please check logs.', 'danger')
        finally:
            # Clean up the temporary directory and its contents
            if os.path.exists(temp_dir):
                 try:
                     shutil.rmtree(temp_dir)
                     app.logger.info(f"Successfully removed temporary directory: {temp_dir}")
                 except Exception as cleanup_error:
                      app.logger.error(f"Error removing temporary directory {temp_dir}: {cleanup_error}")
            
        return redirect(url_for('dashboard'))

    # GET request just shows the upload form
    return render_template('bulk_upload.html')
# --- End Bulk Upload Route ---


# --- Error Handlers ---
@app.errorhandler(404)
def not_found_error(error):
    """Handles 404 Not Found errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handles 500 Internal Server errors."""
    db.session.rollback() # Rollback the session in case of DB errors
    app.logger.error(f"Server Error: {error}", exc_info=True) # Log the full traceback
    return render_template('500.html'), 500
# --- End Error Handlers ---

# --- Commented out Download Template route as we use direct link ---
# @app.route('/download_template')
# @login_required
# def download_template():
#     try:
#         return send_file('static/bulk_upload_template.csv', as_attachment=True)
#     except FileNotFoundError:
#         flash("Template file not found on the server.", "danger")
#         return redirect(url_for('bulk_upload'))

