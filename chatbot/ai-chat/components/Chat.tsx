"use client";

import { useState } from "react";

import { sendMessage } from "@/lib/api";

import { useChatStore } from "@/store/chatStore";

import Message from "./Message";
import ChatInput from "./ChatInput";
import Sidebar from "./Sidebar";

export default function Chat() {
    const {
        chats,
        currentChatId,
        addMessage
    } = useChatStore();

    const currentChat = chats.find(
        (chat) => chat.id === currentChatId
    );

    const [loading, setLoading] = useState(false);

    async function handleSend(text: string) {
        const userMessage = {
            role: "user" as const,
            content: text
        };

        addMessage(userMessage);

        setLoading(true);

        try {
            const updatedMessages = [
                ...(currentChat?.messages || []),
                userMessage
            ];

            const response =
                await sendMessage(updatedMessages);

            addMessage({
                role: "assistant",
                content: response
            });

        } catch {
            addMessage({
                role: "assistant",
                content:
                    "Ошибка подключения к API"
            });

        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex h-screen bg-black text-white">
            
            <Sidebar />

            <div className="flex-1 flex flex-col">
                
                <div
                    className="
                        flex-1
                        overflow-y-auto
                        px-6
                        py-10
                    "
                >
                    <div className="max-w-4xl mx-auto">
                        {currentChat?.messages.map(
                            (msg, index) => (
                                <Message
                                    key={index}
                                    role={msg.role}
                                    content={msg.content}
                                />
                            )
                        )}
                    </div>
                </div>

                <ChatInput
                    onSend={handleSend}
                    loading={loading}
                />
            </div>
        </div>
    );
}