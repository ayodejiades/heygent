"""
dashboard.py
------------
Stunning, glassmorphic single-page web dashboard for HeyGent.
Exposes Task A and Task B visually with retro Chain-of-Thought terminals,
glowing persona cards, and multi-turn chat refinements.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HeyGent — Agent Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #080d1a;
            --panel-bg: rgba(13, 22, 43, 0.7);
            --card-bg: rgba(255, 255, 255, 0.03);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --teal-accent: #0d9488;
            --teal-glow: rgba(13, 148, 136, 0.4);
            --purple-accent: #7c3aed;
            --purple-glow: rgba(124, 58, 237, 0.4);
            --amber-accent: #f59e0b;
            --amber-glow: rgba(245, 158, 11, 0.4);
            --terminal-bg: #030712;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 10% 20%, rgba(13, 148, 136, 0.1) 0px, transparent 50%),
                radial-gradient(at 90% 80%, rgba(124, 58, 237, 0.08) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
            overflow-x: hidden;
        }

        /* --- Header Section --- */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            background: var(--panel-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        }

        .logo-block {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-title {
            font-family: 'Outfit', sans-serif;
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--text-primary), var(--teal-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .logo-subtitle {
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 400;
            margin-top: 2px;
        }

        .badge-container {
            display: flex;
            gap: 8px;
        }

        .badge {
            font-size: 11px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            background: rgba(255, 255, 255, 0.03);
        }

        .badge.teal {
            color: #2dd4bf;
            border-color: rgba(13, 148, 136, 0.3);
            background: rgba(13, 148, 136, 0.08);
            box-shadow: 0 0 10px rgba(13, 148, 136, 0.1);
        }

        .badge.purple {
            color: #c084fc;
            border-color: rgba(124, 58, 237, 0.3);
            background: rgba(124, 58, 237, 0.08);
            box-shadow: 0 0 10px rgba(124, 58, 237, 0.1);
        }

        /* --- Main Grid Layout --- */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .panel {
            background: var(--panel-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 14px;
        }

        .panel-title {
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .panel-title.teal { color: #2dd4bf; }
        .panel-title.purple { color: #c084fc; }

        /* --- UI Controls --- */
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        select, input, textarea {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            color: var(--text-primary);
            font-size: 14px;
            font-family: inherit;
            transition: all 0.2s ease;
        }

        select:focus, input:focus, textarea:focus {
            outline: none;
            border-color: var(--teal-accent);
            box-shadow: 0 0 10px rgba(13, 148, 136, 0.2);
        }

        .btn {
            background: linear-gradient(135deg, var(--teal-accent), var(--teal-accent));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 15px var(--teal-glow);
        }

        .btn.purple {
            background: linear-gradient(135deg, var(--purple-accent), var(--purple-accent));
        }

        .btn.purple:hover {
            box-shadow: 0 0 15px var(--purple-glow);
        }

        /* --- Custom Cards & Outputs --- */
        .output-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: all 0.3s ease;
        }

        .persona-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .persona-tag {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }

        .persona-tag-title {
            color: var(--text-secondary);
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 2px;
        }

        /* --- Retro Terminal Block --- */
        .terminal {
            background: var(--terminal-bg);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            font-family: 'Fira Code', monospace;
            font-size: 12px;
            padding: 16px;
            height: 200px;
            overflow-y: auto;
            color: #38bdf8;
            box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.8);
        }

        .terminal-line {
            margin-bottom: 6px;
            line-height: 1.4;
        }

        .terminal-line.green { color: #4ade80; }
        .terminal-line.yellow { color: #fbbf24; }

        /* --- Chat Module --- */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 12px;
            border: 1px solid var(--border-color);
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 12px;
            height: 180px;
            overflow-y: auto;
        }

        .chat-bubble {
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 13px;
            line-height: 1.4;
        }

        .chat-bubble.user {
            align-self: flex-end;
            background: rgba(124, 58, 237, 0.2);
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-bottom-right-radius: 2px;
        }

        .chat-bubble.agent {
            align-self: flex-start;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-bottom-left-radius: 2px;
        }

        .chat-input-row {
            display: flex;
            gap: 8px;
        }

        /* --- Recommendation Cards --- */
        .rec-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
            max-height: 380px;
            padding-right: 4px;
        }

        .rec-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            gap: 16px;
            align-items: center;
            transition: all 0.3s ease;
        }

        .rec-card:hover {
            transform: scale(1.01);
            background: rgba(255,255,255,0.04);
            border-color: rgba(124, 58, 237, 0.3);
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.05);
        }

        .rec-rank {
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            font-weight: 800;
            color: var(--purple-accent);
            min-width: 30px;
            text-align: center;
        }

        .rec-info {
            flex-grow: 1;
        }

        .rec-title-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .rec-name {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 15px;
        }

        .rec-rating {
            color: var(--amber-accent);
            font-weight: 600;
            font-size: 13px;
        }

        .rec-reason {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        .confidence-bar-outer {
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            margin-top: 8px;
            width: 100%;
        }

        .confidence-bar-inner {
            height: 100%;
            background: linear-gradient(90deg, var(--purple-accent), var(--teal-accent));
            border-radius: 2px;
        }

        .empty-state {
            color: var(--text-secondary);
            text-align: center;
            padding: 40px 0;
            font-size: 13px;
            font-style: italic;
        }

        .latency-badge {
            font-size: 10px;
            background: rgba(255,255,255,0.08);
            padding: 4px 8px;
            border-radius: 4px;
            color: var(--text-secondary);
        }
    </style>
</head>
<body>

    <!-- --- Header --- -->
    <header>
        <div class="logo-block">
            <div>
                <h1 class="logo-title">HeyGent</h1>
                <p class="logo-subtitle">LLM-Based User Modeling & Recommendation Agents</p>
            </div>
        </div>
        <div class="badge-container">
            <div class="badge teal">TASK A: Review Simulation</div>
            <div class="badge purple">TASK B: ReAct Recommender</div>
            <div class="badge">Gemini 2.5 Flash</div>
        </div>
    </header>

    <!-- --- Main Grid --- -->
    <div class="main-grid">

        <!-- ================================================================= -->
        <!-- PANEL A: USER MODELING & SIMULATION -->
        <!-- ================================================================= -->
        <div class="panel">
            <div class="panel-header">
                <h2 class="panel-title teal">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    Task A: Behavioral Modeling & Simulation
                </h2>
                <div id="cache-indicator" class="latency-badge" style="display: none;">Cached</div>
            </div>

            <!-- Profile Selector -->
            <div class="form-group">
                <label for="profile-select">Select Demo Profile (Cross-Domain Enabled)</label>
                <select id="profile-select" onchange="onProfileChange()">
                    <!-- Populated dynamically -->
                </select>
            </div>

            <!-- History Preview -->
            <div class="form-group">
                <label>Historical Reviews / Preferences Preview</label>
                <div id="history-preview" class="output-card" style="font-size: 12px; max-height: 110px; overflow-y: auto; color: var(--text-secondary);">
                    Select a profile to load details.
                </div>
            </div>

            <!-- CTA: Build Persona -->
            <button class="btn" onclick="triggerBuildPersona()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                Extract Taste Persona
            </button>

            <!-- Persona Displays -->
            <div class="form-group">
                <label>Extracted taste persona profile</label>
                <div id="persona-display" class="output-card">
                    <div class="empty-state">Click 'Extract Taste Persona' above to analyze reviews.</div>
                </div>
            </div>

            <!-- Simulation Review Box -->
            <div style="border-top: 1px solid var(--border-color); padding-top: 20px;" class="form-group">
                <label>Simulate review for unseen item</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                    <div class="form-group">
                        <label for="item-name">Business Name</label>
                        <input id="item-name" type="text" value="The Yellow Chilli">
                    </div>
                    <div class="form-group">
                        <label for="item-categories">Categories</label>
                        <input id="item-categories" type="text" value="Nigerian, Fine Dining">
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                    <div class="form-group">
                        <label for="item-city">City</label>
                        <input id="item-city" type="text" value="Lagos">
                    </div>
                    <div class="form-group">
                        <label for="item-highlights">Highlights</label>
                        <input id="item-highlights" type="text" value="suya, pepper soup, chilled AC, generator">
                    </div>
                </div>

                <button class="btn" onclick="triggerGenerateReview()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    Simulate Rating & Review
                </button>
            </div>

            <!-- Simulated Output Card -->
            <div class="form-group">
                <div id="simulation-output" class="output-card" style="border-color: rgba(13, 148, 136, 0.2);">
                    <div class="empty-state">Configure an item and click 'Simulate Rating & Review' above.</div>
                </div>
            </div>
        </div>

        <!-- ================================================================= -->
        <!-- PANEL B: AGENTIC RECOMMENDATION & REASONING -->
        <!-- ================================================================= -->
        <div class="panel">
            <div class="panel-header">
                <h2 class="panel-title purple">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                    Task B: LangGraph ReAct Recommendation Engine
                </h2>
                <div id="recommend-latency" class="latency-badge">0.0s</div>
            </div>

            <!-- Query context box -->
            <div class="form-group">
                <label for="recommend-query">What are you looking for? (Search Context)</label>
                <input id="recommend-query" type="text" placeholder="e.g. looking for a quiet place with good suya and power backup...">
            </div>

            <!-- CTA: Get Recommendations -->
            <button class="btn purple" onclick="triggerRecommend()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                Generate Ranked Recommendations
            </button>

            <!-- Step-by-Step Chain of Thought Terminal -->
            <div class="form-group">
                <label>LangGraph ReAct Agent Chain of Thought reasoning trace</label>
                <div id="terminal" class="terminal">
                    <div class="terminal-line yellow">&gt; Terminal initialized. Awaiting pipeline execution.</div>
                </div>
            </div>

            <!-- Ranked Output List -->
            <div class="form-group">
                <label>Ranked Recommendations (spec-compliant JSON mapped)</label>
                <div id="recommend-list" class="rec-list">
                    <div class="empty-state">Click 'Generate Ranked Recommendations' to run the agentic pipeline.</div>
                </div>
            </div>

            <!-- Chat refinement container -->
            <div style="border-top: 1px solid var(--border-color); padding-top: 20px;" class="form-group">
                <label>Conversational Refinement Session</label>
                <div id="chat-container" class="chat-container">
                    <div class="chat-bubble agent">Welcome! Generate initial recommendations above, then you can refine them here by giving feedback (e.g. "actually, I prefer pizza" or "somewhere more quiet").</div>
                </div>
                <div class="chat-input-row">
                    <input id="chat-input" type="text" placeholder="Give feedback to refine recommendations..." style="flex-grow: 1;" onkeypress="handleChatKey(event)">
                    <button class="btn purple" style="padding: 12px 20px;" onclick="triggerRefine()">Send</button>
                </div>
            </div>
        </div>

    </div>

    <!-- --- JS Controller Logic --- -->
    <script>
        let demoProfiles = {};
        let activeProfile = {};
        let activePersona = null;
        let currentSessionId = null;

        // Preloaded candidate items for demo search
        const CANDIDATE_ITEMS = [
            {
                "business_id": "philly_biz_1",
                "name": "Mama Cass Restaurant",
                "categories": "Nigerian, African, Restaurants",
                "city": "Lagos",
                "stars": 4.5,
                "attributes": {"WiFi": "Yes", "AC": "Yes", "PowerBackup": "Yes"}
            },
            {
                "business_id": "philly_biz_2",
                "name": "Spice Garden",
                "categories": "African, Restaurants",
                "city": "Lagos",
                "stars": 2.5,
                "attributes": {"AC": "Yes"}
            },
            {
                "business_id": "philly_biz_3",
                "name": "The Suya Spot",
                "categories": "Street Food, Restaurants",
                "city": "Lagos",
                "stars": 4.0,
                "attributes": {"OutdoorSeating": "Yes"}
            },
            {
                "business_id": "philly_biz_4",
                "name": "Pizzeria Stella",
                "categories": "Italian, Pizza, Restaurants",
                "city": "Philadelphia",
                "stars": 4.6,
                "attributes": {"AC": "Yes", "Ambience": "Romantic"}
            },
            {
                "business_id": "philly_biz_5",
                "name": "Quiet Library Cafe",
                "categories": "Cafe, Restaurants, Coffee",
                "city": "Philadelphia",
                "stars": 4.2,
                "attributes": {"Quiet": "Yes", "WiFi": "Yes"}
            }
        ];

        // Fetch demo profiles on mount
        window.onload = async () => {
            try {
                const res = await fetch("/demo-profiles");
                demoProfiles = await res.json();
                
                const select = document.getElementById("profile-select");
                select.innerHTML = "";
                for (const key in demoProfiles) {
                    const option = document.createElement("option");
                    option.value = key;
                    option.textContent = demoProfiles[key].name;
                    select.appendChild(option);
                }
                onProfileChange();
            } catch (err) {
                console.error("Failed to load demo profiles", err);
                appendTerminal("Error loading demo profiles from API.", "red");
            }
        };

        function onProfileChange() {
            const select = document.getElementById("profile-select");
            const profileKey = select.value;
            activeProfile = demoProfiles[profileKey];
            activePersona = null;
            currentSessionId = null;
            
            // Clear outputs
            document.getElementById("persona-display").innerHTML = `<div class="empty-state">Click 'Extract Taste Persona' above to analyze reviews.</div>`;
            document.getElementById("simulation-output").innerHTML = `<div class="empty-state">Configure an item and click 'Simulate Rating & Review' above.</div>`;
            document.getElementById("recommend-list").innerHTML = `<div class="empty-state">Click 'Generate Ranked Recommendations' to run the agentic pipeline.</div>`;
            document.getElementById("chat-container").innerHTML = `<div class="chat-bubble agent">Welcome! Generate initial recommendations above, then you can refine them here by giving feedback.</div>`;
            document.getElementById("cache-indicator").style.display = "none";

            // Render Preview
            const preview = document.getElementById("history-preview");
            let list = activeProfile.reviews.map(r => `• <b>[${r.stars}★] ${r.business_name}</b> (${r.business_categories}): "${r.text.substring(0, 100)}..."`).join("<br><br>");
            preview.innerHTML = `<b>User ID:</b> ${activeProfile.user_id}<br><b>Avg Stars:</b> ${activeProfile.average_stars}★<br><b>Review Count:</b> ${activeProfile.review_count}<br><br><b>History Snippet:</b><br>${list}`;
            
            appendTerminal(`Loaded profile: ${activeProfile.name}. Ready to extract persona.`, "green");
            
            // Set dynamic default context based on profile tastes
            const queryInput = document.getElementById("recommend-query");
            if (activeProfile.user_id === "demo_user_001") {
                queryInput.value = "looking for a quick local suya spot with backup generator";
                document.getElementById("item-name").value = "The Suya Spot";
                document.getElementById("item-categories").value = "Street Food, Restaurants";
                document.getElementById("item-city").value = "Lagos";
                document.getElementById("item-highlights").value = "pepper soup, suya, quick bite";
            } else if (activeProfile.user_id === "demo_sarah_002") {
                queryInput.value = "highly-rated Italian dining spot with quiet romantic ambience and cold AC";
                document.getElementById("item-name").value = "Pizzeria Stella";
                document.getElementById("item-categories").value = "Italian, Pizza, Restaurants";
                document.getElementById("item-city").value = "Philadelphia";
                document.getElementById("item-highlights").value = "wood-fired pizza, romantic, high service";
            } else {
                queryInput.value = "I love books! Recommend a restaurant in Philly matching my reading preference.";
                document.getElementById("item-name").value = "Quiet Library Cafe";
                document.getElementById("item-categories").value = "Cafe, Restaurants, Coffee";
                document.getElementById("item-city").value = "Philadelphia";
                document.getElementById("item-highlights").value = "quiet study tables, library vibe, espresso";
            }
        }

        function appendTerminal(text, color = "") {
            const term = document.getElementById("terminal");
            const line = document.createElement("div");
            line.className = "terminal-line " + color;
            line.textContent = `> ${text}`;
            term.appendChild(line);
            term.scrollTop = term.scrollHeight;
        }

        // --- CTA 1: Extract Taste Persona ---
        async function triggerBuildPersona() {
            appendTerminal("Extracting behavioral taste persona from review history...", "yellow");
            const select = document.getElementById("profile-select");
            
            try {
                const startTime = performance.now();
                const res = await fetch("/build-persona", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(activeProfile)
                });
                
                const data = await res.json();
                activePersona = data.persona;
                const cached = data.cached;
                const duration = ((performance.now() - startTime) / 1000).toFixed(2);
                
                document.getElementById("cache-indicator").style.display = cached ? "inline" : "none";
                document.getElementById("cache-indicator").textContent = cached ? "Cached (Instant)" : `Parsed in ${duration}s`;
                
                // Render Persona Display
                const display = document.getElementById("persona-display");
                display.innerHTML = `
                    <div style="font-size: 14px; font-weight: 700; color: #2dd4bf; margin-bottom: 8px;">
                        ${activePersona.summary}
                    </div>
                    <div class="persona-grid">
                        <div class="persona-tag">
                            <div class="persona-tag-title">Rating Style</div>
                            <b>${activePersona.rating_style || 'Balanced'}</b> (Avg: ${activePersona.avg_stars_tendency || activeProfile.average_stars}★)
                        </div>
                        <div class="persona-tag">
                            <div class="persona-tag-title">Verbosity & Tone</div>
                            <b>${activePersona.verbosity || 'Moderate'}</b> / ${activePersona.emotional_tone || 'Analytical'}
                        </div>
                        <div class="persona-tag" style="grid-column: span 2;">
                            <div class="persona-tag-title">Dominant Topic Focus</div>
                            <b>${(activePersona.dominant_topics || []).join(", ") || "None"}</b>
                        </div>
                        <div class="persona-tag" style="grid-column: span 2;">
                            <div class="persona-tag-title">Vocabulary Signature</div>
                            <span style="font-family: 'Fira Code', monospace; color: #f59e0b;">
                                ${(activePersona.vocabulary_signature || []).map(w => `"${w}"`).join(", ") || "None"}
                            </span>
                        </div>
                        <div class="persona-tag">
                            <div class="persona-tag-title">Nigerian Pidgin/Speech</div>
                            <b>${activePersona.nigerian_speech_markers ? 'YES (Pidgin Enabled)' : 'NO'}</b>
                        </div>
                    </div>
                `;
                appendTerminal(`Persona builder succeeded. Ready to simulate reviews.`, "green");
            } catch (err) {
                appendTerminal(`Error extracting persona: ${err}`, "red");
            }
        }

        // --- CTA 2: Simulate Review ---
        async function triggerGenerateReview() {
            if (!activePersona) {
                appendTerminal("Warning: No persona extracted yet. Extracting persona automatically...", "yellow");
                await triggerBuildPersona();
            }
            
            appendTerminal("Simulating review and stars rating calibrated to persona...", "yellow");
            
            const payload = {
                user_profile: { ...activeProfile, persona: activePersona },
                item: {
                    name: document.getElementById("item-name").value,
                    categories: document.getElementById("item-categories").value,
                    city: document.getElementById("item-city").value,
                    highlights: document.getElementById("item-highlights").value.split(",")
                }
            };

            try {
                const res = await fetch("/generate-review", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                // Star display helper
                let starsStr = "★".repeat(data.stars) + "☆".repeat(5 - data.stars);
                
                const out = document.getElementById("simulation-output");
                out.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:8px; margin-bottom:8px;">
                        <span style="font-weight:700; color:#2dd4bf; font-family:'Outfit';">${payload.item.name}</span>
                        <span style="color:#f59e0b; font-weight:700;">${starsStr} (${data.stars} Stars)</span>
                    </div>
                    <div style="font-size:13px; line-height:1.5; font-style:italic; color:var(--text-primary);">
                        "${data.review_text}"
                    </div>
                    <div style="font-size:10px; color:var(--text-secondary); margin-top:8px; display:flex; justify-content:space-between;">
                        <span>Confidence: <b>${(data.confidence * 100).toFixed(0)}%</b></span>
                        <span>Tone calibrated: <b>Persona Matching Voice</b></span>
                    </div>
                `;
                appendTerminal(`Review simulation complete. Output rating: ${data.stars}★.`, "green");
            } catch (err) {
                appendTerminal(`Error simulating review: ${err}`, "red");
            }
        }

        // --- CTA 3: Get Recommendations ---
        async function triggerRecommend() {
            appendTerminal("Initializing Task B LangGraph ReAct Agent pipeline...", "yellow");
            appendTerminal("NODE 1: 'analyze_intent' - Classifying intent and formulating target search queries...", "blue");
            
            const query = document.getElementById("recommend-query").value;
            const startTime = performance.now();
            
            const payload = {
                user_profile: { ...activeProfile, persona: activePersona },
                candidates: CANDIDATE_ITEMS,
                user_context: query,
                session_id: currentSessionId
            };

            try {
                const res = await fetch("/recommend/session", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                currentSessionId = data.session_id;
                const duration = ((performance.now() - startTime) / 1000).toFixed(2);
                document.getElementById("recommend-latency").textContent = `${duration}s`;
                
                // Append terminal nodes
                appendTerminal("NODE 2: 'retrieve' - Semantically matching candidates in ChromaDB LSA index...", "blue");
                appendTerminal("NODE 3: 'reason_and_score' - Invoking Chain of Thought reasoning...", "blue");
                appendTerminal("Reasoning trace successfully generated inside terminal.", "green");
                
                // Show reasoning in terminal
                appendTerminal("CHAIN OF THOUGHT LOGS:", "yellow");
                const lines = data.reasoning.split("\\n");
                lines.forEach(l => {
                    if (l.trim()) appendTerminal(l, "green");
                });
                
                appendTerminal("NODE 4: 'format_response' - Ranking candidates and returning spec JSON.", "blue");
                
                // Display Recommendations
                renderRecommendations(data.recommendations);
                
                // Add first bubble to chat
                const chat = document.getElementById("chat-container");
                chat.innerHTML = `<div class="chat-bubble agent">Recommendations generated! You can refine these by typing below.</div>`;
                if (data.clarifying_question) {
                    chat.innerHTML += `<div class="chat-bubble agent"><b>Agent Question:</b> ${data.clarifying_question}</div>`;
                }
                chat.scrollTop = chat.scrollHeight;

            } catch (err) {
                appendTerminal(`Error getting recommendations: ${err}`, "red");
            }
        }

        function renderRecommendations(recs) {
            const list = document.getElementById("recommend-list");
            list.innerHTML = "";
            
            if (!recs || recs.length === 0) {
                list.innerHTML = `<div class="empty-state">No matching candidates found.</div>`;
                return;
            }
            
            recs.forEach(r => {
                let starsStr = "★".repeat(Math.round(r.predicted_stars)) + "☆".repeat(5 - Math.round(r.predicted_stars));
                const card = document.createElement("div");
                card.className = "rec-card";
                card.innerHTML = `
                    <div class="rec-rank">#${r.rank}</div>
                    <div class="rec-info">
                        <div class="rec-title-row">
                            <span class="rec-name">${r.item_name}</span>
                            <span class="rec-rating">${starsStr} (${r.predicted_stars}★)</span>
                        </div>
                        <div class="rec-reason">${r.why_this_user}</div>
                        <div class="confidence-bar-outer">
                            <div class="confidence-bar-inner" style="width: ${r.confidence * 100}%;"></div>
                        </div>
                        <div style="font-size: 9px; color: var(--text-secondary); text-align: right; margin-top: 4px;">
                            Match confidence: ${(r.confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                `;
                list.appendChild(card);
            });
        }

        // --- CTA 4: Refine Conversation ---
        async function triggerRefine() {
            const input = document.getElementById("chat-input");
            const feedback = input.value.trim();
            if (!feedback || !currentSessionId) return;
            
            input.value = "";
            
            // Add user bubble
            const chat = document.getElementById("chat-container");
            chat.innerHTML += `<div class="chat-bubble user">${feedback}</div>`;
            chat.scrollTop = chat.scrollHeight;
            
            appendTerminal("NODE 3: 'reason_and_score' - Incorporating feedback in multi-turn state graph...", "yellow");
            
            try {
                const res = await fetch("/recommend/refine", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        feedback: feedback
                    })
                });
                const data = await res.json();
                
                // Show updated reasoning in terminal
                appendTerminal("REFINED REASONING TRACE:", "yellow");
                const lines = data.reasoning.split("\\n");
                lines.forEach(l => {
                    if (l.trim()) appendTerminal(l, "green");
                });
                
                // Re-render
                renderRecommendations(data.recommendations);
                
                // Add agent response bubble
                chat.innerHTML += `<div class="chat-bubble agent">Adjusted recommendations based on your feedback: "${feedback}".</div>`;
                chat.scrollTop = chat.scrollHeight;
                
            } catch (err) {
                appendTerminal(`Error refining session: ${err}`, "red");
            }
        }

        function handleChatKey(e) {
            if (e.key === "Enter") triggerRefine();
        }
    </script>
</body>
</html>
"""
