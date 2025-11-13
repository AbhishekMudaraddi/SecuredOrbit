// Dashboard JavaScript

let passwords = [];
let filteredPasswords = [];
let searchTerm = '';

function evaluatePasswordStrength(password) {
    let score = 0;

    if (!password || password.length === 0) {
        return { score: 0, label: 'Empty', color: '#ccc' };
    }

    const conditions = [
        password.length >= 8,
        password.length >= 12,
        /[a-z]/.test(password),
        /[A-Z]/.test(password),
        /[0-9]/.test(password),
        /[^A-Za-z0-9]/.test(password)
    ];

    conditions.forEach(condition => {
        if (condition) score += 1;
    });

    if (score > 5) score = 5;

    const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
    const colors = ['#dc3545', '#f66d44', '#f4b400', '#17a2b8', '#28a745', '#2ecc71'];

    return {
        score,
        label: labels[score],
        color: colors[score]
    };
}

function updateModalPasswordStrength(password) {
    const bar = document.getElementById('modal-password-strength-bar');
    const text = document.getElementById('modal-password-strength-text');

    if (!bar || !text) return;

    if (!password) {
        bar.style.width = '0%';
        bar.style.backgroundColor = '#ccc';
        text.textContent = 'Strength: -';
        return;
    }

    const strength = evaluatePasswordStrength(password);
    bar.style.width = `${(strength.score / 5) * 100}%`;
    bar.style.backgroundColor = strength.color;
    text.textContent = `Strength: ${strength.label}`;
}

// Load passwords automatically on page load
document.addEventListener('DOMContentLoaded', function() {
    loadPasswords();
    const searchInput = document.getElementById('password-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            searchTerm = e.target.value.trim().toLowerCase();
            renderPasswords();
        });
    }

    if (window.history && window.history.pushState) {
        const currentUrl = window.location.href;
        history.replaceState({ protectedView: true }, document.title, currentUrl);
        history.pushState({ protectedView: true }, document.title, currentUrl);
        window.addEventListener('popstate', handleProtectedBackNavigation);
    }

    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        updateModalPasswordStrength(passwordInput.value);
        passwordInput.addEventListener('input', function() {
            updateModalPasswordStrength(passwordInput.value);
        });
    }
});

// Load Passwords
async function loadPasswords() {
    const passwordsList = document.getElementById('passwords-list');
    
    try {
        passwordsList.innerHTML = '<div class="loading">Loading passwords...</div>';
        
        const response = await fetch('/api/passwords');
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load passwords');
        }
        
        const data = await response.json();
        passwords = data.passwords || [];
        filteredPasswords = passwords;

        const countEl = document.getElementById('password-count');
        if (countEl) {
            countEl.textContent = passwords.length;
        }
        
        if (passwords.length === 0) {
            passwordsList.innerHTML = `
                <div class="empty-state">
                    <h3>No passwords stored yet</h3>
                    <p>Click "Add New Password" to get started</p>
                </div>
            `;
        } else {
            renderPasswords();
        }
    } catch (error) {
        const countEl = document.getElementById('password-count');
        if (countEl) {
            countEl.textContent = '—';
        }
        passwordsList.innerHTML = `
            <div class="error-message">
                <h3>Error loading passwords</h3>
                <p>${escapeHtml(error.message)}</p>
                <button class="btn btn-primary" onclick="loadPasswords()">Retry</button>
            </div>
        `;
    }
}

