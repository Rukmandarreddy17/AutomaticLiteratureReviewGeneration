import Link from 'next/link';
import { Sparkles } from 'lucide-react';

const Navbar = () => {
    return (
        <header className="fixed top-0 w-full z-50 border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 max-w-screen-2xl items-center mx-auto px-4">
                <div className="mr-4 hidden md:flex">
                    <Link href="/" className="mr-6 flex items-center space-x-2">
                        <Sparkles className="h-6 w-6 text-indigo-500" />
                        <span className="hidden font-bold sm:inline-block">ResearchAI</span>
                    </Link>
                    <nav className="flex items-center gap-6 text-sm">
                        <Link href="/about" className="transition-colors hover:text-foreground/80 text-foreground/60">About</Link>
                        <Link href="/docs" className="transition-colors hover:text-foreground/80 text-foreground/60">Docs</Link>
                    </nav>
                </div>
                <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                    <div className="w-full flex-1 md:w-auto md:flex-none">
                        {/* Search or command menu placeholder */}
                    </div>
                    <nav className="flex items-center gap-2">
                        <Link href="/login">
                            <button className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                                Log in
                            </button>
                        </Link>
                        <Link href="/signup">
                            <button className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                                Get Started
                            </button>
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    );
};

export default Navbar;
