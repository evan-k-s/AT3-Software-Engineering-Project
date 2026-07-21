import { requestBackend } from "../services/api.js";

const themeSwitch = document.getElementById('theme-switch');

themeSwitch.addEventListener('click', async () => {
    let darkmode = false;

    document.body.classList.toggle('darkmode');

    if (document.body.classList.contains('darkmode')) {
        darkmode = true;
    } else {
        darkmode = false;
    }

    try {
        const tokens = {
            sessionToken: sessionStorage.getItem("session_token"),
            csrfToken: sessionStorage.getItem("csrf_token"),
        };
        const body = { darkmode };

        const response = await requestBackend("POST", "toggle-darkmode", tokens, body, null);
    } catch (error) {
        alert(error);
        console.error(error);
    }
})