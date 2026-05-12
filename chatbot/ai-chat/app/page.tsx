"use client";

import { useEffect } from "react";

import { useRouter } from "next/navigation";

import Sidebar from "@/components/Sidebar";

import Chat from "@/components/Chat";

import { useAuthStore } from "@/store/authStore";


export default function Home() {

    const router = useRouter();

    const user = useAuthStore(
        (state) => state.user
    );


    useEffect(() => {

        if (!user) {

            router.push("/login");
        }

    }, [user]);


    return (

        <main
            className="
                flex
                h-screen
                bg-[#0a0a0a]
                text-white
            "
        >

            <Sidebar />

            <Chat />

        </main>
    );
}