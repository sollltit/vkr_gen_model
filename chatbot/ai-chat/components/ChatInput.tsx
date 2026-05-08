"use client";

import { useState } from "react";

interface Props {
    onSend: (text: string) => void;
    loading: boolean;
}

export default function ChatInput({
    onSend,
    loading
}: Props) {
    const [text, setText] = useState("");

    function handleSend() {
        if (!text.trim()) return;

        onSend(text);

        setText("");
    }

    return (
        <div className="w-full px-6 pb-6">
            <div
                className="
                    max-w-4xl
                    mx-auto
                    bg-zinc-900
                    border
                    border-zinc-800
                    rounded-3xl
                    p-4
                "
            >
                <textarea
                    value={text}
                    onChange={(e) =>
                        setText(e.target.value)
                    }
                    placeholder="Напишите сообщение..."
                    rows={3}
                    className="
                        w-full
                        bg-transparent
                        outline-none
                        resize-none
                        text-white
                    "
                    onKeyDown={(e) => {
                        if (
                            e.key === "Enter" &&
                            !e.shiftKey
                        ) {
                            e.preventDefault();

                            handleSend();
                        }
                    }}
                />

                <div className="flex justify-end mt-3">
                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className="
                            bg-blue-600
                            hover:bg-blue-500
                            transition
                            px-5
                            py-2
                            rounded-xl
                        "
                    >
                        {loading ? "..." : "Send"}
                    </button>
                </div>
            </div>
        </div>
    );
}