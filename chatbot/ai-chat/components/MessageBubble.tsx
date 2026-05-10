"use client";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";


interface Props {

    role: "user" | "assistant";

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
                w-full
                flex
                mb-6
                ${
                    isUser
                        ? "justify-end"
                        : "justify-start"
                }
            `}
        >
            <div
                className={`
                    max-w-[85%]
                    px-5
                    py-4
                    rounded-2xl
                    text-[15px]
                    leading-7
                    overflow-hidden
                    whitespace-pre-wrap
                    break-words
                    ${
                        isUser
                            ? "bg-zinc-800 text-white"
                            : "bg-zinc-900 text-zinc-100"
                    }
                `}
            >
<ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{

                        code(props) {

                            const {
                                children,
                                className,
                                ...rest
                            } = props;

                            const match = /language-(\w+)/.exec(
                                className || ""
                            );

                            return match ? (

                                <SyntaxHighlighter
                                    style={oneDark}
                                    language={match[1]}
                                    PreTag="div"
                                >
                                    {String(children).replace(/\n$/, "")}
                                </SyntaxHighlighter>

                            ) : (

                                <code
                                    className="bg-zinc-800 px-1 py-0.5 rounded"
                                    {...rest}
                                >
                                    {children}
                                </code>
                            );
                        }
                    }}
                >
                    {content}
                </ReactMarkdown>

            </div>

        </div>
    );
}