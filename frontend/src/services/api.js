export const BACKEND_PORT = 5000;
export const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

export const requestBackend = async (method, route, tokens, payload, query) => {
    let url = `${BACKEND_URL}/${route}`;
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
    };

    if (query) {
        url += `?${query}`;
    };

    if (tokens) {
        options.headers.Authorization = tokens.sessionToken;
        options.headers['X-CSRF-Token'] = tokens.csrfToken;
    };

    if (payload) {
        options.body = JSON.stringify(payload);
    };

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        return response.json()
    } catch (error) {
        console.error("Error", error);
        throw new Error(error.message);
    }
}