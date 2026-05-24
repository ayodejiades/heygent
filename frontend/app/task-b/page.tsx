"use client";

import { useState, useEffect, useRef } from "react";
import Header from "../components/Header";
import {
  fetchDemoProfiles,
  getRecommendations,
  startSession,
  refineSession,
  UserProfile,
  Persona,
  Recommendation,
  CANDIDATE_ITEMS,
  CandidateItem
} from "../lib/api";
import {
  Cpu,
  Sparkles,
  MessageSquare,
  Send,
  Sliders,
  Award,
  AlertTriangle,
  RotateCcw,
  Zap,
  CheckCircle,
  ThumbsUp,
  MapPin
} from "lucide-react";

interface ChatMessage {
  sender: "user" | "agent";
  text: string;
  timestamp: string;
}

export default function TaskB() {
  const [profiles, setProfiles] = useState<Record<string, UserProfile>>({});
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  
  // Recommendations States
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [reasoning, setReasoning] = useState<string>("");
  const [clarifyingQuestion, setClarifyingQuestion] = useState<string>("");
  const [isLoadingRecs, setIsLoadingRecs] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Chat/Feedback refinement state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState("");
  const [isSendingFeedback, setIsSendingFeedback] = useState(false);

  // Error & Backend State
  const [apiError, setApiError] = useState<string | null>(null);
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  // Terminal Streams
  const [terminalLines, setTerminalLines] = useState<{ text: string; type: string }[]>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load profiles on mount
  useEffect(() => {
    async function loadData() {
      addTerminalLine("Initializing Task B Dialogical Recommendation Engine...", "dim");
      try {
        const data = await fetchDemoProfiles();
        setProfiles(data);
        const firstId = Object.keys(data)[0];
        if (firstId) {
          setSelectedUserId(firstId);
          setProfile(data[firstId]);
        }
        addTerminalLine("Successfully retrieved user candidate profiles from FastAPIs.", "green");
      } catch (err: any) {
        console.error("Backend offline. Activating Sandbox mode.", err);
        setApiError("Backend Offline. Running in client-side high-fidelity sandbox mode.");
        setIsOfflineMode(true);
        
        const mockProfiles = getMockProfiles();
        setProfiles(mockProfiles);
        const firstId = Object.keys(mockProfiles)[0];
        if (firstId) {
          setSelectedUserId(firstId);
          setProfile(mockProfiles[firstId]);
        }
        addTerminalLine("[Warning] FastAPI backend connection failed. Offline Sandbox mode activated.", "yellow");
      }
    }
    loadData();
  }, []);

  // Scroll terminal to bottom
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [terminalLines]);

  // Scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const addTerminalLine = (text: string, type = "purple") => {
    const time = new Date().toLocaleTimeString();
    setTerminalLines((prev) => [...prev, { text: `[${time}] ${text}`, type }]);
  };

  const handleUserChange = (userId: string) => {
    setSelectedUserId(userId);
    const selected = profiles[userId];
    setProfile(selected);
    setRecs([]);
    setReasoning("");
    setClarifyingQuestion("");
    setSessionId(null);
    setChatMessages([]);
    addTerminalLine(`Switched primary context to user: ${selected.name} (${userId})`, "teal");
  };

  // Generate Recommendations (One-shot / Start Session)
  const handleGenerateRecs = async () => {
    if (!profile) return;
    setIsLoadingRecs(true);
    setRecs([]);
    setReasoning("");
    setChatMessages([]);
    setTerminalLines([]);

    addTerminalLine(`[Task B] Initializing recommendation pipeline for ${profile.name}...`, "purple");
    addTerminalLine(`Loading 8 candidate businesses from Nigerian and US datasets...`, "dim");
    
    const delay = (ms: number) => new Promise(res => setTimeout(res, ms));
    await delay(600);
    addTerminalLine("Aligning user historical reviews (ratings bias, categories frequency)...", "teal");
    await delay(700);
    addTerminalLine("Invoking Multi-Turn LangGraph Recommendation node...", "teal");
    await delay(800);
    addTerminalLine("Re-ranking restaurants by predicted rating alignment...", "teal");
    await delay(500);

    try {
      if (isOfflineMode) {
        // Mock Session start in frontend
        await delay(500);
        const mockResult = getMockRecommendations(profile.user_id, "");
        setRecs(mockResult.recommendations);
        setReasoning(mockResult.reasoning);
        setClarifyingQuestion(mockResult.clarifying_question || "");
        setSessionId("session_mock_123");
        
        // Add greeting message
        const systemMsg: ChatMessage = {
          sender: "agent",
          text: `Hi ${profile.name}! Based on your raw history, I've gathered my top recommendations. ${mockResult.clarifying_question || "Let me know what you think!"}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages([systemMsg]);
      } else {
        // Call FastAPI startSession endpoint
        const res = await startSession(profile, CANDIDATE_ITEMS);
        setRecs(res.recommendations);
        setReasoning(res.reasoning);
        setClarifyingQuestion(res.clarifying_question || "");
        setSessionId(res.session_id);
        addTerminalLine(`FastAPI active session initialized. SessionID: ${res.session_id}`, "green");

        const systemMsg: ChatMessage = {
          sender: "agent",
          text: `Hi ${profile.name}! Based on your Yelp history, here are my top picks. ${res.clarifying_question || "Do you prefer a local spot with AC or perhaps something spicy?"}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages([systemMsg]);
      }

      addTerminalLine("Recommendations successfully compiled and rendered.", "green");
      setIsLoadingRecs(false);
    } catch (err: any) {
      addTerminalLine(`Error during recommendations: ${err.message}`, "red");
      setIsLoadingRecs(false);
    }
  };

  // Conversational Feedback / Refine Session
  const handleSendFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !profile) return;

    const userMsgText = userInput;
    setUserInput("");
    setIsSendingFeedback(true);

    const userMsg: ChatMessage = {
      sender: "user",
      text: userMsgText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatMessages(prev => [...prev, userMsg]);

    addTerminalLine(`[Refiner] Processing user feedback: "${userMsgText}"`, "purple");
    addTerminalLine("Running semantic filter & constraint extractor...", "dim");
    
    const delay = (ms: number) => new Promise(res => setTimeout(res, ms));
    await delay(700);
    addTerminalLine("Updating session state with new conversational preferences...", "teal");
    await delay(800);
    addTerminalLine("Re-scoring candidate catalog with interactive modifiers...", "teal");
    await delay(600);

    try {
      if (isOfflineMode) {
        await delay(500);
        const mockResult = getMockRecommendations(profile.user_id, userMsgText);
        setRecs(mockResult.recommendations);
        setReasoning(mockResult.reasoning);
        setClarifyingQuestion(mockResult.clarifying_question || "");

        const agentMsg: ChatMessage = {
          sender: "agent",
          text: `Excellent. I have updated your preferences based on "${userMsgText}" and re-ordered the recommendations. Let me know if you would like any other adjustments!`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, agentMsg]);
      } else {
        if (!sessionId) {
          throw new Error("No active session. Please click Generate first.");
        }
        const res = await refineSession(sessionId, userMsgText);
        setRecs(res.recommendations);
        setReasoning(res.reasoning);
        setClarifyingQuestion(res.clarifying_question || "");

        const agentMsg: ChatMessage = {
          sender: "agent",
          text: `Perfect. I've re-ranked our listings to match your feedback. ${res.clarifying_question || "What else can I refine for you?"}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, agentMsg]);
      }

      addTerminalLine("Re-ranking complete. Recommendations successfully updated.", "green");
      setIsSendingFeedback(false);
    } catch (err: any) {
      addTerminalLine(`Error refining: ${err.message}`, "red");
      setIsSendingFeedback(false);
    }
  };

  // Mock data functions
  const getMockProfiles = (): Record<string, UserProfile> => {
    return {
      "user_01": {
        user_id: "user_01",
        name: "Abidemi Bello",
        review_count: 14,
        average_stars: 4.6,
        avg_review_length_words: 95,
        rating_distribution: { "5": 9, "4": 4, "3": 1, "2": 0, "1": 0 },
        reviews: [
          { stars: 5, text: "The amala was steaming hot and super soft! Gbegiri and ewedu on point. Customer service was excellent, they have standby generator so AC was fully working. Real value for money in Lagos!", business_name: "Amala Zone", business_categories: "Nigerian, Yoruba, Restaurants" }
        ]
      },
      "user_02": {
        user_id: "user_02",
        name: "Chinwe Egwu",
        review_count: 8,
        average_stars: 2.8,
        avg_review_length_words: 135,
        rating_distribution: { "5": 0, "4": 1, "3": 4, "2": 2, "1": 1 },
        reviews: [
          { stars: 2, text: "I did not enjoy the continental food here at all. The price is extremely high but no flavor.", business_name: "Continental Grill", business_categories: "Continental, Fine Dining, Restaurants" }
        ]
      }
    };
  };

  const getMockRecommendations = (userId: string, feedback: string) => {
    const isVegetarian = feedback.toLowerCase().includes("veg") || feedback.toLowerCase().includes("plant");
    const wantsAC = feedback.toLowerCase().includes("ac") || feedback.toLowerCase().includes("quiet") || feedback.toLowerCase().includes("cool");

    if (userId === "user_01") {
      if (isVegetarian) {
        return {
          user_id: "user_01",
          reasoning: "User is seeking vegetarian food. We filtered street BBQ and focused on Amala Zone (which offers rich vegetarian Ewedu/Gbegiri local platters) and Quiet Library Cafe.",
          clarifying_question: "Do you prefer quick street-side ambiance or a quiet café for your meal?",
          recommendations: [
            { rank: 1, item_id: "biz_amala_zone", item_name: "Amala Zone", predicted_stars: 4.8, confidence: 0.95, why_this_user: "Excellent local Yoruba vegetarian amala with ewedu/gbegiri, aligning perfectly with your preference for steaming hot Nigerian food and local value." },
            { rank: 2, item_id: "biz_library_cafe", item_name: "Quiet Library Cafe", predicted_stars: 4.1, confidence: 0.82, why_this_user: "A highly-rated cafe offering vegetarian sandwiches and a quiet, air-conditioned environment." },
            { rank: 3, item_id: "biz_mama_cass", item_name: "Mama Cass Restaurant", predicted_stars: 4.0, confidence: 0.79, why_this_user: "Traditional local foods with excellent bean-based side dishes." }
          ]
        };
      }

      if (wantsAC) {
        return {
          user_id: "user_01",
          reasoning: "User specifically requested air-conditioned, cool, or quiet locations. Mama Cass and Amala Zone both offer power backup and functional AC.",
          clarifying_question: "Would you like continental dining or authentic Yoruba soup platters?",
          recommendations: [
            { rank: 1, item_id: "biz_mama_cass", item_name: "Mama Cass Restaurant", predicted_stars: 4.9, confidence: 0.97, why_this_user: "Fully air-conditioned standard location with excellent local Nigerian cuisine, power backup, and pristine comfort markers." },
            { rank: 2, item_id: "biz_amala_zone", item_name: "Amala Zone", predicted_stars: 4.7, confidence: 0.93, why_this_user: "A premium local spot featuring outstanding ewedu soup, cooling AC, and reliable power backup." },
            { rank: 3, item_id: "biz_library_cafe", item_name: "Quiet Library Cafe", predicted_stars: 4.2, confidence: 0.88, why_this_user: "A peaceful cafe with high-performance cooling systems, perfect for relaxing away from noisy areas." }
          ]
        };
      }

      // Default
      return {
        user_id: "user_01",
        reasoning: "Abidemi Bello loves authentic local Nigerian food (Yoruba, BBQ, street foods) and values active comfort markers like standby generators and working AC systems.",
        clarifying_question: "I see you love street BBQ, but I've also found some great indoor local spots. Do you want something with AC or do you prefer outdoor street food today?",
        recommendations: [
          { rank: 1, item_id: "biz_suya_spot", item_name: "The Suya Spot", predicted_stars: 4.9, confidence: 0.96, why_this_user: "Incredible barbecued spicy beef suya aligning directly with your love for local street BBQ and perfect spices." },
          { rank: 2, item_id: "biz_amala_zone", item_name: "Amala Zone", predicted_stars: 4.8, confidence: 0.94, why_this_user: "Features outstanding steaming hot local amala and ewedu soup, matching your primary praise triggers of hot local dishes and reliable generator backup." },
          { rank: 3, item_id: "biz_mama_cass", item_name: "Mama Cass Restaurant", predicted_stars: 4.6, confidence: 0.90, why_this_user: "Classic local Nigerian foods, highly functional AC, and excellent customer service records." }
        ]
      };
    } else {
      // User 2: Critical Chinwe
      if (wantsAC) {
        return {
          user_id: "user_02",
          reasoning: "Chinwe is highly critical and requested AC/comfort. We isolated the highest star, air-conditioned places with premium waiter attention.",
          clarifying_question: "Are you interested in high-end Continental fine dining or premium Italian today?",
          recommendations: [
            { rank: 1, item_id: "biz_continental", item_name: "The Continental Grill", predicted_stars: 3.9, confidence: 0.89, why_this_user: "Upscale fine dining atmosphere with functional cooling systems and premium waiter care, fitting your rigorous standards." },
            { rank: 2, item_id: "biz_library_cafe", item_name: "Quiet Library Cafe", predicted_stars: 3.5, confidence: 0.78, why_this_user: "Provides a quiet, intellectual environment with stable AC systems, though coffee options are simple." }
          ]
        };
      }

      // Default
      return {
        user_id: "user_02",
        reasoning: "Chinwe Egwu has a critical rating style (-0.8 offset) and values attentive service, flavor precision, and quiet environments. She strongly complains about overpriced/distracted staff.",
        clarifying_question: "I have excluded low-rated local spots. Do you want to see premium quiet cafes or highly attentive upscale restaurants?",
        recommendations: [
          { rank: 1, item_id: "biz_continental", item_name: "The Continental Grill", predicted_stars: 3.8, confidence: 0.86, why_this_user: "Sophisticated fine dining with upscale reviews. Excellent seasoning precision though a bit expensive, matching your high-bar profile." },
          { rank: 2, item_id: "biz_library_cafe", item_name: "Quiet Library Cafe", predicted_stars: 3.7, confidence: 0.81, why_this_user: "Very quiet bookstore layout with attentive staff, helping you avoid noisy distractors." },
          { rank: 3, item_id: "biz_pizzeria", item_name: "Pizzeria Stella", predicted_stars: 3.4, confidence: 0.75, why_this_user: "High-grade romantic Italian restaurant, though noise levels can occasionally be problematic." }
        ]
      };
    }
  };

  return (
    <div className="page-bg" style={{ minHeight: "100vh" }}>
      <div className="page-container">
        <Header />

        {/* --- API Offline Banner --- */}
        {apiError && (
          <div
            style={{
              background: "var(--amber-soft)",
              border: "1px solid var(--amber-border)",
              borderRadius: "var(--radius-md)",
              padding: "12px 18px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "24px",
              animation: "slideUp 0.3s ease",
            }}
          >
            <AlertTriangle className="text-amber-light" style={{ flexShrink: 0 }} size={20} />
            <div style={{ fontSize: "13px" }}>
              <strong style={{ color: "var(--amber-light)" }}>Sandbox Mode Active:</strong> {apiError}
            </div>
          </div>
        )}

        {/* --- Setup Section --- */}
        <section className="glass-panel" style={{ padding: "20px", marginBottom: "24px" }}>
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <Sliders className="text-purple-light" size={24} />
              <div>
                <h2 style={{ fontSize: "16px", fontWeight: 700 }}>Dialogical Recommendation Lab</h2>
                <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>Target a user profile, fetch agent recommendations, and converse to refine rankings in real-time.</p>
              </div>
            </div>

            <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
              <select
                className="select"
                value={selectedUserId}
                onChange={(e) => handleUserChange(e.target.value)}
                style={{ width: "260px", cursor: "pointer" }}
              >
                {Object.values(profiles).map((p) => (
                  <option key={p.user_id} value={p.user_id}>
                    {p.name} (Avg Stars: {p.average_stars})
                  </option>
                ))}
              </select>

              <button
                className="btn btn-purple"
                onClick={handleGenerateRecs}
                disabled={isLoadingRecs || !profile}
              >
                <Cpu size={16} className={isLoadingRecs ? "loading-pulse" : ""} />
                {isLoadingRecs ? "Computing..." : "Generate Recommendations"}
              </button>
            </div>
          </div>
        </section>

        {/* --- Main Content Grid --- */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "24px" }}>
          
          {/* --- Left Column: Recommendation Results --- */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <div className="glass-panel" style={{ padding: "20px", minHeight: "450px", display: "flex", flexDirection: "column" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", borderBottom: "1px solid rgba(255,255,255,0.05)", paddingBottom: "12px" }}>
                <h3 style={{ fontSize: "15px", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                  <Award className="text-purple-light" size={18} />
                  Top Recommended Spots
                </h3>
                <span className="badge badge-purple">{recs.length} Items Ranked</span>
              </div>

              {recs.length === 0 ? (
                <div style={{ flexGrow: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", padding: "40px" }}>
                  <div style={{ width: "64px", height: "64px", borderRadius: "50%", background: "rgba(255,255,255,0.02)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "16px" }}>
                    <Sliders size={32} />
                  </div>
                  <h4 style={{ color: "var(--text-secondary)", marginBottom: "6px" }}>Recommendations Awaiting</h4>
                  <p style={{ fontSize: "12px", textAlign: "center", maxWidth: "300px" }}>
                    Click "Generate Recommendations" above to let the multi-turn agent score candidate listings for the selected profile.
                  </p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  
                  {/* Reasoning card */}
                  {reasoning && (
                    <div style={{ background: "var(--purple-soft)", border: "1px solid var(--purple-border)", borderRadius: "8px", padding: "14px", marginBottom: "8px" }}>
                      <span className="label" style={{ color: "var(--purple-light)" }}>Agent Reasoning Strategy</span>
                      <p style={{ fontSize: "13px", lineHeight: 1.5, color: "var(--text-primary)" }}>{reasoning}</p>
                    </div>
                  )}

                  {/* Recommendations Cards */}
                  {recs.map((rec) => (
                    <div key={rec.item_id} className="rec-card">
                      <div className="rec-rank">#{rec.rank}</div>
                      
                      <div style={{ flexGrow: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "4px" }}>
                          <div>
                            <h4 style={{ fontSize: "15px", fontWeight: 700, color: "white" }}>{rec.item_name}</h4>
                            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                              ID: {rec.item_id}
                            </span>
                          </div>
                          
                          <div style={{ textAlign: "right" }}>
                            <div className="rec-stars">
                              ★ {rec.predicted_stars.toFixed(1)} <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>predicted</span>
                            </div>
                            <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                              Match: <strong>{(rec.confidence * 100).toFixed(0)}%</strong>
                            </div>
                          </div>
                        </div>

                        {/* Explanation justification balloon */}
                        <div style={{ background: "rgba(0, 0, 0, 0.2)", padding: "10px 12px", borderRadius: "6px", border: "1px solid var(--border-color)", marginTop: "10px", fontSize: "12.5px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                          <strong style={{ color: "var(--teal-light)", display: "block", fontSize: "10px", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "2px" }}>Why this for you</strong>
                          "{rec.why_this_user}"
                        </div>

                        {/* Confidence bar */}
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{ width: `${rec.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}

                </div>
              )}
            </div>
          </div>

          {/* --- Right Column: Chat refinement console --- */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Retro Terminal Viewport */}
            <div className="glass-panel" style={{ padding: "16px", minHeight: "200px" }}>
              <div className="terminal-header">
                <div className="terminal-dot red" />
                <div className="terminal-dot yellow" />
                <div className="terminal-dot green" />
                <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--text-muted)", marginLeft: "10px" }}>
                  HEYGENT_PIPELINE_AGENT://terminal.trace
                </span>
              </div>
              <div
                className="terminal"
                style={{
                  maxHeight: "180px",
                  overflowY: "auto",
                }}
              >
                {terminalLines.length === 0 ? (
                  <div style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                    Pipeline idle. Streamed LangGraph recommendation trace logs appear here...
                  </div>
                ) : (
                  terminalLines.map((line, idx) => (
                    <div key={idx} className={`terminal-line ${line.type}`}>
                      {line.text}
                    </div>
                  ))
                )}
                <div ref={terminalEndRef} />
              </div>
            </div>

            {/* Chat Refinement Dashboard */}
            <div className="glass-panel" style={{ display: "flex", flexDirection: "column", flexGrow: 1, minHeight: "360px", padding: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(255,255,255,0.05)", paddingBottom: "12px", marginBottom: "12px" }}>
                <h3 style={{ fontSize: "14px", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                  <MessageSquare className="text-teal-light" size={16} />
                  Conversational Refinement Console
                </h3>
                <span className="badge badge-teal">Multi-Turn Active</span>
              </div>

              {chatMessages.length === 0 ? (
                <div style={{ flexGrow: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", padding: "20px" }}>
                  <MessageSquare size={24} style={{ opacity: 0.5, marginBottom: "8px" }} />
                  <p style={{ fontSize: "12px", textAlign: "center" }}>Awaiting session initialization. Click "Generate Recommendations" above to start conversational chat.</p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", flexGrow: 1 }}>
                  {/* Chat bubbles container */}
                  <div
                    style={{
                      flexGrow: 1,
                      maxHeight: "220px",
                      overflowY: "auto",
                      paddingRight: "6px",
                      marginBottom: "16px",
                    }}
                  >
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                      {chatMessages.map((msg, i) => (
                        <div
                          key={i}
                          className={`chat-bubble ${msg.sender === "user" ? "user" : "agent"}`}
                          style={{
                            maxWidth: "85%",
                            padding: "10px 14px",
                            borderRadius: "12px",
                            fontSize: "12.5px",
                            lineHeight: 1.5,
                            alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                            background: msg.sender === "user" ? "var(--purple-soft)" : "rgba(255,255,255,0.03)",
                            border: `1px solid ${msg.sender === "user" ? "var(--purple-border)" : "var(--border-color)"}`,
                          }}
                        >
                          <div>{msg.text}</div>
                          <div style={{ fontSize: "9px", color: "var(--text-muted)", textAlign: "right", marginTop: "4px" }}>
                            {msg.timestamp}
                          </div>
                        </div>
                      ))}
                      <div ref={chatEndRef} />
                    </div>
                  </div>

                  {/* Input form */}
                  <form onSubmit={handleSendFeedback} style={{ display: "flex", gap: "10px" }}>
                    <input
                      type="text"
                      className="input"
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      placeholder="e.g. 'I want vegetarian dishes' or 'Find me somewhere quiet with AC'..."
                      disabled={isSendingFeedback}
                      style={{ fontSize: "12.5px" }}
                    />
                    <button
                      type="submit"
                      className="btn btn-teal"
                      disabled={isSendingFeedback || !userInput.trim()}
                      style={{ padding: "10px 16px" }}
                    >
                      {isSendingFeedback ? <Cpu size={14} className="loading-pulse" /> : <Send size={14} />}
                    </button>
                  </form>
                </div>
              )}
            </div>

          </div>
        </div>

        {/* --- Footer Nav --- */}
        <section
          style={{
            marginTop: "40px",
            padding: "24px",
            borderTop: "1px solid var(--border-color)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <CheckCircle size={16} className="text-teal-light" />
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Dual-agent frontend testing environment fully completed.</span>
          </div>
          <button
            className="btn btn-ghost"
            onClick={() => {
              window.location.href = "/";
            }}
          >
            Return to Dashboard Home
          </button>
        </section>
      </div>
    </div>
  );
}
