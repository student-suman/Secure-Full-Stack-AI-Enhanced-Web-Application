// Main JavaScript file for Certificate Verification System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Certificate ID formatter
    const certIdInputs = document.querySelectorAll('input[name="certificate_id"]');
    certIdInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-F0-9]/g, '');
        });
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        }).catch(function() {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('Copied to clipboard!', 'success');
        });
    };

    // Show toast notifications
    window.showToast = function(message, type = 'info') {
        const toastContainer = getOrCreateToastContainer();
        const toastEl = createToast(message, type);
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    };

    function getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1080';
            document.body.appendChild(container);
        }
        return container;
    }

    function createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        
        const iconMap = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info'
        };
        
        const icon = iconMap[type] || iconMap['info'];
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${icon} me-2"></i>
                <strong class="me-auto">Certificate System</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        return toast;
    }

    // Hash display formatting
    const hashElements = document.querySelectorAll('.hash-display');
    hashElements.forEach(function(element) {
        const fullHash = element.dataset.hash;
        if (fullHash && fullHash.length > 20) {
            element.innerHTML = `
                <span class="hash-short">${fullHash.substring(0, 20)}...</span>
                <button class="btn btn-link btn-sm p-0 ms-1" onclick="toggleHash(this)" data-full-hash="${fullHash}">
                    <i class="fas fa-eye"></i>
                </button>
            `;
        }
    });

    window.toggleHash = function(button) {
        const hashShort = button.parentElement.querySelector('.hash-short');
        const fullHash = button.dataset.fullHash;
        const icon = button.querySelector('i');
        
        if (hashShort.textContent.includes('...')) {
            hashShort.textContent = fullHash;
            icon.className = 'fas fa-eye-slash';
        } else {
            hashShort.textContent = fullHash.substring(0, 20) + '...';
            icon.className = 'fas fa-eye';
        }
    };

    // File size formatter
    window.formatFileSize = function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Search functionality for tables
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const table = document.querySelector(this.dataset.target);
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });

    // Auto-refresh functionality for dashboards
    if (document.querySelector('.dashboard-auto-refresh')) {
        setInterval(function() {
            const refreshElements = document.querySelectorAll('[data-auto-refresh]');
            refreshElements.forEach(function(element) {
                const url = element.dataset.autoRefresh;
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        // Update specific elements based on data
                        updateDashboardStats(data);
                    })
                    .catch(error => console.log('Auto-refresh failed:', error));
            });
        }, 30000); // Refresh every 30 seconds
    }

    function updateDashboardStats(data) {
        // Update statistics cards if they exist
        const statsElements = document.querySelectorAll('[data-stat]');
        statsElements.forEach(function(element) {
            const statType = element.dataset.stat;
            if (data[statType] !== undefined) {
                element.textContent = data[statType];
            }
        });
    }

    // Loading state management
    window.showLoading = function(element, text = 'Loading...') {
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            ${text}
        `;
        element.disabled = true;
    };

    window.hideLoading = function(element) {
        const originalContent = element.dataset.originalContent;
        if (originalContent) {
            element.innerHTML = originalContent;
            delete element.dataset.originalContent;
        }
        element.disabled = false;
    };

    // Certificate ID validation
    window.validateCertificateId = function(id) {
        const regex = /^[A-F0-9]{32}$/;
        return regex.test(id);
    };

    // Mobile responsive table handling
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(function(table) {
        if (window.innerWidth < 768) {
            // Add mobile-friendly classes or modifications
            table.classList.add('table-sm');
        }
    });

    // Print functionality
    window.printCertificate = function() {
        window.print();
    };

    // Initialize any additional components
    initializeAdditionalComponents();
});

function initializeAdditionalComponents() {
    // Initialize date pickers if available
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Set max date to today for issue dates
        if (input.name === 'issue_date') {
            input.max = new Date().toISOString().split('T')[0];
        }
    });

    // Initialize progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.dataset.width || '0';
        setTimeout(function() {
            bar.style.width = width + '%';
        }, 100);
    });
}

// Export functions for use in other scripts
window.CertVerify = {
    copyToClipboard: window.copyToClipboard,
    showToast: window.showToast,
    formatFileSize: window.formatFileSize,
    validateCertificateId: window.validateCertificateId,
    showLoading: window.showLoading,
    hideLoading: window.hideLoading
};
