"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, useRef, Suspense } from "react";
import { Send, Bot, User, Sparkles, FileText, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
    id: number;
    sender: "user" | "ai";
    content: string;
    timestamp: string;
}

function ChatContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const chatId = searchParams.get("id");

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    // New Research State
    const [idea, setIdea] = useState("");
    const [abstract, setAbstract] = useState("");

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (chatId) {
            fetchMessages(chatId);
        } else {
            setMessages([]);
            setIdea("");
            setAbstract("");
        }
    }, [chatId]);

    const fetchMessages = async (id: string) => {
        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }

        try {
            const res = await fetch(`http://127.0.0.1:8000/api/v1/chats/${id}/messages`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (res.status === 401) {
                localStorage.removeItem("token");
                router.push("/login");
                return;
            }

            if (res.ok) {
                const data = await res.json();
                setMessages(data);
            }
        } catch (error) {
            console.error("Error fetching messages", error);
        }
    };

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!idea.trim()) return;

        setLoading(true);
        const token = localStorage.getItem("token");

        if (!token) {
            router.push("/login");
            return;
        }

        try {
            const res = await fetch("http://127.0.0.1:8000/api/v1/research/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ idea, abstract })
            });

            if (res.status === 401) {
                localStorage.removeItem("token");
                router.push("/login");
                return;
            }

            if (res.ok) {
                const data = await res.json();
                router.push(`/chat?id=${data.chat_id}`);
            }
        } catch (error) {
            console.error("Analysis failed", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || !chatId) return;

        const userMsg: Message = {
            id: Date.now(), // Temp
            sender: "user",
            content: input,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        const token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }

        try {
            const res = await fetch(`http://127.0.0.1:8000/api/v1/chats/${chatId}/messages`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ content: userMsg.content, sender: "user" })
            });

            if (res.status === 401) {
                localStorage.removeItem("token");
                router.push("/login");
                return;
            }

            if (res.ok) {
                const aiMsg = await res.json();
                setMessages(prev => [...prev, aiMsg]);
            }
        } catch (error) {
            console.error("Failed to send message", error);
        } finally {
            setLoading(false);
        }
    };

    if (!chatId) {
        return (
            <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto w-full space-y-8">
                <div className="text-center space-y-4">
                    <div className="bg-primary/10 p-4 rounded-full w-fit mx-auto">
                        <Sparkles className="h-10 w-10 text-primary" />
                    </div>
                    <h1 className="text-3xl font-bold">Start a New Research Analysis</h1>
                    <p className="text-muted-foreground text-lg">
                        Enter your research idea and abstract below. Our AI will analyze existing literature
                        from arXiv, Semantic Scholar, and PubMed to provide structured insights.
                    </p>
                </div>

                <form onSubmit={handleAnalyze} className="w-full space-y-6 bg-card p-8 rounded-xl border shadow-sm">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Research Idea / Topic</label>
                        <input
                            className="flex h-12 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                            placeholder="e.g. AI-driven traffic control systems for smart cities"
                            value={idea}
                            onChange={(e) => setIdea(e.target.value)}
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Abstract (Optional)</label>
                        <textarea
                            className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                            placeholder="Paste your abstract here to get more specific context matching..."
                            value={abstract}
                            onChange={(e) => setAbstract(e.target.value)}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="inline-flex w-full items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                    >
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Analyze Research Gap
                    </button>
                </form>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-[calc(100vh-theme(spacing.20))]">
            <div className="flex-1 overflow-y-auto space-y-6 p-4">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-4 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex gap-3 max-w-[80%] ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                                {msg.sender === 'user' ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                            </div>
                            <div className={`rounded-lg p-4 ${msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                                {msg.sender === 'ai' ? (
                                    <div className="prose prose-sm dark:prose-invert max-w-none">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                ) : (
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4 justify-start">
                        <div className="h-8 w-8 rounded-full flex items-center justify-center shrink-0 bg-muted">
                            <Bot className="h-5 w-5" />
                        </div>
                        <div className="bg-muted rounded-lg p-4 flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">Analyzing literature...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t bg-background">
                <form onSubmit={handleSendMessage} className="relative max-w-4xl mx-auto flex items-center">
                    <input
                        className="flex h-12 w-full rounded-full border border-input bg-transparent px-4 py-2 pr-12 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                        placeholder="Ask a follow-up question..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="absolute right-2 top-2 h-8 w-8 inline-flex items-center justify-center whitespace-nowrap rounded-full text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90"
                    >
                        <Send className="h-4 w-4" />
                    </button>
                </form>
            </div>
        </div>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={<div className="flex h-full items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>}>
            <ChatContent />
        </Suspense>
    );
}
