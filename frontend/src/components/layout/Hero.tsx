"use client";

import { motion } from "framer-motion";
import { ArrowRight, Search } from "lucide-react";

export default function Hero() {
    return (
        <section className="container grid items-center gap-6 pb-8 pt-6 md:py-10 mx-auto px-4 mt-20">
            <div className="flex max-w-[980px] flex-col items-start gap-2">
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-3xl font-extrabold leading-tight tracking-tighter md:text-5xl lg:text-7xl lg:leading-[1.1]"
                >
                    Accelerate your research <br className="hidden sm:inline" />
                    with AI-powered insights.
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="max-w-[750px] text-lg text-muted-foreground sm:text-lg"
                >
                    Instantly analyze research ideas against millions of papers from arXiv, Semantic Scholar, and PubMed. Get structured reports, gap analysis, and future directions in seconds.
                </motion.p>
            </div>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="flex w-full max-w-sm items-center space-x-2 "
            >
                <div className="relative w-full">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <Search className="w-5 h-5 text-gray-500" />
                    </div>
                    <input
                        type="text"
                        className="block w-full p-4 pl-10 text-sm text-foreground bg-background border border-border rounded-lg focus:ring-primary focus:border-primary"
                        placeholder="Describe your research idea..."
                        required
                    />
                    <button type="submit" className="text-white absolute right-2.5 bottom-2.5 bg-primary hover:bg-primary/90 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2">
                        Analyze
                    </button>
                </div>
            </motion.div>
        </section>
    );
}
