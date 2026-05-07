"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
    role: string;
    content: string;
}

export default function Message({ role, content }: Props) {
    const isUser = role === "user";

    return (
        <div
            className={`w-full flex ${
                isUser ? "justify-end" : "justify-start"
            }`}
        >
            <div
                className={`
                    max-w-3xl
                    rounded-2xl
                    px-4
                    py-3
                    my-2
                    whitespace-pre-wrap
                    ${
                        isUser
                            ? "bg-blue-500 text-white"
                            : "bg-zinc-800 text-zinc-100"
                    }
                `}
            >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {content}
                </ReactMarkdown>
            </div>
        </div>
    );
}