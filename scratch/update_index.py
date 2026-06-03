import re

with open("static/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replacement 1: Remove background blobs
blobs_block = """    <div class="background-blobs">
        <div class="blob b1"></div>
        <div class="blob b2"></div>
        <div class="blob b3"></div>
    </div>"""

if blobs_block in content:
    content = content.replace(blobs_block, "")
    print("Background blobs removed!")
else:
    # Try fuzzy space match
    pattern = r'\s*<div class="background-blobs">.*?</div>\s*</div>'
    content = re.sub(pattern, "", content, flags=re.DOTALL)
    print("Background blobs removed (regex)!")

# Replacement 2: Update navbar
navbar_block = """    <nav class="navbar">
        <div class="logo">
            <i class="fa-solid fa-brain"></i>
            <span>TruthLens <strong>AI</strong></span>
        </div>
        <div class="nav-links">
            <a href="#" class="nav-link active" data-view="home">Home</a>
            <a href="#" class="nav-link" data-view="dashboard">Dashboard</a>
            <a href="#" class="nav-link" data-view="chat">Chat</a>
            <a href="#" class="nav-link" data-view="about">About</a>
            <a href="#" class="nav-link" data-view="resources">Resources</a>
            <a href="#" class="nav-link" data-view="contact">Contact</a>
            <a href="#" class="nav-link" data-view="settings">Settings</a>
            <a href="#" class="nav-link" data-view="login" id="nav-login-btn">Login</a>
        </div>
        <button class="btn-primary btn-sm" id="new-analysis-btn">
            <i class="fa-solid fa-wand-magic-sparkles"></i> New Analysis
        </button>
    </nav>"""

new_navbar = """    <nav class="navbar">
        <div class="logo" onclick="navigateTo('home')" style="cursor: pointer;">
            <i class="fa-solid fa-brain"></i>
            <span>TruthLens <strong>AI</strong></span>
        </div>
        <div class="nav-links">
            <a href="#" class="nav-link active" data-view="home">Home</a>
            <a href="#" class="nav-link" data-view="dashboard">Dashboard</a>
            <a href="#" class="nav-link" data-view="chat">Chat</a>
            <a href="#" class="nav-link" data-view="home" onclick="setTimeout(() => { document.getElementById('demo-section').scrollIntoView({behavior: 'smooth'}); }, 100);">Analysis</a>
            <a href="#" class="nav-link" data-view="home" onclick="setTimeout(() => { document.getElementById('features-section').scrollIntoView({behavior: 'smooth'}); }, 100);">Features</a>
            <a href="#" class="nav-link" data-view="contact">Contact</a>
            <a href="#" class="nav-link" data-view="settings">Settings</a>
            <a href="#" class="nav-link" data-view="login" id="nav-login-btn">Login</a>
        </div>
        <button class="btn-primary btn-sm" id="new-analysis-btn">
            <i class="fa-solid fa-wand-magic-sparkles"></i> New Analysis
        </button>
    </nav>"""

if navbar_block in content:
    content = content.replace(navbar_block, new_navbar)
    print("Navbar updated!")
else:
    # Try normalization
    normalized_navbar_block = re.sub(r'\s+', ' ', navbar_block).strip()
    # Find matching navbar in content
    # Look for <nav class="navbar">...</nav>
    nav_match = re.search(r'<nav class="navbar">.*?</nav>', content, re.DOTALL)
    if nav_match:
        content = content.replace(nav_match.group(0), new_navbar)
        print("Navbar updated (regex)!")
    else:
        print("Navbar NOT found!")

# Replacement 3: Rebuild Hero section as a split grid layout with statistics section immediately after
hero_block = """        <!-- 1. Hero Section -->
        <section class="hero-section">
            <div class="content-container">
                <div class="hero-badge">
                    <i class="fa-solid fa-sparkles"></i> The New Standard in AI Reliability
                </div>
                <h1>Detect <span class="text-gradient">Hallucinations</span><br>with Mathematical Certainty</h1>
                <p class="hero-subtitle">TruthLens AI identifies factual inconsistencies and logical fallacies in LLM
                    outputs using state-of-the-art NLI and grounding pipelines.</p>
                <div class="hero-actions">
                    <button class="btn-primary btn-lg" id="hero-get-started"
                        onclick="navigateTo('login'); setLoginMode(false);">
                        <i class="fa-solid fa-user-plus"></i> Get Started Free
                    </button>
                    <button class="btn-secondary btn-lg" id="hero-login"
                        onclick="navigateTo('login'); setLoginMode(true);">
                        <i class="fa-solid fa-right-to-bracket"></i> Login
                    </button>
                    <a href="#demo-section" class="btn-secondary btn-lg" style="opacity: 0.8;">
                        <i class="fa-solid fa-vial"></i> Try Live Demo
                    </a>
                </div>

            </div>
        </section>"""

new_hero_stats = """        <!-- 1. Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <div class="hero-badge">
                    <i class="fa-solid fa-sparkles"></i> Academic Research Initiative
                </div>
                <h1>TruthLens AI<br><span class="text-gradient">Reliable AI Response Verification</span></h1>
                <p class="hero-subtitle">Analyze AI-generated responses and detect misleading information using Natural Language Inference, fact verification, and semantic consistency scoring. Ensure your LLM outputs are grounded in truth.</p>
                <div class="hero-actions">
                    <button class="btn-primary btn-lg" id="hero-get-started"
                        onclick="navigateTo('login'); setLoginMode(false);">
                        <i class="fa-solid fa-user-plus"></i> Get Started Free
                    </button>
                    <button class="btn-secondary btn-lg" id="hero-login"
                        onclick="navigateTo('login'); setLoginMode(true);">
                        <i class="fa-solid fa-right-to-bracket"></i> Login
                    </button>
                    <a href="#demo-section" class="btn-secondary btn-lg" style="opacity: 0.8;" onclick="document.getElementById('demo-section').scrollIntoView({behavior: 'smooth'}); return false;">
                        <i class="fa-solid fa-vial"></i> Try Live Demo
                    </a>
                </div>
            </div>
            <div class="hero-visual">
                <div class="hero-mockup-card">
                    <img src="/static/truthlens_hero_mockup.png" alt="TruthLens AI Dashboard Mockup">
                </div>
            </div>
        </section>

        <!-- Statistics Section -->
        <section class="stats-section">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-num">92%</div>
                    <div class="stat-label">Accuracy</div>
                    <div class="stat-sub">Logical check rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num">3</div>
                    <div class="stat-label">AI Models</div>
                    <div class="stat-sub">Simulated core LLMs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num">&lt;2s</div>
                    <div class="stat-label">Response Time</div>
                    <div class="stat-sub">Average latency</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num">500+</div>
                    <div class="stat-label">Test Cases</div>
                    <div class="stat-sub">Academic benchmark size</div>
                </div>
            </div>
        </section>"""

if hero_block in content:
    content = content.replace(hero_block, new_hero_stats)
    print("Hero & Stats updated!")
else:
    # Try fuzzy regex search
    pattern = r'<!-- 1\. Hero Section -->\s*<section class="hero-section">.*?</section>'
    hero_match = re.search(pattern, content, re.DOTALL)
    if hero_match:
        content = content.replace(hero_match.group(0), new_hero_stats)
        print("Hero & Stats updated (regex)!")
    else:
        print("Hero section NOT found!")

# Replacement 4: Features section (Alternating Asymmetric Grid)
features_block = """        <!-- 2. Features Section -->
        <section class="features-section">
            <div class="content-container">
                <div class="section-label"><span class="line"></span> Core Capabilities <span class="line"></span></div>
                <div class="features-grid">
                    <div class="feature-card" onclick="navigateTo('feat-nli')">
                        <div class="icon bg-blue"><i class="fa-solid fa-shield-halved"></i></div>
                        <h3>Multi-Model NLI</h3>
                        <p>Cross-references claims against trusted knowledge bases using Natural Language Inference.</p>
                        <div class="card-footer">
                            <span class="learn-more">Learn More <i class="fa-solid fa-arrow-right"></i></span>
                        </div>
                    </div>
                    <div class="feature-card" onclick="navigateTo('feat-grounding')">
                        <div class="icon bg-teal"><i class="fa-solid fa-magnifying-glass-chart"></i></div>
                        <h3>Grounding Search</h3>
                        <p>Real-time web retrieval to verify time-sensitive facts and current events.</p>
                        <div class="card-footer">
                            <span class="learn-more">Learn More <i class="fa-solid fa-arrow-right"></i></span>
                        </div>
                    </div>
                    <div class="feature-card" onclick="navigateTo('feat-crosscheck')">
                        <div class="icon bg-cyan"><i class="fa-solid fa-layer-group"></i></div>
                        <h3>LLM Cross-Check</h3>
                        <p>Simulates multiple LLMs (GPT, Gemini, Claude) to identify unstable or disputed facts.</p>
                        <div class="card-footer">
                            <span class="learn-more">Learn More <i class="fa-solid fa-arrow-right"></i></span>
                        </div>
                    </div>
                    <div class="feature-card" onclick="navigateTo('feat-heatmap')">
                        <div class="icon bg-purple"><i class="fa-solid fa-fire-flame-curved"></i></div>
                        <h3>Heatmap Analysis</h3>
                        <p>Visualizes token-level uncertainty to pinpoint exactly where the model is guessing.</p>
                        <div class="card-footer">
                            <span class="learn-more">Learn More <i class="fa-solid fa-arrow-right"></i></span>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""

new_features = """        <!-- 2. Features Section -->
        <section id="features-section" class="features-section">
            <div class="section-label"><span class="line"></span> Core Capabilities <span class="line"></span></div>
            
            <!-- Feature 1: Multi-Modal NLI -->
            <div class="feature-row">
                <div class="feature-visual-col">
                    <div class="nli-illustration">
                        <div class="ill-bubble claim">
                            <span class="ill-tag">Claim Extraction</span>
                            <p>"Paris is the capital of Germany."</p>
                        </div>
                        <div class="ill-connector"><i class="fa-solid fa-arrow-down-long"></i></div>
                        <div class="ill-gate">
                            <i class="fa-solid fa-microchip"></i> NLI Verification Engine
                        </div>
                        <div class="ill-connector"><i class="fa-solid fa-arrow-down-long"></i></div>
                        <div class="ill-bubble verdict contradicted">
                            <span class="ill-tag">Fact Check Result</span>
                            <p>Contradiction Detected (92% Confidence)</p>
                        </div>
                    </div>
                </div>
                <div class="feature-text-col">
                    <h3>Multi-Modal NLI</h3>
                    <p>Cross-references generated claims against trusted academic and web knowledge bases. Our Natural Language Inference (NLI) pipeline mathematically parses semantic alignment to detect contradiction and alignment.</p>
                    <button class="btn-primary" type="button" onclick="navigateTo('feat-nli')">View Details <i class="fa-solid fa-arrow-right"></i></button>
                </div>
            </div>

            <!-- Feature 2: Grounding Search -->
            <div class="feature-row">
                <div class="feature-text-col">
                    <h3>Grounding Search</h3>
                    <p>Enables real-time retrieval from search engines and custom databases to verify time-sensitive facts, news, and live statistics. Prevents model hallucinations stemming from outdated training cutoffs.</p>
                    <button class="btn-primary" type="button" onclick="navigateTo('feat-grounding')">View Details <i class="fa-solid fa-arrow-right"></i></button>
                </div>
                <div class="feature-visual-col">
                    <div class="grounding-illustration">
                        <div class="ill-search-bar">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <span>Starbucks CEO 2026</span>
                        </div>
                        <div class="ill-results">
                            <div class="ill-result-card">
                                <div class="ill-res-header"><i class="fa-solid fa-globe"></i> Wikipedia</div>
                                <p>Brian Niccol assumed the role of CEO of Starbucks...</p>
                                <span class="ill-check"><i class="fa-solid fa-circle-check"></i> Grounded</span>
                            </div>
                            <div class="ill-result-card">
                                <div class="ill-res-header"><i class="fa-solid fa-newspaper"></i> CNBC News</div>
                                <p>Starbucks appoints Brian Niccol to lead corporate turnaround...</p>
                                <span class="ill-check"><i class="fa-solid fa-circle-check"></i> Grounded</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Feature 3: Heatmap Analysis -->
            <div class="feature-row">
                <div class="feature-visual-col">
                    <div class="heatmap-illustration">
                        <div class="ill-heatmap-box">
                            <p>
                                The <span class="tok-green">current</span> <span class="tok-green">CEO</span> of <span class="tok-green">Starbucks</span> is <span class="tok-red">Laxman Narasimhan</span>.
                            </p>
                            <div class="ill-tooltip-mock">
                                <div class="tt-header"><i class="fa-solid fa-circle-exclamation"></i> Contradiction</div>
                                <p>Confidence: 12%</p>
                                <p>Reference: Brian Niccol took office in late 2024.</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="feature-text-col">
                    <h3>Heatmap Analysis</h3>
                    <p>Visualizes token-level uncertainty and semantic contradictions directly within the response text. Highlighted visual maps point developers directly to structural guesses and unverified facts.</p>
                    <button class="btn-primary" type="button" onclick="navigateTo('feat-heatmap')">View Details <i class="fa-solid fa-arrow-right"></i></button>
                </div>
            </div>

            <!-- Feature 4: Cross Model Verification -->
            <div class="feature-row">
                <div class="feature-text-col">
                    <h3>Cross Model Verification</h3>
                    <p>Simulates response distributions across multiple models (Llama, GPT, Claude) to measure fact coherence. If independent models generate conflicting answers, stable hallucinations are caught instantly.</p>
                    <button class="btn-primary" type="button" onclick="navigateTo('feat-crosscheck')">View Details <i class="fa-solid fa-arrow-right"></i></button>
                </div>
                <div class="feature-visual-col">
                    <div class="crosscheck-illustration">
                        <div class="ill-model-grid">
                            <div class="ill-model-box ok">
                                <div class="ill-model-name">Llama 3</div>
                                <p>"Brian Niccol"</p>
                            </div>
                            <div class="ill-model-box ok">
                                <div class="ill-model-name">GPT-4</div>
                                <p>"Brian Niccol"</p>
                            </div>
                            <div class="ill-model-box err">
                                <div class="ill-model-name">Claude 3</div>
                                <p>"L. Narasimhan"</p>
                            </div>
                        </div>
                        <div class="ill-consensus-badge">
                            <i class="fa-solid fa-triangle-exclamation"></i>
                            <span>Fact Instability: 66% Consensus</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""

if features_block in content:
    content = content.replace(features_block, new_features)
    print("Features block updated!")
else:
    pattern = r'<!-- 2\. Features Section -->\s*<section class="features-section">.*?</section>'
    feat_match = re.search(pattern, content, re.DOTALL)
    if feat_match:
        content = content.replace(feat_match.group(0), new_features)
        print("Features block updated (regex)!")
    else:
        print("Features section NOT found!")

# Replacement 5: Workflow section
workflow_block = """        <!-- 3. How It Works (Clean Version) -->
        <section class="workflow-section">
            <div class="content-container">
                <div class="section-label"><span class="line"></span> How It Works <span class="line"></span></div>
                <div class="workflow-steps">
                    <div class="ws-item">
                        <div class="ws-icon"><i class="fa-solid fa-i-cursor"></i></div>
                        <h4>Prompt</h4>
                    </div>
                    <div class="ws-connector"></div>
                    <div class="ws-item">
                        <div class="ws-icon"><i class="fa-solid fa-scissors"></i></div>
                        <h4>Extract</h4>
                    </div>
                    <div class="ws-connector"></div>
                    <div class="ws-item">
                        <div class="ws-icon"><i class="fa-solid fa-globe"></i></div>
                        <h4>Ground</h4>
                    </div>
                    <div class="ws-connector"></div>
                    <div class="ws-item">
                        <div class="ws-icon"><i class="fa-solid fa-gauge-high"></i></div>
                        <h4>Score</h4>
                    </div>
                </div>
            </div>
        </section>"""

new_workflow = """        <!-- 3. How It Works -->
        <section class="workflow-section">
            <div class="section-label"><span class="line"></span> Verification Pipeline <span class="line"></span></div>
            <div class="workflow-steps-new">
                <div class="workflow-step-card">
                    <div class="step-num">1</div>
                    <h4>User Input</h4>
                    <p>Submit any prompt and response pair to the diagnostic tool.</p>
                </div>
                <div class="workflow-step-card">
                    <div class="step-num">2</div>
                    <h4>AI Response</h4>
                    <p>The backbone language model generates or runs the initial text.</p>
                </div>
                <div class="workflow-step-card">
                    <div class="step-num">3</div>
                    <h4>TruthLens Verification</h4>
                    <p>Parallel agents verify claims using NLI and web search signals.</p>
                </div>
                <div class="workflow-step-card">
                    <div class="step-num">4</div>
                    <h4>Risk Score + Heatmap</h4>
                    <p>Get a detailed report with highlighted token-level confidence.</p>
                </div>
            </div>
        </section>"""

if workflow_block in content:
    content = content.replace(workflow_block, new_workflow)
    print("Workflow section updated!")
else:
    pattern = r'<!-- 3\. How It Works.*?-->\s*<section class="workflow-section">.*?</section>'
    wf_match = re.search(pattern, content, re.DOTALL)
    if wf_match:
        content = content.replace(wf_match.group(0), new_workflow)
        print("Workflow section updated (regex)!")
    else:
        print("Workflow section NOT found!")

# Replacement 6: Remove old stats section at the bottom of the home view
old_stats_block = """        <!-- 5. Testimonials & Stats -->
        <section class="stats-section">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-num">98%</div>
                    <div class="stat-label">Detection Accuracy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-num">4+</div>
                    <div class="stat-label">Model Integrations</div>
                </div>
                <div class="stat-item">
                    <div class="stat-num">200ms</div>
                    <div class="stat-label">Inference Latency</div>
                </div>
            </div>
        </section>"""

if old_stats_block in content:
    content = content.replace(old_stats_block, "")
    print("Old stats section removed!")
else:
    pattern = r'<!-- 5\. Testimonials & Stats -->\s*<section class="stats-section">.*?</section>'
    stats_match = re.search(pattern, content, re.DOTALL)
    if stats_match:
        content = content.replace(stats_match.group(0), "")
        print("Old stats section removed (regex)!")
    else:
        print("Old stats section NOT found or already removed!")

# Replacement 7: Rebuild footer
footer_block = """        <!-- 6. Footer -->
        <footer class="main-footer">
            <div class="footer-content">
                <div class="footer-logo">
                    <i class="fa-solid fa-brain"></i> TruthLens AI
                </div>
                <div class="footer-links">
                    <a href="#" onclick="navigateTo('home')">Home</a>
                    <a href="#" onclick="navigateTo('about')">About</a>
                    <a href="#" onclick="navigateTo('contact')">Feedback</a>
                    <a href="#" onclick="navigateTo('login')">Sign In</a>
                </div>
                <div class="footer-copy">
                    &copy; 2026 TruthLens AI Research. All rights reserved.
                </div>
            </div>
        </footer>"""

new_footer = """        <!-- 6. Footer -->
        <footer class="main-footer">
            <div class="footer-content">
                <div class="footer-logo">
                    <i class="fa-solid fa-brain"></i> TruthLens <strong>AI</strong>
                </div>
                <div class="footer-links">
                    <a href="#" onclick="navigateTo('home'); return false;">Home</a>
                    <a href="#" onclick="navigateTo('dashboard'); return false;">Dashboard</a>
                    <a href="#" onclick="navigateTo('chat'); return false;">Chat</a>
                    <a href="#" onclick="navigateTo('about'); return false;">About</a>
                    <a href="#" onclick="navigateTo('contact'); return false;">Contact</a>
                    <a href="#" onclick="navigateTo('settings'); return false;">Settings</a>
                </div>
                
                <div class="footer-tech-stack">
                    <span class="footer-tech-badge">React</span>
                    <span class="footer-tech-badge">FastAPI</span>
                    <span class="footer-tech-badge">Transformers</span>
                    <span class="footer-tech-badge">NLP</span>
                    <span class="footer-tech-badge">FAISS</span>
                </div>
                
                <div class="footer-copy">
                    &copy; 2026 TruthLens AI Academic Project. All rights reserved.
                </div>
            </div>
        </footer>"""

if footer_block in content:
    content = content.replace(footer_block, new_footer)
    print("Footer updated!")
else:
    pattern = r'<!-- 6\. Footer -->\s*<footer class="main-footer">.*?</footer>'
    footer_match = re.search(pattern, content, re.DOTALL)
    if footer_match:
        content = content.replace(footer_match.group(0), new_footer)
        print("Footer updated (regex)!")
    else:
        print("Footer NOT found!")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("index.html successfully updated!")
