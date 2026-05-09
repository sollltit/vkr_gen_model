"use client";

import { useEffect } from "react";

import {
    MessageSquarePlus,
    Trash2
} from "lucide-react";

import { useRouter } from "next/navigation";

import { useChatStore } from "@/store/chatStore";

import { useAuthStore } from "@/store/authStore";


export default function Sidebar() {

    const router = useRouter();


    // =========================
    // AUTH
    // =========================
    const user = useAuthStore(
        (state) => state.user
    );

    const logout = useAuthStore(
        (state) => state.logout
    );


    // =========================
    // CHAT STORE
    // =========================
    const {
        chats,
        currentChatId,
        setCurrentChat,
        setChats
    } = useChatStore();


    // =========================
    // Загрузка чатов пользователя
    // =========================
    useEffect(() => {

        async function loadChats() {

            if (!user) return;

            try {

                const response = await fetch(

                    `http://127.0.0.1:8000/chats/${user.user_id}`

                );

                const data = await response.json();

                console.log("CHATS:", data);

                setChats(

                    Array.isArray(data.chats)
                        ? data.chats
                        : []

                );

            } catch (error) {

                console.error(
                    "Ошибка загрузки чатов",
                    error
                );
            }
        }

        loadChats();

    }, [user]);


    // =========================
    // CREATE CHAT
    // =========================
    async function handleCreateChat() {

    if (!user) return;

    try {

        const response = await fetch(

            "http://127.0.0.1:8000/create_chat",

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

    } catch (error) {

        console.error(error);
    }
}


    // =========================
    // DELETE CHAT
    // =========================
    async function handleDeleteChat(
        chatId: number
    ) {

        try {

            await fetch(

                `http://127.0.0.1:8000/chat/${chatId}`,

                {
                    method: "DELETE"
                }
            );

            // Обновляем список
            const updatedChats = chats.filter(
                (chat) => chat.id !== chatId
            );

            setChats(updatedChats);

        } catch (error) {

            console.error(
                "Ошибка удаления чата",
                error
            );
        }
    }


    // =========================
    // LOGOUT
    // =========================
    function handleLogout() {

        logout();

        router.push("/login");
    }


    return (

        <div
            className="
                w-[280px]
                bg-[#111111]
                border-r
                border-zinc-800
                flex
                flex-col
                h-screen
            "
        >

            {/* HEADER */}
            <div className="p-4">

                <button
                    onClick={handleCreateChat}
                    className="
                        w-full
                        flex
                        items-center
                        gap-2
                        bg-zinc-900
                        hover:bg-zinc-800
                        transition
                        rounded-xl
                        p-3
                        text-white
                    "
                >

                    <MessageSquarePlus size={18} />

                    Новый чат

                </button>

            </div>


            {/* CHAT LIST */}
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
                            cursor-pointer
                            ${
                                currentChatId === chat.id
                                    ? "bg-zinc-800"
                                    : "hover:bg-zinc-900"
                            }
                        `}
                    >

                        {/* CHAT BUTTON */}
                        <button
                            onClick={() =>
                                setCurrentChat(chat.id)
                            }

                            className="
                                flex-1
                                text-left
                                truncate
                                text-white
                            "
                        >

                            {chat.title}

                        </button>


                        {/* DELETE BUTTON */}
                        <button
                            onClick={() =>
                                handleDeleteChat(chat.id)
                            }

                            className="
                                ml-2
                                text-zinc-400
                                hover:text-red-500
                                transition
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
                    border-zinc-800
                "
            >

                {/* EMAIL */}
                <div
                    className="
                        text-sm
                        text-zinc-400
                        mb-3
                        truncate
                    "
                >

                    {user?.email}

                </div>


                {/* LOGOUT */}
                <button
                    onClick={handleLogout}

                    className="
                        w-full
                        bg-zinc-900
                        hover:bg-zinc-800
                        transition
                        rounded-xl
                        p-3
                        text-white
                    "
                >

                    Выйти

                </button>

            </div>

        </div>
    );
}