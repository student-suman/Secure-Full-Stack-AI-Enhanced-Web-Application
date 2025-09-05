// QR Code Scanner functionality

let html5QrCode = null;
let isScanning = false;

document.addEventListener('DOMContentLoaded', function() {
    const startScanBtn = document.getElementById('startScan');
    const qrStatus = document.getElementById('qr-status');
    
    if (startScanBtn) {
        startScanBtn.addEventListener('click', function() {
            if (!isScanning) {
                startQRScanner();
            } else {
                stopQRScanner();
            }
        });
    }
});

function startQRScanner() {
    const qrReader = document.getElementById('qr-reader');
    const startScanBtn = document.getElementById('startScan');
    const qrStatus = document.getElementById('qr-status');
    
    if (!qrReader) return;
    
    // Check if camera is available
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showQRError('Camera not supported in this browser');
        return;
    }
    
    html5QrCode = new Html5Qrcode("qr-reader");
    
    // Update UI
    startScanBtn.innerHTML = '<i class="fas fa-stop me-1"></i>Stop Scanner';
    startScanBtn.className = 'btn btn-danger';
    isScanning = true;
    
    // Start scanning
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
    };
    
    html5QrCode.start(
        { facingMode: "environment" }, // Use back camera
        config,
        onScanSuccess,
        onScanError
    ).catch(err => {
        console.error('Failed to start QR scanner:', err);
        showQRError('Failed to access camera. Please check permissions.');
        resetQRScanner();
    });
    
    // Show status
    qrStatus.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-camera me-2"></i>
            Position the QR code within the scanning area
        </div>
    `;
}

function stopQRScanner() {
    if (html5QrCode && isScanning) {
        html5QrCode.stop().then(() => {
            resetQRScanner();
        }).catch(err => {
            console.error('Error stopping QR scanner:', err);
            resetQRScanner();
        });
    }
}

function resetQRScanner() {
    const startScanBtn = document.getElementById('startScan');
    const qrStatus = document.getElementById('qr-status');
    const qrReader = document.getElementById('qr-reader');
    
    if (startScanBtn) {
        startScanBtn.innerHTML = '<i class="fas fa-camera me-1"></i>Start QR Scanner';
        startScanBtn.className = 'btn btn-success';
    }
    
    if (qrReader) {
        qrReader.innerHTML = '';
    }
    
    if (qrStatus && !qrStatus.querySelector('.alert-success, .alert-danger')) {
        qrStatus.innerHTML = `
            <button type="button" class="btn btn-success" id="startScan">
                <i class="fas fa-camera me-1"></i>Start QR Scanner
            </button>
        `;
        
        // Re-attach event listener
        const newStartBtn = document.getElementById('startScan');
        if (newStartBtn) {
            newStartBtn.addEventListener('click', function() {
                if (!isScanning) {
                    startQRScanner();
                } else {
                    stopQRScanner();
                }
            });
        }
    }
    
    isScanning = false;
    html5QrCode = null;
}

function onScanSuccess(decodedText, decodedResult) {
    console.log('QR Code scanned:', decodedText);
    
    // Stop scanning
    stopQRScanner();
    
    // Extract certificate ID from URL or direct ID
    let certificateId = null;
    
    if (decodedText.includes('/verify/')) {
        // Extract from URL
        const urlParts = decodedText.split('/verify/');
        certificateId = urlParts[1];
    } else if (decodedText.match(/^[A-F0-9]{32}$/)) {
        // Direct certificate ID
        certificateId = decodedText;
    }
    
    if (certificateId) {
        // Show loading state
        const qrStatus = document.getElementById('qr-status');
        qrStatus.innerHTML = `
            <div class="alert alert-info">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                Verifying certificate ${certificateId}...
            </div>
        `;
        
        // Verify certificate via API
        verifyCertificateAPI(certificateId);
    } else {
        showQRError('Invalid QR code format');
    }
}

function onScanError(errorMessage) {
    // Don't log every scan error, they're too frequent
    // console.log('QR scan error:', errorMessage);
}

function verifyCertificateAPI(certificateId) {
    fetch(`/api/verify/${certificateId}`)
        .then(response => response.json())
        .then(data => {
            showVerificationResult(data, certificateId);
        })
        .catch(error => {
            console.error('Verification API error:', error);
            showQRError('Failed to verify certificate. Please try again.');
        });
}

function showVerificationResult(data, certificateId) {
    const qrStatus = document.getElementById('qr-status');
    
    if (data.status === 'valid') {
        qrStatus.innerHTML = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle me-2"></i>Certificate Valid!</h5>
                <p class="mb-2">${data.message}</p>
                <hr>
                <strong>Certificate Details:</strong><br>
                <small>
                    <strong>ID:</strong> ${data.certificate.id}<br>
                    <strong>Title:</strong> ${data.certificate.title}<br>
                    <strong>Student:</strong> ${data.certificate.student_name}<br>
                    <strong>Institution:</strong> ${data.certificate.institution}<br>
                    <strong>Issue Date:</strong> ${new Date(data.certificate.issue_date).toLocaleDateString()}
                </small>
                <div class="mt-3">
                    <a href="/certificate/${certificateId}" class="btn btn-primary btn-sm">
                        <i class="fas fa-eye me-1"></i>View Full Details
                    </a>
                    <button type="button" class="btn btn-secondary btn-sm ms-2" onclick="resetQRScanner()">
                        <i class="fas fa-qrcode me-1"></i>Scan Another
                    </button>
                </div>
            </div>
        `;
    } else if (data.status === 'revoked') {
        qrStatus.innerHTML = `
            <div class="alert alert-warning">
                <h5><i class="fas fa-exclamation-triangle me-2"></i>Certificate Revoked</h5>
                <p class="mb-2">${data.message}</p>
                <button type="button" class="btn btn-secondary btn-sm" onclick="resetQRScanner()">
                    <i class="fas fa-qrcode me-1"></i>Scan Another
                </button>
            </div>
        `;
    } else if (data.status === 'tampered') {
        qrStatus.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-times-circle me-2"></i>Certificate Tampered</h5>
                <p class="mb-2">${data.message}</p>
                <button type="button" class="btn btn-secondary btn-sm" onclick="resetQRScanner()">
                    <i class="fas fa-qrcode me-1"></i>Scan Another
                </button>
            </div>
        `;
    } else {
        qrStatus.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-times-circle me-2"></i>Certificate Not Found</h5>
                <p class="mb-2">${data.message || 'Invalid or unknown certificate ID'}</p>
                <button type="button" class="btn btn-secondary btn-sm" onclick="resetQRScanner()">
                    <i class="fas fa-qrcode me-1"></i>Scan Another
                </button>
            </div>
        `;
    }
}

function showQRError(message) {
    const qrStatus = document.getElementById('qr-status');
    if (qrStatus) {
        qrStatus.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
                <div class="mt-2">
                    <button type="button" class="btn btn-secondary btn-sm" onclick="resetQRScanner()">
                        <i class="fas fa-redo me-1"></i>Try Again
                    </button>
                </div>
            </div>
        `;
    }
    resetQRScanner();
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (html5QrCode && isScanning) {
        html5QrCode.stop();
    }
});

// Handle tab switching to stop scanner
document.addEventListener('visibilitychange', function() {
    if (document.hidden && isScanning) {
        stopQRScanner();
    }
});
