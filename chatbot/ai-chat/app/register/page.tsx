"use client";

import { useState } from "react";

import { useRouter } from "next/navigation";

import {
    Eye,
    EyeOff
} from "lucide-react";


export default function RegisterPage() {

    const router = useRouter();

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [showPassword, setShowPassword] =
        useState(false);

    const [error, setError] =
        useState("");

    const [success, setSuccess] =
        useState("");


    async function handleRegister() {

        setError("");

        setSuccess("");

        try {

            const response = await fetch(
                "https://tunelessly-snappy-goldeneye.cloudpub.ru/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        email,
                        password
                    })
                }
            );

            const data =
                await response.json();

            if (data.error) {

                setError(data.error);

                return;
            }

            setSuccess(
                "Аккаунт создан"
            );

            setTimeout(() => {

                router.push("/login");

            }, 1000);

        } catch {

            setError(
                "Ошибка подключения к API"
            );
        }
    }


    return (

        <main
            className="
                min-h-screen
                bg-[#f5f5f5]
                flex
                items-center
                justify-center
                p-6
            "
        >

            <div
                className="
                    w-full
                    max-w-md
                    bg-white
                    rounded-3xl
                    shadow-sm
                    border
                    border-gray-200
                    p-8
                "
            >

                <h1
                    className="
                        text-3xl
                        font-bold
                        text-center
                        mb-8
                        text-gray-900
                    "
                >

                    Регистрация

                </h1>


                <div className="space-y-5">

                    <input
                        type="email"

                        placeholder="Email"

                        autoComplete="email"

                        value={email}

                        onChange={(e) =>
                            setEmail(
                                e.target.value
                            )
                        }

                        className="
                            w-full
                            border
                            border-gray-300
                            bg-[#f9fafb]
                            rounded-2xl
                            px-5
                            py-4
                            outline-none
                            focus:border-[#f0a3c8]
                            text-gray-900
                        "
                    />


                    <div className="relative">

                        <input
                            type={
                                showPassword
                                    ? "text"
                                    : "password"
                            }

                            placeholder="Пароль"

                            autoComplete="new-password"

                            value={password}

                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }

                            className="
                                w-full
                                border
                                border-gray-300
                                bg-[#f9fafb]
                                rounded-2xl
                                px-5
                                py-4
                                pr-14
                                outline-none
                                focus:border-[#f0a3c8]
                                text-gray-900
                            "
                        />

                        <button
                            type="button"

                            onClick={() =>
                                setShowPassword(
                                    !showPassword
                                )
                            }

                            className="
                                absolute
                                right-4
                                top-1/2
                                -translate-y-1/2
                                text-gray-500
                            "
                        >

                            {showPassword
                                ? <EyeOff size={20} />
                                : <Eye size={20} />
                            }

                        </button>

                    </div>


                    {error && (

                        <div
                            className="
                                text-red-500
                                text-sm
                            "
                        >

                            {error}

                        </div>
                    )}


                    {success && (

                        <div
                            className="
                                text-green-600
                                text-sm
                            "
                        >

                            {success}

                        </div>
                    )}


                    <button
                        onClick={handleRegister}

                        className="
                            w-full
                            bg-[#f0a3c8]
                            hover:bg-[#f0a3c8]
                            transition
                            rounded-2xl
                            py-4
                            text-white
                            font-medium
                        "
                    >

                        Создать аккаунт

                    </button>


                    <button
                        onClick={() =>
                            router.push(
                                "/login"
                            )
                        }

                        className="
                            w-full
                            bg-gray-100
                            hover:bg-gray-200
                            transition
                            rounded-2xl
                            py-4
                            text-gray-900
                            font-medium
                        "
                    >

                        Уже есть аккаунт

                    </button>

                </div>

            </div>

        </main>
    );
}