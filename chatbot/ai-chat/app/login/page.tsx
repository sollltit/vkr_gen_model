"use client";

import { useState } from "react";

import { useRouter } from "next/navigation";

import {
    Eye,
    EyeOff
} from "lucide-react";

import { useAuthStore } from "@/store/authStore";


export default function LoginPage() {

    const router = useRouter();

    const login = useAuthStore(
        (state) => state.login
    );

    const [email, setEmail] = useState("");

    const [password, setPassword] =
        useState("");

    const [showPassword, setShowPassword] =
        useState(false);

    const [error, setError] =
        useState("");


    async function handleLogin() {

        setError("");

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/login",
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

            login(data);

            router.push("/");

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

                    Вход

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

                            autoComplete="current-password"

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


                    <button
                        onClick={handleLogin}

                        className="
                            w-full
                            bg-[#f0a3c8]
                            hover:bg-[#e592ba]
                            transition
                            rounded-2xl
                            py-4
                            text-black
                            font-medium
                        "
                    >

                        Войти

                    </button>


                    <button
                        onClick={() =>
                            router.push(
                                "/register"
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

                        Регистрация

                    </button>

                </div>

            </div>

        </main>
    );
}