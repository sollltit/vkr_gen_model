"use client";

import {
    useEffect,
    useRef,
    useState
} from "react";

import MessageBubble from "./MessageBubble";

import ChatInput from "./ChatInput";

import {
    useMessageStore
} from "@/store/messageStore";

import {
    useChatStore
} from "@/store/chatStore";


export default function Chat() {

    const {
        messages,
        setMessages,
        addMessage
    } = useMessageStore();

    const {
        currentChatId
    } = useChatStore();

    const [loading, setLoading] =
        useState(false);

    const bottomRef =
        useRef<HTMLDivElement>(null);


    // =========================
    // AUTO SCROLL
    // =========================
    useEffect(() => {

        bottomRef.current?.scrollIntoView({
            behavior: "smooth"
        });

    }, [messages]);


    // =========================
    // LOAD MESSAGES
    // =========================
    useEffect(() => {

        async function loadMessages() {

            if (!currentChatId) return;

            try {

                const response = await fetch(

                    `http://127.0.0.1:8000/messages/${currentChatId}`

                );

                const data = await response.json();

                setMessages(

                    Array.isArray(data.messages)
                        ? data.messages
                        : []

                );

            } catch (error) {

                console.error(error);
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

        const userMessage = {

            id: Date.now(),

            role: "user" as const,

            content: text
        };

        // Добавляем user message
        addMessage(userMessage);

        setLoading(true);

        try {

            const response = await fetch(

                "http://127.0.0.1:8000/chat",

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

            const data =
                await response.json();

            // Добавляем ответ модели
            addMessage({

                id: Date.now() + 1,

                role: "assistant",

                content: data.response
            });

        } catch (error) {

            console.error(error);

        } finally {

            setLoading(false);
        }
    }


    // =========================
    // EMPTY SCREEN
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


    return (

        <div
            className="
                flex
                flex-col
                h-screen
                flex-1
                bg-[#0a0a0a]
            "
        >

            {/* MESSAGES */}
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

                    {messages.map(
                        (message) => (

                            <MessageBubble
                                key={message.id}
                                role={message.role}
                                content={
                                    message.content
                                }
                            />
                        )
                    )}

                    <div ref={bottomRef} />

                </div>

            </div>


            {/* INPUT */}
            <ChatInput
                onSend={handleSend}
                loading={loading}
            />

        </div>
    );
}