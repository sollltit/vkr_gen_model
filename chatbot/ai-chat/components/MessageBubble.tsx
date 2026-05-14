"use client";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import rehypeKatex from "rehype-katex";
import rehypeHighlight from "rehype-highlight";

import "katex/dist/katex.min.css";

interface Props {

    role: string;

    content: string;
}

export default function MessageBubble({
    role,
    content
}: Props) {

    return (

        <div
            className={`
                w-full
                flex
                mb-6
                ${
                    role === "user"
                        ? "justify-end"
                        : "justify-start"
                }
            `}
        >

            <div
                className={`
                    max-w-[850px]
                    rounded-3xl
                    px-6
                    py-5
                    shadow-sm
                    leading-8
                    text-[16px]
                    overflow-hidden
                    border
                    ${
                        role === "user"

                            ? `
                                bg-[#f0a3c8]
                                text-black
                                border-pink-600
                            `

                            : `
                                bg-[#eef2f7]
                                text-gray-900
                                border-[#dde3ea]
                            `
                    }
                `}
            >

                <div className="markdown-body">

                    <ReactMarkdown
                        remarkPlugins={[
                            remarkGfm,
                            remarkMath
                        ]}

                        rehypePlugins={[
                            rehypeKatex,
                            rehypeHighlight
                        ]}
                    >

                        {content}

                    </ReactMarkdown>

                </div>

            </div>

        </div>
    );
}