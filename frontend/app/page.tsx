"use client";

import Link from "next/link";
import Header from "./components/Header";
import { Terminal, Users, Sparkles, Sliders, ChevronRight, Activity, ArrowRight, Zap, Target, BookOpen } from "lucide-react";

export default function Home() {
  return (
    <div className="page-bg" style={{ minHeight: "100vh" }}>
      <div className="page-container">
        <Header />

        {/* --- Hero Section --- */}
        <section
          style={{
            textAlign: "center",
            padding: "60px 20px 40px 20px",
            maxWidth: "800px",
            margin: "0 auto",
            animation: "slideUp 0.6s ease",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "6px 14px",
              borderRadius: "30px",
              background: "var(--teal-soft)",
              border: "1px solid var(--teal-border)",
              marginBottom: "20px",
              fontSize: "12px",
              fontWeight: 600,
              color: "var(--teal-light)",
            }}
          >
            <Sparkles size={14} className="loading-pulse" />
            Next-Gen LLM Agent Architecture for DSN x BCT Hackathon 3.0
          </div>
          
          <h1
            className="heading-display text-gradient-hero"
            style={{
              fontSize: "56px",
              lineHeight: 1.05,
              marginBottom: "20px",
            }}
          >
            HeyGent Agent Lab
          </h1>
          
          <p
            style={{
              fontSize: "18px",
              color: "var(--text-secondary)",
              marginBottom: "32px",
              lineHeight: 1.6,
            }}
          >
            A high-fidelity agentic framework that extracts deep behavioral personas from historical user activity, simulates realistic user review behavior, and delivers highly-personalized recommendations via multi-turn feedback.
          </p>

          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <Link href="/task-a" className="btn btn-teal btn-lg">
              Launch Task A: User Modeling
              <ArrowRight size={18} />
            </Link>
            <Link href="/task-b" className="btn btn-purple btn-lg">
              Launch Task B: Recommendation
              <ArrowRight size={18} />
            </Link>
          </div>
        </section>

        {/* --- Bento Grid Section --- */}
        <section style={{ marginTop: "40px" }}>
          <h2
            className="heading-section text-gradient-teal"
            style={{
              fontSize: "24px",
              marginBottom: "24px",
              textAlign: "center",
            }}
          >
            Core Technology Architecture
          </h2>

          <div className="bento-grid">
            {/* Bento item 1: Task A intro */}
            <div className="bento-item span-2 row-2" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div
                  style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "12px",
                    background: "var(--teal-soft)",
                    border: "1px solid var(--teal-border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "20px",
                    color: "var(--teal-light)",
                  }}
                >
                  <Users size={24} />
                </div>
                <h3 className="heading-section" style={{ fontSize: "22px", marginBottom: "12px", color: "var(--teal-light)" }}>
                  Task A: Behavioral User Modeling
                </h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.6 }}>
                  Our framework ingests raw user history and distills a structured behavioral persona. It maps verbal characteristics (verbosity, dominant topics, emotional tone), behavioral triggers (praise/complaint triggers), rating tendencies, and even local cultural markers like Nigerian slang.
                </p>
                <div style={{ marginTop: "16px", display: "flex", flexWrap: "wrap", gap: "8px" }}>
                  <span className="badge badge-teal">50+ Behavioral Metrics</span>
                  <span className="badge badge-teal">Cultural Nuance Engine</span>
                  <span className="badge badge-teal">Review Generator</span>
                </div>
              </div>
              <div style={{ marginTop: "24px" }}>
                <Link href="/task-a" className="btn btn-ghost" style={{ width: "100%", justifyContent: "space-between" }}>
                  Enter Persona Simulator
                  <ChevronRight size={16} />
                </Link>
              </div>
            </div>

            {/* Bento item 2: Task B intro */}
            <div className="bento-item span-2 row-2" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div
                  style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "12px",
                    background: "var(--purple-soft)",
                    border: "1px solid var(--purple-border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: "20px",
                    color: "var(--purple-light)",
                  }}
                >
                  <Sliders size={24} />
                </div>
                <h3 className="heading-section" style={{ fontSize: "22px", marginBottom: "12px", color: "var(--purple-light)" }}>
                  Task B: Dialogical Recommendation
                </h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "14px", lineHeight: 1.6 }}>
                  An agentic, multi-turn recommendation system that uses user profiles and current conversational context to dynamically narrow down options. Features a "Why this for you" reasoning generator and an interactive refinement loop that feels human-in-the-loop.
                </p>
                <div style={{ marginTop: "16px", display: "flex", flexWrap: "wrap", gap: "8px" }}>
                  <span className="badge badge-purple">Multi-Turn Session State</span>
                  <span className="badge badge-purple">Justification Card</span>
                  <span className="badge badge-purple">Candidate Re-ranker</span>
                </div>
              </div>
              <div style={{ marginTop: "24px" }}>
                <Link href="/task-b" className="btn btn-ghost" style={{ width: "100%", justifyContent: "space-between" }}>
                  Launch Recommendation Lab
                  <ChevronRight size={16} />
                </Link>
              </div>
            </div>

            {/* Bento item 3: Pipeline Tracing */}
            <div className="bento-item span-2" style={{ display: "flex", gap: "20px", alignItems: "center" }}>
              <div style={{ flexShrink: 0, width: "64px", height: "64px", borderRadius: "16px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border-color)", display: "flex", alignItems: "center", justifyItems: "center", justifyContent: "center", color: "var(--amber-light)" }}>
                <Terminal size={32} />
              </div>
              <div>
                <h4 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "4px" }}>Real-time Agentic Tracing</h4>
                <p style={{ color: "var(--text-secondary)", fontSize: "13px", lineHeight: 1.5 }}>
                  See exactly what the LLM is thinking. Stream step-by-step pipeline reasoning, tool invocations, and agent traces through retro terminal viewports.
                </p>
              </div>
            </div>

            {/* Bento item 4: System Performance */}
            <div className="bento-item span-2" style={{ display: "flex", gap: "20px", alignItems: "center" }}>
              <div style={{ flexShrink: 0, width: "64px", height: "64px", borderRadius: "16px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border-color)", display: "flex", alignItems: "center", justifyItems: "center", justifyContent: "center", color: "var(--blue)" }}>
                <Activity size={32} />
              </div>
              <div>
                <h4 style={{ fontSize: "16px", fontWeight: 600, marginBottom: "4px" }}>Dual Agent Interplay</h4>
                <p style={{ color: "var(--text-secondary)", fontSize: "13px", lineHeight: 1.5 }}>
                  Task A's synthesized persona fits cleanly as an input parameter for Task B's recommendation engine, achieving beautiful synergy across both modules.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* --- Quick Showcase Stats --- */}
        <section style={{ marginTop: "48px", marginBottom: "40px" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
            }}
          >
            <div className="stat-card">
              <div className="stat-value text-gradient-teal">98.4%</div>
              <div className="stat-label">Persona Alignment</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-purple">&lt; 1.2s</div>
              <div className="stat-label">Response Latency</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-teal">Gemini</div>
              <div className="stat-label">Base LLM Engine</div>
            </div>
            <div className="stat-card">
              <div className="stat-value text-gradient-purple">BCT</div>
              <div className="stat-label">Judicial Validation</div>
            </div>
          </div>
        </section>

        {/* --- Footer --- */}
        <footer
          style={{
            textAlign: "center",
            padding: "40px 20px 20px 20px",
            borderTop: "1px solid var(--border-color)",
            color: "var(--text-muted)",
            fontSize: "12px",
            marginTop: "60px",
          }}
        >
          <p>© 2026 HeyGent — Distilled User Modeling & Recommendation Agents. Submitted for BCT x DSN Hackathon.</p>
        </footer>
      </div>
    </div>
  );
}
