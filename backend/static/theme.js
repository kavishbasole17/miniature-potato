
function toggleTheme() {
    let theme = localStorage.getItem('soa-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('soa-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
}
document.addEventListener("DOMContentLoaded", () => {
    let theme = localStorage.getItem('soa-theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
});
