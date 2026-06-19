import { requestBackend } from "./api.js";


window.deleteReview = async (review_id) => {
    console.log("working");
    try {
        const tokens = {
            sessionToken: sessionStorage.getItem("session_token"),
            csrfToken: sessionStorage.getItem("csrf_token"),
        };
        const body = { review_id };

        const response = await requestBackend("POST", "delete-review", tokens, body, null);

        window.location.reload();
    } catch (error) {
        alert(error);
        console.error(error);
    }
};