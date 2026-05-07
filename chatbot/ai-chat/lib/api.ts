import axios from "axios";

const API_URL = "http://localhost:8000/chat";

export async function sendMessage(messages: any[]) {
    const response = await axios.post(API_URL, {
        messages
    });

    return response.data.response;
}