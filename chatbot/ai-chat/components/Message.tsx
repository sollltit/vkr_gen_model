"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
    role: string;
    content: string;
}

export default function Message({
    role,
    content
}: Props) {

    const isUser = role === "user";

    return (
        <div
            className={`
                flex
                w-full
                mb-8
                ${
                    isUser
                        ? "justify-end"
                        : "justify-start"
                }
            `}
        >
            <div
                className={`
                    max-w-3xl
                    rounded-3xl
                    px-6
                    py-5
                    text-[16px]
                    leading-8
                    shadow-lg
                    whitespace-pre-wrap
                    ${
                        isUser
                            ? "bg-blue-600 text-white"
                            : "bg-[#1f1f1f] text-white border border-zinc-800"
                    }
                `}
            >
                <div className="text-white">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {content}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
}