import axios from "axios";

const API_URL = "https://portentously-glamorous-leafroller.cloudpub.ru/chat";

export async function sendMessage(messages: any[]) {
    const response = await axios.post(API_URL, {
        messages
    });

    return response.data.response;
}