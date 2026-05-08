"use client";

import { MessageSquarePlus } from "lucide-react";

import { useChatStore } from "@/store/chatStore";

export default function Sidebar() {
    const {
        chats,
        currentChatId,
        setCurrentChat,
        createChat
    } = useChatStore();

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
            <div className="p-4">
                <button
                    onClick={createChat}
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
                    "
                >
                    <MessageSquarePlus size={18} />

                    Новый чат
                </button>
            </div>

            <div className="flex-1 overflow-y-auto px-2">
                {chats.map((chat) => (
                    <button
                        key={chat.id}
                        onClick={() =>
                            setCurrentChat(chat.id)
                        }
                        className={`
                            w-full
                            text-left
                            p-3
                            rounded-xl
                            mb-2
                            transition
                            ${
                                currentChatId === chat.id
                                    ? "bg-zinc-800"
                                    : "hover:bg-zinc-900"
                            }
                        `}
                    >
                        {chat.title}
                    </button>
                ))}
            </div>
        </div>
    );
}