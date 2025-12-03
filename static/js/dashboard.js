// Dashboard JavaScript
let passwords = [];

// Load passwords when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadPasswords();
    
    // Modal event listeners
    document.getElementById('add-password-btn').addEventListener('click', openModal);
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-btn').addEventListener('click', closeModal);
    
    // Form submit
    document.getElementById('password-form').addEventListener('submit', handleFormSubmit);
    
    // Close modal on outside click
    document.getElementById('password-modal').addEventListener('click', function(e) {
        if (e.target.id === 'password-modal') {
            closeModal();
        }
    });
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
    
    passwordsList.innerHTML = passwords.map(password => `
        <div class="password-item">
            <div class="password-item-info">
                <h3>${escapeHtml(password.website)}</h3>
                ${password.username ? `<p><strong>Username:</strong> ${escapeHtml(password.username)}</p>` : ''}
                <p><strong>Password:</strong> 
                    <span class="password-value" id="pwd-${password.id}">••••••••</span>
                    <button class="btn-show-password" onclick="togglePassword('${password.id}', '${escapeHtml(password.password)}')">Show</button>
                </p>
                ${password.notes ? `<p><strong>Notes:</strong> ${escapeHtml(password.notes)}</p>` : ''}
            </div>
            <div class="password-item-actions">
                <button class="btn btn-primary btn-small" onclick="editPassword('${password.id}')">Edit</button>
                <button class="btn btn-danger btn-small" onclick="deletePassword('${password.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Toggle Password Visibility
function togglePassword(id, password) {
    const pwdElement = document.getElementById(`pwd-${id}`);
    const button = event.target;
    
    if (pwdElement.textContent === '••••••••') {
        pwdElement.textContent = password;
        button.textContent = 'Hide';
    } else {
        pwdElement.textContent = '••••••••';
        button.textContent = 'Show';
    }
}

// Open Modal
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
    } else {
        title.textContent = 'Add Password';
        form.reset();
        document.getElementById('password-id').value = '';
    }
    
    modal.style.display = 'flex';
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('password-modal');
    modal.style.display = 'none';
    document.getElementById('password-form').reset();
}

// Handle Form Submit
async function handleFormSubmit(e) {
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
        alert('Password saved successfully!');
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

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
        alert('Password deleted successfully!');
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

