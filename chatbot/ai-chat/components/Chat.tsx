"use client";

import { useState } from "react";

import { sendMessage } from "@/lib/api";

import { useChatStore } from "@/store/chatStore";

import Message from "./Message";
import ChatInput from "./ChatInput";

export default function Chat() {
    const { messages, addMessage } = useChatStore();

    const [loading, setLoading] = useState(false);

    async function handleSend(text: string) {
        const userMessage = {
            role: "user",
            content: text
        };

        addMessage(userMessage);

        setLoading(true);

        try {
            const updatedMessages = [
                ...messages,
                userMessage
            ];

            const response = await sendMessage(updatedMessages);

            addMessage({
                role: "assistant",
                content: response
            });

        } catch (error) {
            addMessage({
                role: "assistant",
                content: "Ошибка подключения к API"
            });

        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex flex-col h-screen bg-black">
            <div className="flex-1 overflow-y-auto p-4">
                {messages.map((msg, index) => (
                    <Message
                        key={index}
                        role={msg.role}
                        content={msg.content}
                    />
                ))}
            </div>

            <ChatInput
                onSend={handleSend}
                loading={loading}
            />
        </div>
    );
}