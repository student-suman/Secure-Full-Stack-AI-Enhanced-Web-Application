// In static/js/ai_scanner.js

document.addEventListener('DOMContentLoaded', function () {
    const scanButton = document.getElementById('scan-ai-button');
    const fileInput = document.getElementById('certificate_file');
    const spinner = document.getElementById('ai-spinner');

    scanButton.addEventListener('click', function () {
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a certificate file first.');
            return;
        }

        // Show loading state
        spinner.classList.remove('d-none');
        scanButton.disabled = true;

        const formData = new FormData();
        formData.append('certificate_file', file);

        // Send the file to our backend's AI scanner endpoint
        fetch('/scan_certificate', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert('AI Error: ' + data.error);
                return;
            }

            // AI successful! Populate the form fields.
            document.getElementById('title').value = data.title || '';
            document.getElementById('institution').value = data.institution || '';
            document.getElementById('student_name').value = data.student_name || '';
            document.getElementById('issue_date').value = data.issue_date || '';
            
            alert('Form has been auto-filled by AI. Please review and add the student email.');
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            alert('An error occurred while scanning the certificate. Please try again.');
        })
        .finally(() => {
            // Hide loading state
            spinner.classList.add('d-none');
            scanButton.disabled = false;
        });
    });
});