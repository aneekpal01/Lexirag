import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LexiRAG AI",
  description: "AI legal research assistant with cited answers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <nav className="border-b border-slate-200 bg-white px-6 py-4 flex items-center justify-between">
          <span className="font-semibold text-lg">LexiRAG AI</span>
          <div className="flex gap-4 text-sm">
            <a href="/upload" className="hover:underline">
              Upload
            </a>
            <a href="/chat" className="hover:underline">
              Ask
            </a>
          </div>
        </nav>
        <main className="max-w-3xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
