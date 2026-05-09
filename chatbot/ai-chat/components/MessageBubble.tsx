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
                ${isUser
                    ? "justify-end"
                    : "justify-start"}
            `}
        >

            <div
                className={`
                    max-w-[800px]
                    px-5
                    py-4
                    rounded-2xl
                    whitespace-pre-wrap
                    leading-7
                    text-[15px]
                    shadow-lg
                    ${isUser
                        ? "bg-blue-600 text-white"
                        : "bg-zinc-900 text-zinc-100"}
                `}
            >

                {content}

            </div>

        </div>
    );
}