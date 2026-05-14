import { create } from "zustand";


// =========================
// TYPES
// =========================
export interface Message {

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

    updateLastMessage: (
        content: string
    ) => void;
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
            }),


        // =========================
        // STREAM UPDATE
        // =========================
        updateLastMessage: (content) =>

            set((state) => {

                const updated = [
                    ...state.messages
                ];

                if (
                    updated.length === 0
                ) {
                    return {
                        messages: []
                    };
                }

                updated[
                    updated.length - 1
                ] = {

                    ...updated[
                        updated.length - 1
                    ],

                    content
                };

                return {
                    messages: updated
                };
            })
    }));