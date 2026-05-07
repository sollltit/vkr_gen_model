import { create } from "zustand";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatState {
    messages: Message[];

    addMessage: (msg: Message) => void;

    setMessages: (messages: Message[]) => void;

    clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
    messages: [],

    addMessage: (msg) =>
        set((state) => ({
            messages: [...state.messages, msg]
        })),

    setMessages: (messages) =>
        set(() => ({
            messages
        })),

    clearChat: () =>
        set(() => ({
            messages: []
        }))
}));