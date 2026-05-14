"use client";

import {
    useState,
    KeyboardEvent
} from "react";


interface Props {

    onSend: (
        text: string
    ) => void;

    loading: boolean;
}


export default function ChatInput({
    onSend,
    loading
}: Props) {

    const [text, setText] = useState("");


    // =========================
    // SEND MESSAGE
    // =========================
    function handleSend() {

        if (!text.trim()) return;

        onSend(text);

        setText("");
    }


    // =========================
    // ENTER
    // =========================
    function handleKeyDown(
        e: KeyboardEvent<HTMLTextAreaElement>
    ) {

        if (
            e.key === "Enter" &&
            !e.shiftKey
        ) {

            e.preventDefault();

            handleSend();
        }
    }


    return (

        <div
            className="
                border-t
                border-zinc-800
                p-4
                bg-[#0a0a0a]
            "
        >

            <div
                className="
                    max-w-4xl
                    mx-auto
                    flex
                    gap-3
                    items-end
                "
            >

                {/* INPUT */}
                <textarea
                    value={text}

                    onChange={(e) =>
                        setText(e.target.value)
                    }

                    onKeyDown={handleKeyDown}

                    placeholder="Напишите сообщение..."

                    rows={1}

                    className="
                        flex-1
                        resize-none
                        rounded-2xl
                        bg-zinc-900
                        text-black
                        px-5
                        py-4
                        outline-none
                        border
                        border-zinc-800
                        focus:border-zinc-700
                        min-h-[60px]
                        max-h-[200px]
                    "
                />


                {/* BUTTON */}
                <button
                    onClick={handleSend}

                    disabled={loading}

                    className="
                        h-[60px]
                        px-6
                        rounded-2xl
                        bg-blue-600
                        hover:bg-blue-500
                        transition
                        text-black
                        disabled:opacity-50
                    "
                >

                    {loading
                        ? "..."
                        : "Отправить"}

                </button>

            </div>

        </div>
    );
}