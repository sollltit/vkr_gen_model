"use client";

import { useEffect, useRef, useState } from "react";

import { useChatStore } from "@/store/chatStore";
import { useMessageStore } from "@/store/messageStore";

import MessageBubble from "./MessageBubble";


export default function Chat() {

    const [isLoading, setIsLoading] =
        useState(false);

    const [input, setInput] = useState("");

    const messagesEndRef =
        useRef<HTMLDivElement>(null);

    const currentChatId = useChatStore(
        (state) => state.currentChatId
    );

    const chats = useChatStore(
        (state) => state.chats
    );

    const setChats = useChatStore(
        (state) => state.setChats
    );

    const {
        messages,
        setMessages,
        addMessage,
        updateLastMessage
    } = useMessageStore();


    useEffect(() => {

        async function loadMessages() {

            if (!currentChatId) {

                setMessages([]);

                return;
            }

            try {

                const response = await fetch(
                    `http://127.0.0.1:8000/messages/${currentChatId}`
                );

                const data = await response.json();

                setMessages(
                    data.messages || []
                );

            } catch (error) {

                console.error(error);

                setIsLoading(false);
            }
        }

        loadMessages();

    }, [currentChatId]);

    useEffect(() => {

        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });

    }, [messages, isLoading]);

    async function handleSend() {

        if (!input.trim()) return;

        if (!currentChatId) return;

        setIsLoading(true);

        const userMessage = {

            role: "user",

            content: input
        };

        addMessage(userMessage);

        setInput("");

        addMessage({
            role: "assistant",
            content: ""
        });

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/chat_stream",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        chat_id: currentChatId,
                        messages: [
                            ...messages,
                            userMessage
                        ]
                    })
                }
            );

            const reader = response.body?.getReader();

            const decoder = new TextDecoder();

            let fullText = "";

            if (!reader) return;

            while (true) {

                const {
                    done,
                    value
                } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);

                fullText += chunk;

                updateLastMessage(fullText);
            }


            const updatedChats = chats.map((chat) => {

                if (
                    chat.id === currentChatId &&
                    chat.title === "Новый чат"
                ) {

                    return {

                        ...chat,

                        title: input.slice(0, 40)
                    };
                }

                return chat;
            });

            setChats(updatedChats);

            setIsLoading(false);

        } catch (error) {

            console.error(error);

            setIsLoading(false);
        }
    }


    if (!currentChatId) {

        return (

            <div
                className="
                    flex
                    items-center
                    justify-center
                    bg-[#f5f5f5]
                    h-full
                "
            >

                <h1
                    className="
                        text-4xl
                        font-bold
                        text-gray-400
                    "
                >

                    Создайте чат

                </h1>

            </div>
        );
    }


    return (

        <div
            className="
                flex-1
                flex
                flex-col
                bg-[#f5f5f5]
                h-screen
            "
        >

            {/* MESSAGES */}
            <div
                className="
                    flex-1
                    overflow-y-auto
                    px-6
                    py-8
                "
            >

                <div
                    className="
                        max-w-4xl
                        mx-auto
                    "
                >

                    {/* CHAT MESSAGES */}
                    {messages.map((message, index) => (

                        <MessageBubble
                            key={index}
                            role={message.role}
                            content={message.content}
                        />

                    ))}


                    {/* LOADING */}
                    {isLoading && (

                        <div
                            className="
                                flex
                                justify-start
                                mb-6
                            "
                        >

                            <div
                                className="
                                    bg-[#eeeeee]
                                    text-gray-500
                                    px-5
                                    py-3
                                    rounded-2xl
                                    italic
                                    text-sm
                                    shadow-sm
                                    max-w-[80%]
                                "
                            >

                                Генерация ответа...

                            </div>

                        </div>

                    )}


                    <div ref={messagesEndRef} />

                </div>

            </div>


            {/* INPUT */}
            <div
                className="
                    border-t
                    border-gray-200
                    bg-white
                    p-6
                "
            >

                <div
                    className="
                        max-w-4xl
                        mx-auto
                        flex
                        gap-4
                    "
                >

                    <input
                        value={input}

                        onChange={(e) =>
                            setInput(e.target.value)
                        }

                        onKeyDown={(e) => {

                            if (e.key === "Enter") {

                                handleSend();
                            }
                        }}

                        placeholder="Напишите сообщение..."

                        className="
                            flex-1
                            bg-white
                            border
                            border-gray-300
                            rounded-2xl
                            px-5
                            py-4
                            outline-none
                            text-gray-900
                            focus:border-[#f0a3c8]
                        "
                    />


                    <button
                        onClick={handleSend}

                        className="
                            bg-[#f0a3c8]
                            hover:bg-[#f0a3c8]
                            transition
                            rounded-2xl
                            px-8
                            text-black
                            font-medium
                            border-pink-100
                        "
                    >

                        Отправить

                    </button>

                </div>

            </div>

        </div>
    );
}

