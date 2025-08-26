document.getElementById('job-filter-btn').addEventListener('click', function() {
    const query = document.getElementById('job-search').value.toLowerCase();
    const location = document.getElementById('job-location').value.toLowerCase();
    const jobs = document.querySelectorAll('.job-card-wrapper');

    jobs.forEach(job => {
        const title = job.querySelector('h4')?.innerText.toLowerCase() || '';
        let jobLoc = '';
        let skills = '';

        // Find all <p> inside this job card
        job.querySelectorAll('p').forEach(p => {
            const text = p.innerText.toLowerCase();
            if (text.startsWith('location:')) jobLoc = text;
            if (text.startsWith('skills:')) skills = text;
        });

        // Show job if title OR skills match query AND location matches
        if ((title.includes(query) || skills.includes(query)) && jobLoc.includes(location)) {
            job.style.display = '';
        } else {
            job.style.display = 'none';
        }
    });
});

// Optional: live filter as user types
document.getElementById('job-search').addEventListener('input', () => {
    document.getElementById('job-filter-btn').click();
});
document.getElementById('job-location').addEventListener('input', () => {
    document.getElementById('job-filter-btn').click();
});
