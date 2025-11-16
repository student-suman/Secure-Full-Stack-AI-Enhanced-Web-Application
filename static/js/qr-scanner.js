// --- NEW, COMPLETE qr-scanner.js ---

document.addEventListener('DOMContentLoaded', function () {
    const startScanBtn = document.getElementById('startScan');
    if (startScanBtn) {
        startScanBtn.addEventListener('click', toggleCameraScanner);
    }

    const fileInput = document.getElementById('qr-input-file');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
});

let html5QrCode = null;

function toggleCameraScanner() {
    if (html5QrCode && html5QrCode.isScanning) {
        stopCameraScanner();
    } else {
        startCameraScanner();
    }
}

function startCameraScanner() {
    const startScanBtn = document.getElementById('startScan');
    startScanBtn.disabled = true;

    html5QrCode = new Html5Qrcode("qr-reader");
    const config = { fps: 10, qrbox: { width: 250, height: 250 } };

    html5QrCode.start(
        { facingMode: "environment" },
        config,
        (decodedText, decodedResult) => {
            // This is the success callback
            stopCameraScanner();
            handleDecodedText(decodedText);
        },
        (errorMessage) => {
            // This is the error callback, we can ignore it
        })
        .then(() => {
            startScanBtn.textContent = 'Stop Scanner';
            startScanBtn.classList.replace('btn-success', 'btn-danger');
            startScanBtn.disabled = false;
        })
        .catch(err => {
            alert('Could not start camera. Please check permissions.');
            console.error(err);
            startScanBtn.disabled = false;
        });
}

function stopCameraScanner() {
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop().then(() => {
            const startScanBtn = document.getElementById('startScan');
            startScanBtn.textContent = 'Start Camera Scanner';
            startScanBtn.classList.replace('btn-danger', 'btn-success');
        }).catch(err => console.error("Failed to stop scanner", err));
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    const html5QrCode = new Html5Qrcode("qr-reader");
    html5QrCode.scanFile(file, true)
        .then(decodedText => {
            handleDecodedText(decodedText);
        })
        .catch(err => {
            alert("Could not find a QR code in the uploaded image.");
            console.error(`Error scanning file: ${err}`);
        });
}

function handleDecodedText(decodedText) {
    console.log(`QR Code raw data: ${decodedText}`);

    // This simplified logic finds the last part of a URL or assumes the whole text is the ID
    const parts = decodedText.split('/');
    const certificateId = parts[parts.length - 1];

    if (certificateId) {
        console.log(`Extracted Certificate ID: ${certificateId}`);
        // Redirect to the correct URL
        window.location.href = `/certificate/${certificateId}`;
    } else {
        alert("Could not extract a valid Certificate ID from the QR code.");
    }
}