"use client";

import { useEffect, useRef, useState } from "react";

import MessageBubble from "./MessageBubble";

import ChatInput from "./ChatInput";

import {
    useMessageStore
} from "@/store/messageStore";

import {
    useChatStore
} from "@/store/chatStore";


export default function Chat() {

    // =========================
    // CHAT STORE
    // =========================
    const currentChatId = useChatStore(
        (state) => state.currentChatId
    );


    // =========================
    // MESSAGE STORE
    // =========================
    const {
        messages,
        setMessages,
        addMessage
    } = useMessageStore();


    // =========================
    // LOADING
    // =========================
    const [loading, setLoading] =
        useState(false);


    // =========================
    // AUTO SCROLL
    // =========================
    const bottomRef =
        useRef<HTMLDivElement>(null);


    useEffect(() => {

        bottomRef.current?.scrollIntoView({
            behavior: "smooth"
        });

    }, [messages]);


    // =========================
    // ЗАГРУЗКА СООБЩЕНИЙ ЧАТА
    // =========================
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

                console.log(
                    "MESSAGES:",
                    data
                );

                setMessages(
                    data.messages || []
                );

            } catch (error) {

                console.error(
                    "Ошибка загрузки сообщений",
                    error
                );
            }
        }

        loadMessages();

    }, [currentChatId]);


    // =========================
    // SEND MESSAGE
    // =========================
    async function handleSend(
        text: string
    ) {

        if (!currentChatId) return;

        if (!text.trim()) return;


        // =========================
        // USER MESSAGE
        // =========================
        const userMessage = {

            id: Date.now(),

            role: "user" as const,

            content: text
        };


        // Сразу показываем сообщение
        addMessage(userMessage);


        // =========================
        // ВРЕМЕННОЕ AI MESSAGE
        // =========================
        const assistantId =
            Date.now() + 1;


        addMessage({

            id: assistantId,

            role: "assistant",

            content: ""
        });


        setLoading(true);


        try {

            // =========================
            // STREAM REQUEST
            // =========================
            const response = await fetch(

                "http://127.0.0.1:8000/chat_stream",

                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
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


            if (!response.body) {

                console.error(
                    "Нет response.body"
                );

                return;
            }


            // =========================
            // STREAM READER
            // =========================
            const reader =
                response.body.getReader();

            const decoder =
                new TextDecoder();


            let fullText = "";


            // =========================
            // ЧТЕНИЕ STREAM
            // =========================
            while (true) {

                const {
                    done,
                    value
                } = await reader.read();


                if (done) break;


                // chunk текста
                const chunk =
                    decoder.decode(value);


                // накапливаем текст
                fullText += chunk;


                // обновляем assistant message
                setMessages((prev: any[]) =>

                    prev.map((msg) =>

                        msg.id === assistantId

                            ? {
                                ...msg,
                                content: fullText
                            }

                            : msg
                    )
                );
            }

        } catch (error) {

            console.error(
                "Ошибка отправки",
                error
            );

        } finally {

            setLoading(false);
        }
    }


    // =========================
    // EMPTY CHAT
    // =========================
    if (!currentChatId) {

        return (

            <div
                className="
                    flex-1
                    flex
                    items-center
                    justify-center
                    text-zinc-500
                    text-2xl
                "
            >

                Создайте чат

            </div>
        );
    }


    // =========================
    // UI
    // =========================
    return (

        <div
            className="
                flex-1
                flex
                flex-col
                h-screen
                bg-[#0f0f0f]
            "
        >

            {/* ========================= */}
            {/* MESSAGES */}
            {/* ========================= */}
            <div
                className="
                    flex-1
                    overflow-y-auto
                    px-6
                    py-10
                "
            >

                <div
                    className="
                        max-w-4xl
                        mx-auto
                    "
                >

                    {messages.map((message) => (

                        <MessageBubble
                            key={message.id}
                            role={message.role}
                            content={message.content}
                        />

                    ))}


                    {/* LOADING */}
                    {loading && (

                        <div
                            className="
                                text-zinc-500
                                text-sm
                                mt-2
                            "
                        >

                            Модель печатает...

                        </div>
                    )}


                    {/* AUTO SCROLL */}
                    <div ref={bottomRef} />

                </div>

            </div>


            {/* ========================= */}
            {/* INPUT */}
            {/* ========================= */}
            <div
                className="
                    border-t
                    border-zinc-800
                    p-4
                    bg-[#0f0f0f]
                "
            >

                <div
                    className="
                        max-w-4xl
                        mx-auto
                    "
                >

                    <ChatInput
                        onSend={handleSend}
                    />

                </div>

            </div>

        </div>
    );
}