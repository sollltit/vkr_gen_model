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

    // setMessages теперь умеет:
    // 1. принимать массив
    // 2. принимать callback(prev => ...)
    setMessages: any;

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

        // =========================
        // STATE
        // =========================
        messages: [],


        // =========================
        // SET MESSAGES
        // =========================
        setMessages: (messages: any) => {

            // Если передали функцию:
            // setMessages(prev => ...)
            if (typeof messages === "function") {

                set((state) => ({

                    messages: messages(
                        state.messages
                    )
                }));

            }

            // Если передали массив:
            // setMessages([...])
            else {

                set({
                    messages
                });
            }
        },


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
        // CLEAR MESSAGES
        // =========================
        clearMessages: () =>

            set({
                messages: []
            })
    }));