const themeSwitch = document.getElementById('theme-switch');

themeSwitch.addEventListener('click', () => {
    document.body.classList.toggle('darkmode');
})