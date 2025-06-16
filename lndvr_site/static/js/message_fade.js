
// Automatically hide alert after 4 seconds
setTimeout(function () {
    const alert = document.getElementById("auto-dismiss-alert");
    if (alert) {
        // Bootstrap fade out (optional smooth transition)
        alert.classList.remove("show");
        alert.classList.add("fade");
        setTimeout(() => alert.remove(), 500); // Remove from DOM after fade
    }
}, 2000); // 2000 ms = 2 seconds
