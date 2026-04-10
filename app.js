const themeToggle = document.getElementById('themeToggle');
const root = document.documentElement;

function updateTheme(mode) {
    if (mode === 'dark') {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
        themeToggle.textContent = 'Light';
    } else {
        document.body.classList.add('light-mode');
        document.body.classList.remove('dark-mode');
        themeToggle.textContent = 'Dark';
    }
}

if (themeToggle) {
    const preferred = localStorage.getItem('study-theme') || 'light';
    updateTheme(preferred);

    themeToggle.addEventListener('click', () => {
        const nextTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        updateTheme(nextTheme);
        localStorage.setItem('study-theme', nextTheme);
    });
}
