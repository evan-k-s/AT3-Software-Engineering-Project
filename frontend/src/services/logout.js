import { authLogout } from "./auth.js";

document.getElementById("logout").addEventListener('click', async function(event) {
    event.preventDefault();
    try {
        await authLogout();
        window.location.href = "/login";
    } catch (error) {
        console.error(error.message);
    }
});