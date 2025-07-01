document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        const action = e.submitter.value;
        if (action === 'update') {
            if (!confirm("Are you sure you want to update this job?")) {
                e.preventDefault();
            }
        } else if (action === 'delete') {
            if (!confirm("Are you sure you want to delete this job? This action cannot be undone.")) {
                e.preventDefault();
            }
        }
    });
});

