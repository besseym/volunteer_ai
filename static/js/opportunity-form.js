/**
 * Opportunity Form Validator
 * Handles form validation for creating/editing volunteer opportunities
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('opportunityForm');
    const submitBtn = document.getElementById('submitBtn');

    if (!form) return;

    form.addEventListener('submit', function(e) {
        let isValid = true;
        const requiredFields = ['title', 'category', 'date', 'description'];

        // Clear previous validation states
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.validation-error').forEach(el => el.remove());

        requiredFields.forEach(fieldName => {
            const field = document.getElementById('id_' + fieldName);
            if (field && !field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');

                // Add error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback d-block validation-error';
                errorDiv.textContent = 'This field is required.';
                field.parentNode.appendChild(errorDiv);
            }
        });

        if (!isValid) {
            e.preventDefault();
            // Scroll to first error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        } else {
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';
        }
    });

    // Real-time validation
    ['title', 'category', 'date', 'description'].forEach(fieldName => {
        const field = document.getElementById('id_' + fieldName);
        if (field) {
            field.addEventListener('blur', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    const error = this.parentNode.querySelector('.validation-error');
                    if (error) error.remove();
                }
            });

            field.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    const error = this.parentNode.querySelector('.validation-error');
                    if (error) error.remove();
                }
            });
        }
    });
});