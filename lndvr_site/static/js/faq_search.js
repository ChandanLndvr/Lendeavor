// Toggle FAQ answer visibility
    document.querySelectorAll('.faq-question').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            const answer = btn.nextElementSibling;
            answer.style.display = answer.style.display === 'block' ? 'none' : 'block';
        });
    });

    // Search filter functionality
    document.getElementById('faqSearch').addEventListener('input', function () {
        const query = this.value.toLowerCase();
        const faqSections = document.querySelectorAll('.faq-questions-card .faq-section');

        faqSections.forEach(section => {
            let anyVisible = false;
            section.querySelectorAll('.faq-block').forEach(faq => {
                const question = faq.querySelector('.faq-question').textContent.toLowerCase();
                const answer = faq.querySelector('.faq-answer').textContent.toLowerCase();

                if (question.includes(query) || answer.includes(query)) {
                    faq.style.display = '';
                    anyVisible = true;
                } else {
                    faq.style.display = 'none';
                }
            });
            section.style.display = anyVisible ? '' : 'none';
        });
    });