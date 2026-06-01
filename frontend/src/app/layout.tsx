import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TopNav } from "@/components/layout/TopNav";
import { LeftNav } from "@/components/layout/LeftNav";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "AI Lead Intelligence",
  description: "Enterprise Lead Intelligence & Opportunity Discovery Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-[var(--color-background)] text-[var(--color-text-primary)] min-h-screen flex flex-col`}>
        <TopNav />
        <div className="flex flex-1 overflow-hidden">
          <LeftNav />
          <main className="flex-1 overflow-y-auto overflow-x-hidden">
            <div className="mx-auto max-w-[1440px] p-6 md:p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
