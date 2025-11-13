// Main JavaScript file
// Utility functions

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    return errorDiv;
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    return successDiv;
}

function togglePasswordVisibility(inputId, trigger) {
    const input = document.getElementById(inputId);
    const control = trigger || (typeof event !== 'undefined' ? event.target : null);

    if (!input || !control) {
        return;
    }

    if (input.type === 'password') {
        input.type = 'text';
        control.textContent = 'Hide';
    } else {
        input.type = 'password';
        control.textContent = 'Show';
    }
}

// Reveal-on-scroll animations
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('[data-animate]');
    if (!('IntersectionObserver' in window) || animatedElements.length === 0) {
        animatedElements.forEach(el => el.classList.add('is-visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    animatedElements.forEach(el => observer.observe(el));
});

