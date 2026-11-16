"use client";

import Link from "next/link";
import { Plus, MessageSquare, LogOut, User as UserIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Chat {
    id: number;
    title: string;
}

export default function Sidebar() {
    const router = useRouter();
    const [chats, setChats] = useState<Chat[]>([]);

    useEffect(() => {
        fetchChats();
    }, []);

    const fetchChats = async () => {
        const token = localStorage.getItem("token");
        if (!token) return;

        try {
            const res = await fetch("http://localhost:8000/api/v1/chats/", {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setChats(data);
            }
        } catch (error) {
            console.error("Failed to fetch chats", error);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        router.push("/login");
    };

    return (
        <div className="flex h-full w-[250px] flex-col border-r bg-muted/40 hidden md:flex">
            <div className="flex h-[60px] items-center px-6">
                <Link href="/" className="flex items-center gap-2 font-semibold">
                    <span className="">ResearchAI</span>
                </Link>
            </div>
            <div className="flex-1 overflow-auto py-2">
                <nav className="grid items-start px-4 text-sm font-medium">
                    <Link
                        href="/chat"
                        // In a real app, this clears selected chat state
                        className="flex items-center gap-3 rounded-lg px-3 py-2 text-primary transition-all hover:text-primary mb-2 border border-dashed border-border"
                    >
                        <Plus className="h-4 w-4" />
                        New Research
                    </Link>
                    <div className="my-2 border-t border-border/50" />
                    <div className="text-xs font-semibold text-muted-foreground mb-2 px-2">History</div>
                    {chats.map((chat) => (
                        <Link
                            key={chat.id}
                            href={`/chat?id=${chat.id}`}
                            className="flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary truncate"
                        >
                            <MessageSquare className="h-4 w-4" />
                            <span className="truncate">{chat.title}</span>
                        </Link>
                    ))}
                </nav>
            </div>
            <div className="mt-auto p-4 border-t">
                <button onClick={handleLogout} className="flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary w-full">
                    <LogOut className="h-4 w-4" />
                    Logout
                </button>
            </div>
        </div>
    );
}
