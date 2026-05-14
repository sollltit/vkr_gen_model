// "use client";

// import { useEffect } from "react";

// import { useRouter } from "next/navigation";

// import Sidebar from "@/components/Sidebar";

// import Chat from "@/components/Chat";

// import { useAuthStore } from "@/store/authStore";


// export default function Home() {

//     const router = useRouter();

//     const user = useAuthStore(
//         (state) => state.user
//     );


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

//             <Sidebar />

//             <Chat />

//         </main>
//     );
// }
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