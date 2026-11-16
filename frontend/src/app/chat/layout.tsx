"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/chat/Sidebar";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
        }
    }, [router]);

    return (
        <div className="flex min-h-screen w-full">
            <Sidebar />
            <div className="flex flex-col flex-1 min-h-screen">
                {/* Mobile Header could go here */}
                <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6 bg-background">
                    {children}
                </main>
            </div>
        </div>
    );
}
