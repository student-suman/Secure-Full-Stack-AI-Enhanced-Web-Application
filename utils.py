import os
import hashlib
import secrets
import qrcode
from io import BytesIO
from PIL import Image
from datetime import datetime
from werkzeug.utils import secure_filename
from app import db
from models import Certificate, BlockchainBlock

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_certificate_id():
    """Generate a unique certificate ID"""
    return secrets.token_hex(16).upper()

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_blockchain_hash(certificate_id, file_hash, previous_hash="0"):
    """Calculate blockchain hash for certificate"""
    data = f"{certificate_id}{file_hash}{previous_hash}{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()

def get_previous_hash():
    """Get the hash of the last certificate for blockchain simulation"""
    last_cert = Certificate.query.order_by(Certificate.id.desc()).first()
    return last_cert.blockchain_hash if last_cert else "0"

def generate_qr_code(certificate_id, save_path):
    """Generate QR code for certificate verification"""
    verification_url = f"https://certificate-verify.com/verify/{certificate_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(save_path)
    return save_path

def save_uploaded_file(file, upload_folder):
    """Save uploaded file securely"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to prevent filename conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return file_path
    return None

def verify_certificate_integrity(certificate):
    """Verify certificate file integrity using stored hash"""
    if not os.path.exists(certificate.file_path):
        return False
    
    current_hash = calculate_file_hash(certificate.file_path)
    return current_hash == certificate.file_hash

def create_blockchain_block():
    """Create a new blockchain block (simulation)"""
    last_block = BlockchainBlock.query.order_by(BlockchainBlock.block_number.desc()).first()
    block_number = (last_block.block_number + 1) if last_block else 1
    previous_hash = last_block.block_hash if last_block else "0"
    
    # Get certificates added since last block
    certificates = Certificate.query.filter(
        Certificate.id > (last_block.id if last_block else 0)
    ).all()
    
    # Calculate merkle root (simplified)
    cert_hashes = [cert.blockchain_hash for cert in certificates]
    merkle_root = hashlib.sha256(''.join(cert_hashes).encode()).hexdigest() if cert_hashes else "0"
    
    # Calculate block hash
    block_data = f"{block_number}{previous_hash}{merkle_root}{datetime.utcnow().isoformat()}"
    block_hash = hashlib.sha256(block_data.encode()).hexdigest()
    
    # Create block
    block = BlockchainBlock(
        block_number=block_number,
        block_hash=block_hash,
        previous_hash=previous_hash,
        certificate_count=len(certificates),
        merkle_root=merkle_root
    )
    
    db.session.add(block)
    db.session.commit()
    return block

def get_blockchain_info():
    """Get blockchain statistics"""
    total_blocks = BlockchainBlock.query.count()
    total_certificates = Certificate.query.count()
    last_block = BlockchainBlock.query.order_by(BlockchainBlock.block_number.desc()).first()
    
    return {
        'total_blocks': total_blocks,
        'total_certificates': total_certificates,
        'last_block_hash': last_block.block_hash if last_block else None,
        'last_block_time': last_block.timestamp if last_block else None
    }
