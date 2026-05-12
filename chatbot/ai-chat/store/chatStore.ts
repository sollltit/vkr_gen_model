import { create } from "zustand";


export interface Chat {

    id: number;

    title: string;
}


interface ChatStore {

    chats: Chat[];

    currentChatId: number | null;

    setChats: (
        chats: Chat[]
    ) => void;

    setCurrentChat: (
        id: number | null
    ) => void;
}


export const useChatStore =
    create<ChatStore>((set) => ({

        chats: [],

        currentChatId: null,


        setChats: (chats) =>

        set({
            chats: Array.isArray(chats)
                ? chats
                : []
        }),


        setCurrentChat: (id) =>

            set({
                currentChatId: id
            })

    }));