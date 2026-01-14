/**
 * Volunteer Signup Form Validator
 * Handles form validation for volunteer registration
 */

function VolunteerFormValidator() {
    const form = document.getElementById('volunteerForm');
    const submitBtn = document.getElementById('submitBtn');
    const ageInput = document.getElementById('id_age');
    const opportunitySelect = document.getElementById('id_opportunity');

    if (!form) return null;

    // Age validation with visual feedback
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            const age = parseInt(this.value);
            this.classList.remove('is-invalid', 'is-valid');

            if (this.value && age < 18) {
                this.classList.add('is-invalid');
                let errorDiv = this.parentNode.querySelector('.age-error');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback d-block age-error';
                    errorDiv.textContent = 'You must be at least 18 years old to volunteer.';
                    this.parentNode.appendChild(errorDiv);
                }
            } else if (this.value && age >= 18) {
                this.classList.add('is-valid');
                const errorDiv = this.parentNode.querySelector('.age-error');
                if (errorDiv) errorDiv.remove();
            }
        });
    }

    // Opportunity preview
    if (opportunitySelect) {
        opportunitySelect.addEventListener('change', function() {
            const preview = document.getElementById('opportunityPreview');
            const selectedOption = this.options[this.selectedIndex];

            if (this.value && selectedOption.text !== '---------') {
                preview.classList.remove('d-none');
                document.getElementById('previewTitle').textContent = selectedOption.text.split(' - ')[0];
            } else {
                preview.classList.add('d-none');
            }
        });
    }

    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const fields = {
            'name': 'Name is required.',
            'age': 'Age is required.',
            'expertise': 'Please describe your expertise.',
            'opportunity': 'Please select an opportunity.'
        };

        // Clear previous validation states
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.validation-error').forEach(el => el.remove());

        for (const [fieldName, errorMsg] of Object.entries(fields)) {
            const field = document.getElementById('id_' + fieldName);
            if (field && !field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');

                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback d-block validation-error';
                errorDiv.textContent = errorMsg;
                field.parentNode.appendChild(errorDiv);
            }
        }

        // Check age requirement
        if (ageInput && ageInput.value) {
            const age = parseInt(ageInput.value);
            if (age < 18) {
                isValid = false;
                ageInput.classList.add('is-invalid');
            }
        }

        if (!isValid) {
            e.preventDefault();
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        } else {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Signing Up...';
        }
    });

    // Real-time validation feedback
    ['name', 'expertise', 'opportunity'].forEach(fieldName => {
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
        }
    });

    return null;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const root = ReactDOM.createRoot(document.createElement('div'));
    root.render(<VolunteerFormValidator />);
});