"use client";

import { useState } from "react";

type Props = {
    onSend: (text: string) => void;
    loading: boolean;
};

export default function ChatInput({ onSend, loading }: Props) {
    const [text, setText] = useState("");

    const handleSend = () => {
        if (!text.trim()) return;

        onSend(text);
        setText("");
    };

    return (
        <div className="p-4 border-t border-zinc-800 bg-black">
            <div className="flex gap-2 max-w-3xl mx-auto">
                
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Напишите сообщение..."
                    className="
                        flex-1
                        bg-zinc-900
                        text-white
                        p-3
                        rounded-xl
                        resize-none
                        outline-none
                        border border-zinc-700
                    "
                    rows={3}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                />

                <button
                    onClick={handleSend}
                    disabled={loading}
                    className="
                        px-5
                        rounded-xl
                        bg-blue-600
                        text-white
                        disabled:opacity-50
                    "
                >
                    {loading ? "..." : "Send"}
                </button>
            </div>
        </div>
    );
}