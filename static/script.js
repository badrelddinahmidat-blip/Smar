// Smart Library JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Language switching functionality
    initializeLanguageSwitching();

    // File upload validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (16MB max)
                const maxSize = 16 * 1024 * 1024; // 16MB in bytes
                if (file.size > maxSize) {
                    alert('File size must be less than 16MB');
                    e.target.value = '';
                    return;
                }

                // Check file type
                if (file.type !== 'application/pdf') {
                    alert('Only PDF files are allowed');
                    e.target.value = '';
                    return;
                }

                // Show file info
                showFileInfo(file);
            }
        });
    }

    // Login form enhancement
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const firstName = document.getElementById('first_name').value.trim();
            const lastName = document.getElementById('last_name').value.trim();
            
            if (!firstName || !lastName) {
                e.preventDefault();
                alert('Please enter both first and last name');
                return;
            }
            
            // Show loading state
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Entering Library...';
            submitBtn.disabled = true;
        });
    }

    // Form validation for add book
    const addBookForm = document.getElementById('addBookForm');
    if (addBookForm) {
        addBookForm.addEventListener('submit', function(e) {
            const title = document.getElementById('title').value.trim();
            const author = document.getElementById('author').value.trim();
            const file = document.getElementById('file').files[0];

            if (!title || !author || !file) {
                e.preventDefault();
                alert('Please fill in all required fields and select a PDF file');
                return;
            }

            // Show loading state
            const submitBtn = addBookForm.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Adding Book...';
            submitBtn.disabled = true;
        });
    }

    // AI Search functionality
    const aiSearchForm = document.getElementById('aiSearchForm');
    if (aiSearchForm) {
        aiSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value.trim();
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            // Show loading spinner
            showLoadingSpinner();
            
            // Make AJAX request to AI search API
            fetch('/ai_search_api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                hideLoadingSpinner();
                
                if (data.success) {
                    displayAIResponse(data.query, data.response);
                } else {
                    showError(data.error || 'An error occurred');
                }
            })
            .catch(error => {
                hideLoadingSpinner();
                showError('Network error: ' + error.message);
            });
        });
    }

    // Search functionality enhancement
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        // Add search suggestions (basic implementation)
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            if (query.length > 2) {
                // Could implement AJAX search suggestions here
                highlightSearchTerms(query);
            }
        });
    }

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Show file information when file is selected
function showFileInfo(file) {
    const fileInfo = document.createElement('div');
    fileInfo.className = 'alert alert-info mt-2';
    fileInfo.innerHTML = `
        <i class="fas fa-file-pdf me-2"></i>
        <strong>Selected:</strong> ${file.name} 
        <span class="text-muted">(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
    `;
    
    const existingInfo = document.querySelector('.file-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    fileInfo.className += ' file-info';
    document.getElementById('file').parentNode.appendChild(fileInfo);
}

// Highlight search terms in results
function highlightSearchTerms(query) {
    const searchResults = document.querySelectorAll('.card-title, .card-subtitle');
    searchResults.forEach(element => {
        const text = element.textContent;
        const regex = new RegExp(`(${query})`, 'gi');
        element.innerHTML = text.replace(regex, '<mark>$1</mark>');
    });
}

// Confirm download action
function confirmDownload(bookTitle) {
    return confirm(`Are you sure you want to download "${bookTitle}"?`);
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Copy book link to clipboard
function copyBookLink(bookId) {
    const url = window.location.origin + '/book/' + bookId;
    navigator.clipboard.writeText(url).then(() => {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check me-2"></i>Book link copied to clipboard!
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }).catch(err => {
        console.error('Failed to copy link: ', err);
        alert('Failed to copy link to clipboard');
    });
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Enhanced search with debouncing
const debouncedSearch = debounce(function(query) {
    if (query.length > 2) {
        // Could implement live search here
        console.log('Searching for:', query);
    }
}, 300);

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.blur();
        }
    }
});

// AI Search Helper Functions
function showLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    const errorMsg = document.getElementById('errorMessage');
    if (spinner) spinner.style.display = 'block';
    if (errorMsg) errorMsg.style.display = 'none';
}

function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) spinner.style.display = 'none';
}

function showError(message) {
    const errorMsg = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    if (errorMsg && errorText) {
        errorText.textContent = message;
        errorMsg.style.display = 'block';
    }
}

