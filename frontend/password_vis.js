const passVis = document.getElementById('pass-vis');
const password = document.getElementById('password');
const confirmPassVis = document.getElementById('confirm-pass-vis');
const confirmPassword = document.getElementById('confirm-password')

passVis.addEventListener('click', () => {
    passVis.classList.toggle('visible');
    if (password.getAttribute('type') == 'password') {
        password.setAttribute('type', 'text');
    } else {
        password.setAttribute('type', 'password');
    };
});

confirmPassVis.addEventListener('click', () => {
    confirmPassVis.classList.toggle('visible');
    if (confirmPassword.getAttribute('type') == 'password') {
        confirmPassword.setAttribute('type', 'text');
    } else {
        confirmPassword.setAttribute('type', 'password');
    };
})