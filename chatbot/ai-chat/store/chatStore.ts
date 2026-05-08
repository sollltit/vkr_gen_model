import { create } from "zustand";

import { persist } from "zustand/middleware";

import { v4 as uuidv4 } from "uuid";

export interface Message {
    role: "user" | "assistant";
    content: string;
}

export interface Chat {
    id: string;
    title: string;
    messages: Message[];
}

interface ChatState {

    chats: Chat[];

    currentChatId: string;

    createChat: () => void;

    setCurrentChat: (id: string) => void;

    addMessage: (message: Message) => void;
}

const initialChat = {
    id: uuidv4(),
    title: "Новый чат",
    messages: []
};

export const useChatStore = create<ChatState>()(

    persist(

        (set, get) => ({

            chats: [initialChat],

            currentChatId: initialChat.id,

            createChat: () => {

                const newChat = {
                    id: uuidv4(),
                    title: "Новый чат",
                    messages: []
                };

                set((state) => ({
                    chats: [newChat, ...state.chats],
                    currentChatId: newChat.id
                }));
            },

            setCurrentChat: (id) => {
                set(() => ({
                    currentChatId: id
                }));
            },

            addMessage: (message) => {

                const {
                    chats,
                    currentChatId
                } = get();

                const updatedChats = chats.map((chat) => {

                    if (chat.id === currentChatId) {

                        return {
                            ...chat,
                            messages: [
                                ...chat.messages,
                                message
                            ]
                        };
                    }

                    return chat;
                });

                set(() => ({
                    chats: updatedChats
                }));
            }

        }),

        {
            name: "ai-chat-storage"
        }

    )

);