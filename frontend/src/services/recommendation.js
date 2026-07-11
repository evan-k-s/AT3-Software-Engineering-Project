import { requestBackend } from "./api.js";


window.saveRecommendation = async (recommendation_id) => {
    try {
        const tokens = {
            sessionToken: sessionStorage.getItem("session_token"),
            csrfToken: sessionStorage.getItem("csrf_token"),
        };
        const body = { recommendation_id };

        const response = await requestBackend("POST", "save-recommendation", tokens, body, null);

        window.location.reload();
    } catch (error) {
        alert(error);
        console.error(error);
    }
};