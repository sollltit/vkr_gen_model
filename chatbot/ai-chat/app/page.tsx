"use client";

import Sidebar from "@/components/Sidebar";
import Chat from "@/components/Chat";

export default function Home() {

    return (

        <div
            className="
                flex
                h-screen
                bg-[#f5f7fb]
                text-black
            "
        >

            <Sidebar />

            <main className="flex-1">

                <Chat />

            </main>

        </div>
    );
}