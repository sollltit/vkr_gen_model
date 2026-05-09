// "use client";

// import { useEffect } from "react";

// import { useRouter } from "next/navigation";

// import { useAuthStore } from "@/store/authStore";

// import Sidebar from "@/components/Sidebar";


// export default function Home() {

//     const router = useRouter();

//     const user = useAuthStore(
//         (state) => state.user
//     );


//     // =========================
//     // Проверка авторизации
//     // =========================
//     useEffect(() => {

//         if (!user) {

//             router.push("/login");
//         }

//     }, [user]);


//     return (

//         <main
//             className="
//                 flex
//                 h-screen
//                 bg-[#0a0a0a]
//                 text-white
//             "
//         >

//             {/* SIDEBAR */}
//             <Sidebar />


//             {/* MAIN */}
//             <div
//                 className="
//                     flex-1
//                     flex
//                     items-center
//                     justify-center
//                 "
//             >

//                 <div
//                     className="
//                         text-center
//                     "
//                 >

//                     {/* TITLE */}
//                     <h1
//                         className="
//                             text-5xl
//                             font-semibold
//                             mb-4
//                             text-zinc-200
//                         "
//                     >

//                         Создайте чат

//                     </h1>


//                     {/* SUBTITLE */}
//                     <p
//                         className="
//                             text-zinc-500
//                             text-lg
//                         "
//                     >

//                         Начните диалог с моделью

//                     </p>

//                 </div>

//             </div>

//         </main>
//     );
// }

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