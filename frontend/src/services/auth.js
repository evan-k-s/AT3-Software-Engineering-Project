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
}