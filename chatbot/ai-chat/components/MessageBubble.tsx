"use client";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";

import remarkMath from "remark-math";

import rehypeKatex from "rehype-katex";

import rehypeHighlight from "rehype-highlight";

import "katex/dist/katex.min.css";

import "highlight.js/styles/github-dark.css";

interface Props {

    role: string;

    content: string;
}


export default function MessageBubble({
    role,
    content
}: Props) {

    const isUser = role === "user";

    return (

        <div
            className={`
                flex
                mb-6
                ${isUser ? "justify-end" : "justify-start"}
            `}
        >

            <div
                className={`
                    max-w-[850px]
                    rounded-2xl
                    px-5
                    py-4
                    leading-7
                    overflow-hidden
                    ${
                        isUser
                            ? "bg-zinc-800 text-white"
                            : "bg-zinc-900 text-zinc-100"
                    }
                `}
            >

                <div
                    className="
                        prose
                        prose-invert
                        max-w-none

                        prose-headings:text-white

                        prose-p:text-zinc-200

                        prose-strong:text-white

                        prose-code:text-blue-300

                        prose-pre:bg-[#111111]
                        prose-pre:border
                        prose-pre:border-zinc-800
                        prose-pre:rounded-xl
                        prose-pre:p-4

                        prose-table:w-full
                        prose-table:border-collapse

                        prose-th:border
                        prose-th:border-zinc-700
                        prose-th:p-2

                        prose-td:border
                        prose-td:border-zinc-700
                        prose-td:p-2
                    "
                >

                    <ReactMarkdown
                        remarkPlugins={[
                            remarkGfm,
                            remarkMath
                        ]}

                        rehypePlugins={[
                            rehypeHighlight,
                            [rehypeKatex, {
                                strict: false
                            }]
                        ]}
                    >

                        {content}

                    </ReactMarkdown>

                </div>

            </div>

        </div>
    );
}