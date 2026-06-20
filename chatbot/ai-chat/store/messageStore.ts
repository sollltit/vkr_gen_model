import { create } from "zustand";


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


export const useMessageStore =
    create<MessageStore>((set) => ({

        messages: [],


        setMessages: (messages) =>

            set({
                messages
            }),


        addMessage: (message) =>

            set((state) => ({

                messages: [
                    ...state.messages,
                    message
                ]
            })),


        clearMessages: () =>

            set({
                messages: []
            }),

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