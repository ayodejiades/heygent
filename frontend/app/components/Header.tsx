"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
  const pathname = usePathname();

  const navItems = [
    { href: "/", label: "Home", icon: "◆" },
    { href: "/task-a", label: "Task A: User Modeling", accent: "teal" },
    { href: "/task-b", label: "Task B: Recommendation", accent: "purple" },
  ];

  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "14px 24px",
        background: "var(--panel-bg)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        border: "1px solid var(--border-color)",
        borderRadius: "var(--radius-lg)",
        marginBottom: "24px",
        boxShadow: "var(--shadow-panel)",
        position: "sticky",
        top: "16px",
        zIndex: 100,
      }}
    >
      <Link href="/" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div>
          <h1
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "24px",
              fontWeight: 800,
              background: "linear-gradient(135deg, var(--text-primary), var(--teal))",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              lineHeight: 1.2,
            }}
          >
            HeyGent
          </h1>
          <p
            style={{
              fontSize: "11px",
              color: "var(--text-muted)",
              fontWeight: 400,
              marginTop: "1px",
            }}
          >
            DSN × BCT Hackathon 3.0
          </p>
        </div>
      </Link>

      <nav style={{ display: "flex", gap: "6px", alignItems: "center" }}>
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const accentColor =
            item.accent === "teal"
              ? "var(--teal)"
              : item.accent === "purple"
              ? "var(--purple)"
              : "var(--text-secondary)";

          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                fontSize: "12px",
                fontWeight: isActive ? 600 : 500,
                padding: "8px 16px",
                borderRadius: "8px",
                color: isActive ? accentColor : "var(--text-secondary)",
                background: isActive ? "rgba(255,255,255,0.05)" : "transparent",
                border: isActive
                  ? `1px solid ${
                      item.accent === "teal"
                        ? "var(--teal-border)"
                        : item.accent === "purple"
                        ? "var(--purple-border)"
                        : "var(--border-color)"
                    }`
                  : "1px solid transparent",
                transition: "all var(--transition-normal)",
                whiteSpace: "nowrap",
              }}
            >
              {item.icon ? `${item.icon} ` : ""}
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div style={{ display: "flex", gap: "8px" }}>
        <span className="badge badge-teal">Gemini 2.5 Flash</span>
        <span className="badge badge-purple">LangGraph</span>
      </div>
    </header>
  );
}
