"use client";

import { useEffect, useState } from "react";

import {
    MessageSquarePlus,
    Trash2
} from "lucide-react";

import { useRouter } from "next/navigation";

import { useChatStore } from "@/store/chatStore";
import { useAuthStore } from "@/store/authStore";
import { useMessageStore } from "@/store/messageStore";


export default function Sidebar() {

    const router = useRouter();

    const [search, setSearch] = useState("");

    const user = useAuthStore(
        (state) => state.user
    );

    const logout = useAuthStore(
        (state) => state.logout
    );

    const {
        chats,
        currentChatId,
        setCurrentChat,
        setChats
    } = useChatStore();

    const clearMessages = useMessageStore(
        (state) => state.clearMessages
    );


    useEffect(() => {

        async function loadChats() {

            if (!user) return;

            try {

                const response = await fetch(
                    `https://tunelessly-snappy-goldeneye.cloudpub.ru/chats/${user.user_id}`
                );

                const data = await response.json();

                setChats(
                    Array.isArray(data.chats)
                        ? data.chats
                        : []
                );

            } catch (error) {

                console.error(error);
            }
        }

        loadChats();

    }, [user]);


    useEffect(() => {

        async function searchChats() {

            if (!user) return;

            if (!search.trim()) {

                const response = await fetch(
                    `https://tunelessly-snappy-goldeneye.cloudpub.ru/chats/${user.user_id}`
                );

                const data = await response.json();

                setChats(data.chats || []);

                return;
            }

            try {

                const response = await fetch(
                    `https://tunelessly-snappy-goldeneye.cloudpub.ru/search_chats/${user.user_id}?query=${search}`
                );

                const data = await response.json();

                setChats(data.chats || []);

            } catch (error) {

                console.error(error);
            }
        }

        const timeout = setTimeout(
            searchChats,
            300
        );

        return () => clearTimeout(timeout);

    }, [search]);


    async function handleCreateChat() {

        if (!user) return;

        try {

            const response = await fetch(
                "https://tunelessly-snappy-goldeneye.cloudpub.ru/create_chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        user_id: user.user_id
                    })
                }
            );

            const newChat = await response.json();

            setChats([
                newChat,
                ...(Array.isArray(chats)
                    ? chats
                    : [])
            ]);

            setCurrentChat(newChat.id);

            clearMessages();

        } catch (error) {

            console.error(error);
        }
    }


    async function handleDeleteChat(
        chatId: number
    ) {

        try {

            await fetch(
                `https://tunelessly-snappy-goldeneye.cloudpub.ru/chat/${chatId}`,
                {
                    method: "DELETE"
                }
            );

            const updatedChats = chats.filter(
                (chat) => chat.id !== chatId
            );

            setChats(updatedChats);

            if (currentChatId === chatId) {

                setCurrentChat(null);

                clearMessages();
            }

        } catch (error) {

            console.error(error);
        }
    }


    function handleLogout() {

        logout();

        router.push("/login");
    }


    return (

        <div
            className="
                w-[300px]
                bg-white
                border-r
                border-gray-200
                flex
                flex-col
                h-screen
            "
        >

            {/* HEADER */}
            <div className="p-4 space-y-4">

                <button
                    onClick={handleCreateChat}
                    className="
                        w-full
                        flex
                        items-center
                        gap-2
                        bg-[#f0a3c8]
                        hover:bg-[#f0a3c8]
                        transition
                        rounded-xl
                        p-3
                        text-black
                        font-medium
                    "
                >

                    <MessageSquarePlus size={18} />

                    Новый чат

                </button>


                <input
                    type="text"

                    value={search}

                    onChange={(e) =>
                        setSearch(e.target.value)
                    }

                    placeholder="Поиск в чатах"

                    className="
                        w-full
                        bg-white
                        border
                        border-gray-300
                        rounded-xl
                        p-3
                        outline-none
                        focus:border-pink-500
                    "
                />

            </div>


            {/* CHATS */}
            <div
                className="
                    flex-1
                    overflow-y-auto
                    px-2
                "
            >

                {Array.isArray(chats) && chats.map((chat) => (

                    <div
                        key={chat.id}

                        className={`
                            flex
                            items-center
                            justify-between
                            p-3
                            rounded-xl
                            mb-2
                            transition
                            ${
                                currentChatId === chat.id
                                    ? "bg-[#f0a3c8]"
                                    : "hover:bg-gray-100"
                            }
                        `}
                    >

                        <button
                            onClick={() =>
                                setCurrentChat(chat.id)
                            }

                            className="
                                flex-1
                                text-left
                                truncate
                                text-gray-900
                            "
                        >

                            {chat.title}

                        </button>


                        <button
                            onClick={() =>
                                handleDeleteChat(chat.id)
                            }

                            className="
                                ml-2
                                text-gray-400
                                hover:text-red-500
                            "
                        >

                            <Trash2 size={16} />

                        </button>

                    </div>

                ))}

            </div>


            {/* FOOTER */}
            <div
                className="
                    p-4
                    border-t
                    border-gray-200
                "
            >

                <div
                    className="
                        text-sm
                        text-gray-500
                        mb-3
                        truncate
                    "
                >

                    {user?.email}

                </div>


                <button
                    onClick={handleLogout}

                    className="
                        w-full
                        bg-gray-100
                        hover:bg-gray-200
                        transition
                        rounded-xl
                        p-3
                        text-gray-900
                        font-medium
                    "
                >

                    Выйти

                </button>

            </div>

        </div>
    );
}