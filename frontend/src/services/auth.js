import { requestBackend } from "./api.js";


export const authLogin = async (username, password) => {
    const body = { username, password };
    const response = await requestBackend("POST", "login", null, body, null);

    if (response.error) {
        throw new Error(response.error);
    }
    sessionStorage.setItem("session_token", response.session_token);
    sessionStorage.setItem("csrf_token", response.csrf_token);
    sessionStorage.setItem("owner", username);

    return response;
};


export const authRegister = async (email, password, username) => {
    const body = { email, password, username };
    const response = await requestBackend("POST", "register", null, body, null);

    if (response.error) {
        throw new Error(response.error);
    }
    sessionStorage.setItem("session_token", response.session_token);
    sessionStorage.setItem("csrf_token", response.csrf_token);
    sessionStorage.setItem("owner", username);

    return response;
};

export const authLogout = async () => {
    const tokens = {
        sessionToken: sessionStorage.getItem("session_token"),
        csrfToken: sessionStorage.getItem("csrf_token"),
    }
    const ownerUsername = sessionStorage.getItem("owner");

    if (!tokens || !ownerUsername) {
        throw new Error("Cannot logout: no tokens or username not found");
    }

    const response = await requestBackend("POST", "logout", tokens, null, null);
    if (response.error) {
        throw new Error(response.error)
    }

    sessionStorage.removeItem("session_token");
    sessionStorage.removeItem("owner");
}