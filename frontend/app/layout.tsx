import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HeyGent — LLM-Based User Modeling & Recommendation Agents",
  description:
    "Dual-agent system for DSN x BCT Hackathon 3.0. Build agents that understand how people behave, what they want, and what they'll choose next.",
  keywords: [
    "LLM",
    "AI Agent",
    "Recommendation System",
    "User Modeling",
    "Hackathon",
    "LangGraph",
    "Gemini",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="page-bg">{children}</body>
    </html>
  );
}