function displayAIResponse(query, response) {
    // Create response HTML
    const responseHTML = `
        <div class="card shadow">
            <div class="card-header bg-success text-white">
                <h3 class="h5 mb-0">
                    <i class="fas fa-brain me-2"></i>AI Response
                </h3>
                <small class="text-light">Query: "${query}"</small>
            </div>
            
            <div class="card-body">
                <div class="ai-response">
                    ${response.replace(/\n/g, '<br>')}
                </div>
                
                <hr>
                
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Powered by OpenAI ChatGPT
                    </small>
                    <button class="btn btn-outline-primary btn-sm" onclick="copyResponse()">
                        <i class="fas fa-copy me-1"></i>Copy Response
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Insert response after the form
    const form = document.getElementById('aiSearchForm');
    if (form) {
        form.insertAdjacentHTML('afterend', responseHTML);
    }
}

function clearForm() {
    const queryField = document.getElementById('query');
    if (queryField) {
        queryField.value = '';
        queryField.focus();
    }
    
    // Remove any existing response
    const existingResponse = document.querySelector('.card.shadow');
    if (existingResponse && existingResponse.querySelector('.ai-response')) {
        existingResponse.remove();
    }
    
    // Hide error messages
    const errorMsg = document.getElementById('errorMessage');
    if (errorMsg) errorMsg.style.display = 'none';
}

function setQuery(query) {
    const queryField = document.getElementById('query');
    if (queryField) {
        queryField.value = query;
        queryField.focus();
    }
}

function copyResponse() {
    const responseElement = document.querySelector('.ai-response');
    if (responseElement) {
        const text = responseElement.textContent;
        navigator.clipboard.writeText(text).then(() => {
            // Show success message
            const toast = document.createElement('div');
            toast.className = 'toast align-items-center text-white bg-success border-0';
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-check me-2"></i>Response copied to clipboard!
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;
            
            document.body.appendChild(toast);
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove toast element after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        }).catch(err => {
            console.error('Failed to copy response: ', err);
            alert('Failed to copy response to clipboard');
        });
    }
}

// Language switching functionality
function initializeLanguageSwitching() {
    // Check if language preference is stored in localStorage
    const savedLanguage = localStorage.getItem('preferred_language');
    if (savedLanguage) {
        // Apply saved language preference
        applyLanguagePreference(savedLanguage);
    }
    
    // Add click handlers for language toggle buttons
    const languageLinks = document.querySelectorAll('a[href*="/set_language/"]');
    languageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const language = this.getAttribute('href').split('/').pop();
            switchLanguage(language);
        });
    });
}

function switchLanguage(language) {
    // Store language preference in localStorage
    localStorage.setItem('preferred_language', language);
    
    // Apply language preference immediately
    applyLanguagePreference(language);
    
    // Navigate to the language switch URL
    window.location.href = `/set_language/${language}`;
}

function applyLanguagePreference(language) {
    const body = document.body;
    
    // Remove existing language classes
    body.classList.remove('rtl', 'ltr');
    
    // Apply new language class
    if (language === 'ar') {
        body.classList.add('rtl');
        document.documentElement.setAttribute('dir', 'rtl');
        document.documentElement.setAttribute('lang', 'ar');
    } else {
        body.classList.add('ltr');
        document.documentElement.setAttribute('dir', 'ltr');
        document.documentElement.setAttribute('lang', 'en');
    }
}

// Enhanced language switching with smooth transitions
function switchLanguageWithTransition(language) {
    // Add transition class for smooth switching
    document.body.classList.add('language-transition');
    
    // Apply language preference
    applyLanguagePreference(language);
    
    // Remove transition class after animation
    setTimeout(() => {
        document.body.classList.remove('language-transition');
    }, 300);
}

// Language-specific utility functions
function getCurrentLanguage() {
    return localStorage.getItem('preferred_language') || 'ar';
}

function isRTL() {
    return getCurrentLanguage() === 'ar';
}

function isLTR() {
    return getCurrentLanguage() === 'en';
}

// RTL/LTR specific adjustments
function adjustLayoutForLanguage() {
    const isRTLMode = isRTL();
    
    // Adjust form inputs
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        if (isRTLMode) {
            control.style.textAlign = 'right';
        } else {
            control.style.textAlign = 'left';
        }
    });
    
    // Adjust card content
    const cardBodies = document.querySelectorAll('.card-body');
    cardBodies.forEach(card => {
        if (isRTLMode) {
            card.style.textAlign = 'right';
        } else {
            card.style.textAlign = 'left';
        }
    });
}
