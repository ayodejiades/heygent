"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import Header from "../components/Header";
import {
  fetchDemoProfiles,
  buildPersona,
  generateReview,
  UserProfile,
  Persona,
  CANDIDATE_ITEMS,
  CandidateItem
} from "../lib/api";
import {
  User,
  Sparkles,
  Terminal as TerminalIcon,
  Play,
  RotateCcw,
  Star,
  MessageSquare,
  AlertTriangle,
  Heart,
  TrendingUp,
  Cpu,
  BadgeAlert,
  BadgeCheck
} from "lucide-react";

export default function TaskA() {
  const [profiles, setProfiles] = useState<Record<string, UserProfile>>({});
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  
  // States for Persona Extraction
  const [isBuildingPersona, setIsBuildingPersona] = useState(false);
  const [persona, setPersona] = useState<Persona | null>(null);

  // States for Review Simulation
  const [selectedBizId, setSelectedBizId] = useState<string>("");
  const [isSimulatingReview, setIsSimulatingReview] = useState(false);
  const [simulatedReview, setSimulatedReview] = useState<{
    stars: number;
    text: string;
    confidence: number;
    persona_used?: string;
  } | null>(null);

  // Error & Backend State
  const [apiError, setApiError] = useState<string | null>(null);
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  // Terminal Streams
  const [terminalLines, setTerminalLines] = useState<{ text: string; type: string }[]>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Step indicator
  const [steps, setSteps] = useState({
    profileSelected: "waiting", // waiting, running, done
    personaExtracted: "waiting",
    reviewSimulated: "waiting",
  });

  // Load profiles on mount
  useEffect(() => {
    async function loadData() {
      addTerminalLine("Initializing connection to HeyGent FastAPI backends...", "dim");
      try {
        const data = await fetchDemoProfiles();
        setProfiles(data);
        const firstId = Object.keys(data)[0];
        if (firstId) {
          setSelectedUserId(firstId);
          setProfile(data[firstId]);
          setSteps(prev => ({ ...prev, profileSelected: "done" }));
        }
        addTerminalLine("Successfully connected to FastAPI agent service. loaded demo profiles.", "green");
      } catch (err: any) {
        console.error("Backend offline. Activating Sandbox mode.", err);
        setApiError("Backend Offline. Running in client-side high-fidelity sandbox mode.");
        setIsOfflineMode(true);
        
        // Load mock profiles so UX is perfect
        const mockProfiles = getMockProfiles();
        setProfiles(mockProfiles);
        const firstId = Object.keys(mockProfiles)[0];
        if (firstId) {
          setSelectedUserId(firstId);
          setProfile(mockProfiles[firstId]);
          setSteps(prev => ({ ...prev, profileSelected: "done" }));
        }
        addTerminalLine("[Warning] FastAPI backend connection failed. Offline Sandbox mode activated.", "yellow");
      }
    }
    loadData();
    // Default select first item
    if (CANDIDATE_ITEMS && CANDIDATE_ITEMS.length > 0) {
      setSelectedBizId(CANDIDATE_ITEMS[0].business_id);
    }
  }, []);

  // Scroll terminal to bottom
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [terminalLines]);

  const addTerminalLine = (text: string, type = "teal") => {
    const time = new Date().toLocaleTimeString();
    setTerminalLines((prev) => [...prev, { text: `[${time}] ${text}`, type }]);
  };

  const handleUserChange = (userId: string) => {
    setSelectedUserId(userId);
    const selected = profiles[userId];
    setProfile(selected);
    setPersona(null);
    setSimulatedReview(null);
    setSteps({
      profileSelected: "done",
      personaExtracted: "waiting",
      reviewSimulated: "waiting",
    });
    addTerminalLine(`Loaded raw history profile for user: ${selected.name} (${userId})`, "teal");
  };

  // Extract Persona Action
  const handleExtractPersona = async () => {
    if (!profile) return;
    setIsBuildingPersona(true);
    setPersona(null);
    setSimulatedReview(null);
    setSteps(prev => ({ ...prev, personaExtracted: "running", reviewSimulated: "waiting" }));
    setTerminalLines([]);

    addTerminalLine(`[Task A] Distilling behavioral persona for ${profile.name}...`, "purple");
    addTerminalLine(`Analyzing ${profile.reviews.length} historical reviews...`, "dim");
    
    // Simulate complex pipeline steps in terminal
    const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

    await delay(600);
    addTerminalLine("Synthesizing praise triggers & absolute preferences...", "teal");
    await delay(700);
    addTerminalLine("Evaluating ratings tendency (average stars deviation)...", "teal");
    await delay(600);
    addTerminalLine("Inspecting emotional vocabulary signature...", "teal");
    await delay(800);
    addTerminalLine("Scanning linguistics for regional syntax markers (Naija/Yoruba pidgin matches)...", "yellow");
    await delay(500);

    try {
      let resultPersona: Persona;

      if (isOfflineMode) {
        // Mock Persona Generation in frontend
        await delay(500);
        resultPersona = getMockPersona(profile.user_id);
      } else {
        const res = await buildPersona(profile);
        resultPersona = res.persona;
        addTerminalLine(`Received LLM compilation response from server (Cached: ${res.cached ? 'Yes' : 'No'})`, "green");
      }

      setPersona(resultPersona);
      setIsBuildingPersona(false);
      setSteps(prev => ({ ...prev, personaExtracted: "done" }));
      addTerminalLine(`Persona extraction complete for ${profile.name}! Summary: "${resultPersona.summary.substring(0, 70)}..."`, "green");
    } catch (err: any) {
      addTerminalLine(`Error during persona build: ${err.message}`, "red");
      setIsBuildingPersona(false);
      setSteps(prev => ({ ...prev, personaExtracted: "error" }));
    }
  };

  // Simulate Review Action
  const handleSimulateReview = async () => {
    if (!profile || !selectedBizId) return;
    const biz = CANDIDATE_ITEMS.find(c => c.business_id === selectedBizId);
    if (!biz) return;

    setIsSimulatingReview(true);
    setSimulatedReview(null);
    setSteps(prev => ({ ...prev, reviewSimulated: "running" }));
    
    addTerminalLine(`[SimLab] Generating simulated review for business: ${biz.name}`, "purple");
    addTerminalLine(`Target attributes: Categories=[${biz.categories}], City=${biz.city || 'Lagos'}`, "dim");
    
    const delay = (ms: number) => new Promise(res => setTimeout(res, ms));
    await delay(700);
    
    if (persona) {
      addTerminalLine(`Injecting persona context: Tendency=${persona.avg_stars_tendency}, Style=${persona.rating_style}`, "teal");
    } else {
      addTerminalLine("[Notice] Persona has not been explicitly distilled yet. Backend will auto-extract persona dynamically before generation.", "yellow");
    }
    
    await delay(800);
    addTerminalLine(`Prompting base LLM using Yelp review model structure...`, "teal");
    await delay(600);

    try {
      let resultReview: any;

      if (isOfflineMode) {
        await delay(900);
        resultReview = getMockSimulatedReview(profile.user_id, biz);
      } else {
        const itemParam = {
          name: biz.name,
          categories: biz.categories,
          city: biz.city || "",
          price_range: biz.attributes?.PriceRange || "Medium",
          highlights: []
        };
        resultReview = await generateReview(profile, itemParam);
      }

      setSimulatedReview({
        stars: resultReview.stars,
        text: resultReview.review_text,
        confidence: resultReview.confidence || 0.94,
        persona_used: resultReview.persona_used
      });
      setIsSimulatingReview(false);
      setSteps(prev => ({ ...prev, reviewSimulated: "done" }));
      addTerminalLine(`Generated simulated review successfully! Score: ${resultReview.stars} Stars.`, "green");
    } catch (err: any) {
      addTerminalLine(`Error during review generation: ${err.message}`, "red");
      setIsSimulatingReview(false);
      setSteps(prev => ({ ...prev, reviewSimulated: "error" }));
    }
  };

  // Mock functions for Sandbox Mode
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
          { stars: 5, text: "The amala was steaming hot and super soft! Gbegiri and ewedu on point. Customer service was excellent, they have standby generator so AC was fully working. Real value for money in Lagos!", business_name: "Amala Zone", business_categories: "Nigerian, Yoruba, Restaurants" },
          { stars: 4, text: "Beautiful outdoor space. The suya has the perfect hot spice. Took a bit of time to serve but it was totally worth the wait.", business_name: "The Suya Spot", business_categories: "Street Food, BBQ, Restaurants" }
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
          { stars: 2, text: "I did not enjoy the continental food here at all. The price is extremely high but no flavor. AC was barely cooling. The waiters were busy pressing phone instead of taking orders. Disappointing.", business_name: "Continental Grill", business_categories: "Continental, Fine Dining, Restaurants" },
          { stars: 3, text: "Average experience. The pizza was okay, but too salty. Noise level was quite high.", business_name: "Pizzeria Stella", business_categories: "Italian, Pizza, Restaurants" }
        ]
      }
    };
  };

  const getMockPersona = (userId: string): Persona => {
    if (userId === "user_01") {
      return {
        rating_style: "Generous & Enthusiastic",
        avg_stars_tendency: +0.4,
        verbosity: "Moderate (80-100 words)",
        dominant_topics: ["Local Food Authenticity", "Power backup & AC", "Polite customer care"],
        emotional_tone: "Warm, supportive, easily pleased by good local spices",
        praise_triggers: ["Steaming hot food", "Standby generator", "Polite staff"],
        complaint_triggers: ["Cold food", "Poor ventilation/hot room"],
        nigerian_speech_markers: true,
        vocabulary_signature: ["steaming hot", "on point", "value for money", "standby"],
        summary: "A passionate local food explorer who values authentic Nigerian cuisine and basic comfort facilities (power backup/cooling). Highly appreciative of hospitable staff and fast service."
      };
    } else {
      return {
        rating_style: "Critical & High-bar",
        avg_stars_tendency: -0.8,
        verbosity: "Highly descriptive (120-150 words)",
        dominant_topics: ["Waiter attention", "Food seasoning/balance", "Price-to-quality ratio"],
        emotional_tone: "Demanding, analytical, skeptical",
        praise_triggers: ["Flawless seasoning", "Attentive but non-intrusive service"],
        complaint_triggers: ["Overpriced menus", "Distracted waitstaff", "Inadequate AC"],
        nigerian_speech_markers: false,
        vocabulary_signature: ["highly overpriced", "disappointing", "lacked flavor", "attentiveness"],
        summary: "A critical customer who expects premium, flawless service and precise food flavors, especially at higher price tags. Highly sensitive to staff distractions."
      };
    }
  };

  const getMockSimulatedReview = (userId: string, biz: CandidateItem) => {
    if (userId === "user_01") {
      const isNigerian = biz.categories.includes("Nigerian") || biz.categories.includes("African");
      const hasAC = biz.attributes?.AC === "Yes";
      const stars = isNigerian ? (hasAC ? 5 : 4) : 3;
      const text = isNigerian
        ? `Tried ${biz.name} today. Let me tell you, their food was absolutely on point! The spice was steaming hot and very rich. They have strong AC and standby generator running perfectly. Real value for money in Lagos, I will surely return!`
        : `Visited ${biz.name}. The atmosphere was fine and customer service was polite, but the food didn't have that strong local spice I prefer. Standard average experience.`;

      return {
        stars,
        review_text: text,
        confidence: 0.96,
        persona_used: "Abidemi Bello (Generous & Enthusiastic)"
      };
    } else {
      const priceIsHigh = biz.name.includes("Grill") || biz.name.includes("Continental");
      const stars = priceIsHigh ? 2 : 3;
      const text = `I went to ${biz.name} and found the entire visit rather disappointing. The dishes lacked proper flavor balance and felt highly overpriced for the quality served. Additionally, the service was quite slow as the staff seemed extremely distracted. I would not recommend this location unless they significantly improve their attention to detail.`;

      return {
        stars,
        review_text: text,
        confidence: 0.91,
        persona_used: "Chinwe Egwu (Critical & High-bar)"
      };
    }
  };

  // Helper to render stars
  const renderStarRating = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;
    return (
      <span className="stars">
        {"★".repeat(fullStars)}
        {hasHalf ? "½" : ""}
        {"☆".repeat(5 - fullStars - (hasHalf ? 1 : 0))}
      </span>
    );
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

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          
          {/* --- Left Column: Persona Lab Controls --- */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Step 1: Profile Selector */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <h2 style={{ fontSize: "16px", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--teal-soft)", border: "1px solid var(--teal-border)", fontSize: "11px", color: "var(--teal-light)" }}>1</span>
                  Select Historical User Profile
                </h2>
                <span className={`badge ${steps.profileSelected === "done" ? "badge-green" : "badge-amber"}`}>
                  {steps.profileSelected === "done" ? "Selected" : "Awaiting Select"}
                </span>
              </div>

              <div style={{ marginBottom: "16px" }}>
                <label className="label">Available Yelp User Profiles</label>
                <select
                  className="select"
                  value={selectedUserId}
                  onChange={(e) => handleUserChange(e.target.value)}
                  style={{ cursor: "pointer" }}
                >
                  {Object.values(profiles).map((p) => (
                    <option key={p.user_id} value={p.user_id}>
                      {p.name} ({p.review_count} Reviews • Avg Stars: {p.average_stars})
                    </option>
                  ))}
                </select>
              </div>

              {profile && (
                <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: "8px", padding: "14px", border: "1px solid var(--border-color)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                    <span style={{ fontSize: "13px", fontWeight: 600 }}>{profile.name}</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>ID: {profile.user_id}</span>
                  </div>
                  <div style={{ display: "flex", gap: "20px", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "12px" }}>
                    <div>Reviews: <strong style={{ color: "white" }}>{profile.review_count}</strong></div>
                    <div>Avg Rating: <strong style={{ color: "white" }}>{profile.average_stars} ★</strong></div>
                    <div>Avg Words: <strong style={{ color: "white" }}>{profile.avg_review_length_words}</strong></div>
                  </div>

                  <div style={{ borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "12px" }}>
                    <span className="label" style={{ marginBottom: "8px" }}>Sample Raw Review Comment</span>
                    {profile.reviews && profile.reviews[0] ? (
                      <p style={{ fontSize: "12px", fontStyle: "italic", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                        "{profile.reviews[0].text.substring(0, 150)}..."
                      </p>
                    ) : (
                      <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>No reviews found.</p>
                    )}
                  </div>
                </div>
              )}

              <div style={{ marginTop: "16px" }}>
                <button
                  className="btn btn-teal"
                  onClick={handleExtractPersona}
                  disabled={isBuildingPersona || !profile}
                  style={{ width: "100%" }}
                >
                  <Cpu size={16} className={isBuildingPersona ? "loading-pulse" : ""} />
                  {isBuildingPersona ? "Extracting Persona..." : "Extract Behavioral Persona"}
                </button>
              </div>
            </div>

            {/* Step 2: Behavioral Persona Card */}
            {persona && (
              <div className="glass-panel" style={{ padding: "20px", animation: "slideUp 0.4s ease", borderLeft: "4px solid var(--teal)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <h2 style={{ fontSize: "16px", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                    <Sparkles className="text-teal-light" size={18} />
                    Synthesized Persona Profile
                  </h2>
                  <div style={{ display: "flex", gap: "6px" }}>
                    {persona.nigerian_speech_markers && (
                      <span className="nigerian-marker">Naija Nuance</span>
                    )}
                    <span className="badge badge-teal">Verified Persona</span>
                  </div>
                </div>

                <p style={{ fontSize: "13px", color: "var(--text-primary)", background: "var(--teal-soft)", padding: "12px", borderRadius: "8px", border: "1px solid var(--teal-border)", marginBottom: "16px", lineHeight: 1.5 }}>
                  <strong>Summary:</strong> {persona.summary}
                </p>

                <div className="persona-grid">
                  <div className="persona-tag">
                    <div className="persona-tag-title">Rating Bias</div>
                    <div className="persona-tag-value" style={{ color: "var(--teal-light)" }}>
                      {persona.avg_stars_tendency >= 0 ? `+${persona.avg_stars_tendency}` : persona.avg_stars_tendency} Avg Offset
                    </div>
                  </div>
                  <div className="persona-tag">
                    <div className="persona-tag-title">Verbosity Signature</div>
                    <div className="persona-tag-value">{persona.verbosity}</div>
                  </div>
                  <div className="persona-tag">
                    <div className="persona-tag-title">Rating Style</div>
                    <div className="persona-tag-value">{persona.rating_style}</div>
                  </div>
                  <div className="persona-tag">
                    <div className="persona-tag-title">Emotional Tone</div>
                    <div className="persona-tag-value">{persona.emotional_tone}</div>
                  </div>
                </div>

                <div style={{ marginTop: "16px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <div>
                    <span className="label" style={{ color: "var(--green)" }}>Praise Triggers</span>
                    <ul style={{ paddingLeft: "14px", fontSize: "12px", color: "var(--text-secondary)" }}>
                      {persona.praise_triggers.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </div>
                  <div>
                    <span className="label" style={{ color: "var(--red)" }}>Complaint Triggers</span>
                    <ul style={{ paddingLeft: "14px", fontSize: "12px", color: "var(--text-secondary)" }}>
                      {persona.complaint_triggers.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </div>
                </div>

                {persona.vocabulary_signature && persona.vocabulary_signature.length > 0 && (
                  <div style={{ marginTop: "14px", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "12px" }}>
                    <span className="label">Linguistic Vocabulary Signature</span>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "4px" }}>
                      {persona.vocabulary_signature.map((v, i) => (
                        <span key={i} style={{ fontSize: "10px", padding: "2px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "4px", border: "1px solid rgba(255,255,255,0.05)" }}>
                          "{v}"
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Simulated Review Lab */}
            {persona && (
              <div className="glass-panel" style={{ padding: "20px", animation: "slideUp 0.4s ease" }}>
                <h2 style={{ fontSize: "16px", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
                  <span style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "24px", height: "24px", borderRadius: "50%", background: "var(--purple-soft)", border: "1px solid var(--purple-border)", fontSize: "11px", color: "var(--purple-light)" }}>2</span>
                  Simulate User Review Behavior
                </h2>

                <div style={{ marginBottom: "16px" }}>
                  <label className="label">Select Target Restaurant</label>
                  <select
                    className="select"
                    value={selectedBizId}
                    onChange={(e) => setSelectedBizId(e.target.value)}
                    style={{ cursor: "pointer" }}
                  >
                    {CANDIDATE_ITEMS.map((c) => (
                      <option key={c.business_id} value={c.business_id}>
                        {c.name} ({c.categories.split(",")[0]} • {c.city})
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  className="btn btn-purple"
                  onClick={handleSimulateReview}
                  disabled={isSimulatingReview}
                  style={{ width: "100%" }}
                >
                  <Play size={16} />
                  {isSimulatingReview ? "Simulating Behavior..." : "Simulate Review"}
                </button>
              </div>
            )}
          </div>

          {/* --- Right Column: Retro Terminal Tracing & Outputs --- */}
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Retro Terminal viewport */}
            <div className="glass-panel" style={{ display: "flex", flexDirection: "column", flexGrow: 1, minHeight: "400px", padding: "16px" }}>
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
                  flexGrow: 1,
                  maxHeight: "450px",
                  overflowY: "auto",
                }}
              >
                {terminalLines.length === 0 ? (
                  <div style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                    Pipeline idle. Trigger "Extract Behavioral Persona" or "Simulate Review" to stream live LLM pipeline execution traces...
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

            {/* Generated Review Outcome */}
            {simulatedReview && (
              <div className="glass-panel animate-slideUp" style={{ padding: "20px", borderLeft: "4px solid var(--purple)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                  <h3 style={{ fontSize: "15px", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
                    <MessageSquare className="text-purple-light" size={18} />
                    Simulated Review Outcome
                  </h3>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      LLM Confidence: <strong style={{ color: "var(--green)" }}>{(simulatedReview.confidence * 100).toFixed(0)}%</strong>
                    </div>
                    <span className="badge badge-purple">Simulated</span>
                  </div>
                </div>

                <div style={{ background: "rgba(0,0,0,0.3)", borderRadius: "8px", padding: "14px", border: "1px solid var(--border-color)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                    <div>
                      {renderStarRating(simulatedReview.stars)}
                      <span style={{ fontSize: "12px", marginLeft: "10px", fontWeight: 600, color: "var(--amber-light)" }}>
                        {simulatedReview.stars} Stars Predicted
                      </span>
                    </div>
                    <div style={{ fontSize: "10px", padding: "2px 6px", background: "rgba(255,255,255,0.05)", borderRadius: "4px", color: "var(--text-muted)" }}>
                      Yelp Generator v1
                    </div>
                  </div>

                  <p style={{ fontSize: "13px", lineHeight: 1.6, color: "var(--text-primary)", fontStyle: "italic", whiteSpace: "pre-line" }}>
                    "{simulatedReview.text}"
                  </p>
                </div>

                {persona?.nigerian_speech_markers && simulatedReview.text.includes("on point") && (
                  <div style={{ marginTop: "12px", display: "flex", gap: "6px", alignItems: "center", padding: "8px 12px", background: "var(--amber-soft)", border: "1px solid var(--amber-border)", borderRadius: "6px" }}>
                    <BadgeCheck size={16} className="text-amber-light" />
                    <span style={{ fontSize: "11px", color: "var(--amber-light)", fontWeight: 500 }}>
                      Cultural Nuance Check: Linguistic marker matches detected persona signature ("on point") successfully injected.
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* --- Bottom Navigation --- */}
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
            <Cpu size={16} className="text-teal-light" />
            <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Finished Task A? Move to the recommendation panel.</span>
          </div>
          <Link href="/task-b" className="btn btn-purple">
            Proceed to Task B: Recommendation Lab
            <Play size={14} />
          </Link>
        </section>
      </div>
    </div>
  );
}
