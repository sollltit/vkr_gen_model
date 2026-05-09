import { create } from "zustand";


// =========================
// TYPES
// =========================
export interface Message {

    id: number;

    role: "user" | "assistant";

    content: string;
}


interface MessageStore {

    messages: Message[];

    setMessages: (
        messages: Message[]
    ) => void;

    addMessage: (
        message: Message
    ) => void;

    clearMessages: () => void;
}


// =========================
// STORE
// =========================
export const useMessageStore =
    create<MessageStore>((set) => ({

        messages: [],


        // =========================
        // SET MESSAGES
        // =========================
        setMessages: (messages) =>

            set({
                messages
            }),


        // =========================
        // ADD MESSAGE
        // =========================
        addMessage: (message) =>

            set((state) => ({

                messages: [
                    ...state.messages,
                    message
                ]
            })),


        // =========================
        // CLEAR
        // =========================
        clearMessages: () =>

            set({
                messages: []
            })

    }));