// Render Passwords
function renderPasswords() {
    const passwordsList = document.getElementById('passwords-list');
    
    const items = (passwords || []).filter(entry => {
        if (!searchTerm) return true;
        const haystack = [
            entry.website,
            entry.username,
            entry.password,
            entry.notes
        ].join(' ').toLowerCase();
        return haystack.includes(searchTerm);
    });

    if (items.length === 0) {
        passwordsList.innerHTML = `
            <div class="empty-state">
                <h3>No matches found</h3>
                <p>Try adjusting your search terms.</p>
            </div>
        `;
        return;
    }

    passwordsList.innerHTML = items.map(password => `
        <div class="password-item" data-id="${password.id}">
            <div class="password-item-info">
                <h3>${escapeHtml(password.website)}</h3>
                ${password.username ? `<p><strong>Username:</strong> ${escapeHtml(password.username)}</p>` : ''}
                <p><strong>Password:</strong> 
                    <span class="password-value" id="pwd-${password.id}">••••••••</span>
                    <button class="btn-show-password btn-small" data-password="${encodeURIComponent(password.password || '')}" onclick="toggleShowPassword('${password.id}', this)">Show</button>
                </p>
                ${password.notes ? `<p><strong>Notes:</strong> ${escapeHtml(password.notes)}</p>` : ''}
            </div>
            <div class="password-item-actions">
                <button class="btn btn-edit btn-small" onclick="editPassword('${password.id}')">Edit</button>
                <button class="btn btn-danger btn-small" onclick="deletePassword('${password.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Toggle password visibility
function toggleShowPassword(id, button) {
    const pwdElement = document.getElementById(`pwd-${id}`);
    if (!pwdElement || !button) {
        return;
    }

    const password = decodeURIComponent(button.getAttribute('data-password') || '');

    if (pwdElement.textContent === '••••••••') {
        pwdElement.textContent = password;
        button.textContent = 'Hide';
    } else {
        pwdElement.textContent = '••••••••';
        button.textContent = 'Show';
    }
}

// Add Password Button
document.getElementById('add-password-btn').addEventListener('click', () => {
    openModal();
});

// Modal Functions
function openModal(passwordId = null) {
    const modal = document.getElementById('password-modal');
    const form = document.getElementById('password-form');
    const title = document.getElementById('modal-title');
    
    if (passwordId) {
        title.textContent = 'Edit Password';
        const password = passwords.find(p => p.id === passwordId);
        if (password) {
            document.getElementById('password-id').value = password.id;
            document.getElementById('website').value = password.website;
            document.getElementById('username').value = password.username || '';
            document.getElementById('password').value = password.password;
            document.getElementById('notes').value = password.notes || '';
        }
        updateModalPasswordStrength(document.getElementById('password').value);
    } else {
        title.textContent = 'Add Password';
        form.reset();
        document.getElementById('password-id').value = '';
        updateModalPasswordStrength('');
    }
    
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('password-modal');
    modal.style.display = 'none';
    document.getElementById('password-form').reset();
    updateModalPasswordStrength('');
}

document.getElementById('close-modal').addEventListener('click', closeModal);
document.getElementById('cancel-btn').addEventListener('click', closeModal);

// Password Form Submit
document.getElementById('password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const passwordId = document.getElementById('password-id').value;
    const data = {
        website: document.getElementById('website').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        notes: document.getElementById('notes').value
    };
    
    if (!data.website || !data.password) {
        alert('Website and password are required');
        return;
    }
    
    try {
        const url = passwordId ? `/api/passwords/${passwordId}` : '/api/passwords';
        const method = passwordId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save password');
        }
        
        closeModal();
        await loadPasswords();
        
        // Show success message
        showNotification('Password saved successfully!', 'success');
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
});

// Edit Password
function editPassword(passwordId) {
    openModal(passwordId);
}

// Delete Password
async function deletePassword(passwordId) {
    if (!confirm('Are you sure you want to delete this password?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/passwords/${passwordId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete password');
        }
        
        await loadPasswords();
        showNotification('Password deleted successfully!', 'success');
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type || ''}`;
    notification.textContent = message;

    document.body.appendChild(notification);
    requestAnimationFrame(() => notification.classList.add('visible'));

    setTimeout(() => {
        notification.classList.remove('visible');
        setTimeout(() => notification.remove(), 320);
    }, 3200);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
document.getElementById('password-modal').addEventListener('click', (e) => {
    if (e.target.id === 'password-modal') {
        closeModal();
    }
});

function handleProtectedBackNavigation(event) {
    if (!(event.state && event.state.protectedView)) {
        return;
    }

    const confirmLogout = window.confirm('Do you want to logout and leave the dashboard?');
    if (confirmLogout) {
        window.removeEventListener('popstate', handleProtectedBackNavigation);
        window.location.href = '/logout';
    } else {
        history.pushState({ protectedView: true }, document.title, window.location.href);
    }
}

// Add CSS animations
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
    
    .btn-show-password {
        margin-left: 10px;
        padding: 4px 8px;
        font-size: 12px;
    }
`;
document.head.appendChild(style);
