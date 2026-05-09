"use client";

import { useState } from "react";

import { useRouter } from "next/navigation";

import {
    Eye,
    EyeOff
} from "lucide-react";


export default function RegisterPage() {

    const router = useRouter();

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    const [error, setError] = useState("");

    const [loading, setLoading] = useState(false);

    const [showPassword, setShowPassword] = useState(false);


    // =========================
    // Проверка русских букв
    // =========================
    function containsRussian(text: string) {

        return /[А-Яа-яЁё]/.test(text);

    }


    // =========================
    // Регистрация
    // =========================
    async function handleRegister() {

        // Сбрасываем ошибку
        setError("");

        // Проверка email
        if (containsRussian(email)) {

            setError(
                "Email должен содержать только английские символы"
            );

            return;
        }

        // Проверка password
        if (containsRussian(password)) {

            setError(
                "Пароль не должен содержать русские символы"
            );

            return;
        }

        try {

            setLoading(true);

            const response = await fetch(
                "http://127.0.0.1:8000/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email,
                        password
                    })
                }
            );

            const data = await response.json();

            // Ошибка backend
            if (data.error) {

                setError(data.error);

                return;
            }

            // Переход на login
            router.push("/login");

        } catch (err) {

            setError("Ошибка подключения");

        } finally {

            setLoading(false);

        }
    }


    return (

        <main
            className="
                min-h-screen
                bg-black
                flex
                items-center
                justify-center
            "
        >

            <div
                className="
                    w-full
                    max-w-md
                    bg-[#0f0f0f]
                    border
                    border-zinc-800
                    rounded-3xl
                    p-8
                    shadow-2xl
                "
            >

                {/* TITLE */}
                <h1
                    className="
                        text-4xl
                        font-semibold
                        text-center
                        text-white
                        mb-8
                    "
                >
                    Регистрация
                </h1>


                {/* EMAIL */}
                <input
                    type="email"

                    autoComplete="email"

                    placeholder="Email"

                    value={email}

                    onChange={(e) =>
                        setEmail(e.target.value)
                    }

                    className="
                        w-full
                        mb-4
                        bg-zinc-900
                        border
                        border-zinc-700
                        rounded-2xl
                        px-4
                        py-4
                        text-white
                        outline-none
                    "
                />


                {/* PASSWORD CONTAINER */}
                <div className="relative mb-4">

                    {/* PASSWORD INPUT */}
                    <input
                        type={
                            showPassword
                                ? "text"
                                : "password"
                        }

                        autoComplete="new-password"

                        placeholder="Пароль"

                        value={password}

                        onChange={(e) =>
                            setPassword(e.target.value)
                        }

                        className="
                            w-full
                            bg-zinc-900
                            border
                            border-zinc-700
                            rounded-2xl
                            px-4
                            py-4
                            pr-14
                            text-white
                            outline-none
                        "
                    />

                    {/* EYE BUTTON */}
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
                            text-zinc-400
                            hover:text-white
                        "
                    >

                        {showPassword
                            ? <EyeOff size={20} />
                            : <Eye size={20} />
                        }

                    </button>

                </div>


                {/* ERROR */}
                {error && (

                    <div
                        className="
                            text-red-500
                            mb-4
                            text-sm
                        "
                    >
                        {error}
                    </div>

                )}


                {/* BUTTON */}
                <button
                    onClick={handleRegister}

                    disabled={loading}

                    className="
                        w-full
                        bg-white
                        text-black
                        rounded-2xl
                        py-4
                        font-medium
                        hover:opacity-90
                        transition
                    "
                >

                    {loading
                        ? "Создание..."
                        : "Создать аккаунт"}

                </button>


                {/* LOGIN LINK */}
                <button
                    onClick={() =>
                        router.push("/login")
                    }

                    className="
                        w-full
                        mt-4
                        text-zinc-400
                        hover:text-white
                        transition
                    "
                >

                    Уже есть аккаунт? Войти

                </button>

            </div>

        </main>

    );
}