import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/layout/Hero";

export default function Home() {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <Navbar />
      <main className="flex-1">
        <Hero />
      </main>
    </div>
  );
}
