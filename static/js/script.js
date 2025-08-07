// Global variables
let selectedFile = null;
let currentConversionId = null;
let conversionType = 'pdf_to_word';
let statusCheckInterval = null;

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const convertBtn = document.getElementById('convertBtn');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Conversion type buttons
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            setConversionType(btn.dataset.type);
        });
    });
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processSelectedFile(file);
    }
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

// Handle drop
function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processSelectedFile(files[0]);
    }
}

// Process selected file
function processSelectedFile(file) {
    // Validate file type
    const allowedExtensions = conversionType === 'pdf_to_word' ? ['pdf'] : ['docx', 'doc'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        showError(`Please select a ${allowedExtensions.join(' or ').toUpperCase()} file for ${conversionType === 'pdf_to_word' ? 'PDF to Word' : 'Word to PDF'} conversion.`);
        return;
    }
    
    // Validate file size (100MB limit)
    if (file.size > 100 * 1024 * 1024) {
        showError('File size must be less than 100MB.');
        return;
    }
    
    selectedFile = file;
    displayFileInfo(file);
    convertBtn.disabled = false;
}

// Display file information
function displayFileInfo(file) {
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Remove selected file
function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    convertBtn.disabled = true;
}

// Set conversion type
function setConversionType(type) {
    conversionType = type;
    
    // Update button states
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-type="${type}"]`).classList.add('active');
    
    // Update file type text
    const fileTypeText = document.getElementById('fileTypeText');
    if (type === 'pdf_to_word') {
        fileTypeText.textContent = 'Select a PDF file to convert to Word';
        fileInput.accept = '.pdf';
    } else {
        fileTypeText.textContent = 'Select a Word file to convert to PDF';
        fileInput.accept = '.docx,.doc';
    }
    
    // Clear any selected file if it doesn't match the new type
    if (selectedFile) {
        const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
        const allowedExtensions = type === 'pdf_to_word' ? ['pdf'] : ['docx', 'doc'];
        
        if (!allowedExtensions.includes(fileExtension)) {
            removeFile();
        }
    }
}

// Start conversion
async function startConversion() {
    if (!selectedFile) {
        showError('Please select a file first.');
        return;
    }
    
    try {
        // Show progress section
        showProgressSection();
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('conversion_type', conversionType);
        
        // Upload file
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentConversionId = result.conversion_id;
            startStatusChecking();
        } else {
            throw new Error(result.error || 'Upload failed');
        }
        
    } catch (error) {
        console.error('Conversion error:', error);
        showError(error.message || 'Failed to start conversion');
        hideProgressSection();
    }
}

// Show progress section
function showProgressSection() {
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Animate progress bar
    const progressFill = document.getElementById('progressFill');
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
    }, 500);
    
    // Store interval for cleanup
    progressSection.dataset.progressInterval = interval;
}

// Hide progress section
function hideProgressSection() {
    progressSection.style.display = 'none';
    
    // Clear progress animation
    const interval = progressSection.dataset.progressInterval;
    if (interval) {
        clearInterval(interval);
        delete progressSection.dataset.progressInterval;
    }
}

// Start status checking
function startStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(checkConversionStatus, 2000);
}

// Check conversion status
async function checkConversionStatus() {
    if (!currentConversionId) return;
    
    try {
        const response = await fetch(`/status/${currentConversionId}`);
        const result = await response.json();
        
        if (response.ok) {
            updateProgressStatus(result.status);
            
            if (result.status === 'completed') {
                clearInterval(statusCheckInterval);
                statusCheckInterval = null;
                showSuccessResult();
            } else if (result.status === 'failed') {
                clearInterval(statusCheckInterval);
                statusCheckInterval = null;
                showError(result.error_message || 'Conversion failed');
            }
        } else {
            throw new Error(result.error || 'Status check failed');
        }
        
    } catch (error) {
        console.error('Status check error:', error);
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
        showError('Failed to check conversion status');
    }
}

// Update progress status
function updateProgressStatus(status) {
    const progressStatus = document.getElementById('progressStatus');
    const progressText = document.getElementById('progressText');
    
    progressStatus.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    
    switch (status) {
        case 'pending':
            progressText.textContent = 'File uploaded, waiting to start conversion...';
            break;
        case 'processing':
            progressText.textContent = 'Converting your file with LibreOffice...';
            break;
        case 'completed':
            progressText.textContent = 'Conversion completed successfully!';
            break;
        case 'failed':
            progressText.textContent = 'Conversion failed. Please try again.';
            break;
    }
}

// Show success result
function showSuccessResult() {
    hideProgressSection();
    resultsSection.style.display = 'block';
    errorSection.style.display = 'none';
    
    // Complete progress bar
    const progressFill = document.getElementById('progressFill');
    progressFill.style.width = '100%';
}

// Show error
function showError(message) {
    hideProgressSection();
    errorSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    document.getElementById('errorMessage').textContent = message;
}

// Download converted file
function downloadFile() {
    if (!currentConversionId) {
        showError('No file to download');
        return;
    }
    
    window.open(`/download/${currentConversionId}`, '_blank');
}

// Reset form
function resetForm() {
    removeFile();
    hideProgressSection();
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    currentConversionId = null;
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

// Utility function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        background: ${type === 'error' ? '#ff4757' : type === 'success' ? '#38a169' : '#667eea'};
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 