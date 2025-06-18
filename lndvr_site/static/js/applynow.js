document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    const nextButtons = document.querySelectorAll('.next-btn');
    const backButtons = document.querySelectorAll('.back-btn');

    // Month number extraction logic
    const startDateInput = document.getElementById('startdate');
    const monthNumberInput = document.getElementById('month_number');

    if (startDateInput && monthNumberInput) {
        startDateInput.addEventListener('change', function () {
            const value = this.value; // e.g., "2025-06"
            const monthNumber = value.split('-')[1]; // Extract "06"
            monthNumberInput.value = monthNumber;
        });
    }

    nextButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentTab = getCurrentTab();
            const currentTabContent = document.getElementById(currentTab);

            if (validateTab(currentTabContent)) {
                if (currentTab === 'business') switchTab('ownership');
                else if (currentTab === 'ownership') switchTab('financial');
            }
        });
    });

    backButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const currentTab = getCurrentTab();
            if (currentTab === 'financial') switchTab('ownership');
            else if (currentTab === 'ownership') switchTab('business');
        });
    });

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            const currentTab = getCurrentTab();
            const currentTabContent = document.getElementById(currentTab);

            if (tabId !== currentTab && validateTab(currentTabContent)) {
                switchTab(tabId);
            }
        });
    });

    function getCurrentTab() {
        for (const content of tabContents) {
            if (content.style.display !== 'none') return content.id;
        }
        return null;
    }

    function switchTab(tabId) {
        tabContents.forEach(content => content.style.display = 'none');
        tabButtons.forEach(btn => btn.classList.remove('active'));

        document.getElementById(tabId).style.display = 'block';
        document.querySelector(`.tab-button[data-tab="${tabId}"]`).classList.add('active');
    }

    function validateTab(tabContent) {
        const inputs = tabContent.querySelectorAll('input, select, textarea');
        for (const input of inputs) {
            if (input.offsetParent !== null && !input.checkValidity()) {
                input.reportValidity();
                input.focus();
                return false;
            }
        }
        return true;
    }
});
