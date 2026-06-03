import os

css_path = r"c:\Users\palep\OneDrive\Desktop\Harikaaaa\static\style.css"

with open(css_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# We keep the first 5401 lines (1-indexed: 0 to 5400)
kept_lines = lines[:5401]

new_css = """
/* ==========================================================================
   === MODERN SAAS AI REDESIGN ===
   ========================================================================== */
:root {
    --neon-blue: #3b82f6;
    --neon-purple: #8b5cf6;
    --neon-purple-glow: rgba(139, 92, 246, 0.1);
    --neon-blue-glow: rgba(59, 130, 246, 0.1);
    --glass-border: rgba(255, 255, 255, 0.5);
    --glass-bg: rgba(255, 255, 255, 0.7);
    --glass-shadow: 0 15px 35px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.02);
}

[data-theme="dark"] {
    --glass-border: rgba(255, 255, 255, 0.12);
    --glass-bg: rgba(15, 23, 42, 0.85);
    --glass-shadow: 0 20px 45px rgba(0, 0, 0, 0.45);
}

/* Premium Background */
.premium-hero-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 950px;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
}

.premium-hero-bg .grid-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        linear-gradient(rgba(99, 102, 241, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99, 102, 241, 0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse at 50% 50%, black, transparent 75%);
    -webkit-mask-image: radial-gradient(ellipse at 50% 50%, black, transparent 75%);
}

.ambient-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(140px);
    opacity: 0.35;
    mix-blend-mode: screen;
}

.ambient-glow.g1 {
    top: 8%;
    left: 12%;
    width: 480px;
    height: 480px;
    background: radial-gradient(circle, var(--neon-blue) 0%, transparent 80%);
    animation: glow-float 18s infinite alternate ease-in-out;
}

.ambient-glow.g2 {
    top: 20%;
    right: 12%;
    width: 520px;
    height: 520px;
    background: radial-gradient(circle, var(--neon-purple) 0%, transparent 80%);
    animation: glow-float 22s infinite alternate-reverse ease-in-out;
}

@keyframes glow-float {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(60px, 30px) scale(1.1); }
}

/* Hero Layout */
.premium-split-hero {
    position: relative;
    padding-top: 180px; /* Shift content slightly downward */
    padding-bottom: 64px;
    z-index: 10;
}

.premium-hero-container {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 4rem;
    align-items: center;
}

/* Left Side Info */
.hero-left-content {
    text-align: left;
}

.premium-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 99px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(8px);
    color: var(--primary);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 24px; /* Spacing System */
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05);
}

[data-theme="dark"] .premium-hero-badge {
    color: #a5b4fc;
}

.premium-hero-title {
    font-size: 4rem; /* Larger bold typography */
    font-weight: 800;
    line-height: 1.2; /* Better line height */
    letter-spacing: -1.5px;
    color: var(--text-main);
    margin-bottom: 24px; /* Spacing System */
    max-width: 620px; /* Balanced width */
}

.gradient-text-alt {
    background: linear-gradient(135deg, #6366f1, #0ea5e9, #a855f7);
    background-size: 200% 200%;
    animation: gradient-shift 6s infinite alternate ease-in-out;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}

.premium-hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 32px; /* Spacing System */
    max-width: 90%;
}

/* Live Example Card */
.hero-live-example-card {
    display: inline-flex;
    align-items: center;
    gap: 1.25rem;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(12px);
    padding: 0.65rem 1.25rem;
    border-radius: 12px;
    margin-bottom: 32px; /* Spacing System */
    box-shadow: var(--glass-shadow);
    max-width: 100%;
    animation: float-slow-anim-ex 10s infinite alternate ease-in-out;
}

@keyframes float-slow-anim-ex {
    0% { transform: translateY(0); }
    100% { transform: translateY(-4px); }
}

.example-input-wrap {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
}

.ex-lbl {
    color: var(--primary);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.ex-val {
    color: var(--text-main);
    font-weight: 500;
    font-style: italic;
}

.example-arrow {
    color: var(--text-muted);
    opacity: 0.6;
    font-size: 0.95rem;
}

.example-output-wrap {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.badge-verified-glow {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(16, 185, 129, 0.08);
    color: #10b981;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid rgba(16, 185, 129, 0.2);
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.1);
}

.ex-conf-score {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
}

.premium-hero-actions {
    display: flex;
    gap: 1.25rem;
    margin-bottom: 48px; /* Spacing System */
}

.btn-glow {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-glow:hover {
    box-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
    transform: translateY(-2px);
}

.btn-outline {
    background: transparent !important;
    border: 1px solid var(--primary) !important;
    color: var(--primary) !important;
    transition: all 0.3s ease;
}

.btn-outline:hover {
    background: rgba(99, 102, 241, 0.08) !important;
    transform: translateY(-2px);
}

.hero-trust-badges {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
}

.trust-badge {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-muted);
}

.trust-badge i {
    color: #10b981;
}

/* Right Side: Mockup Scene */
.hero-right-content {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    perspective: 1200px;
}

.mockup-scene {
    position: relative;
    width: 100%;
    max-width: 500px;
    height: 480px;
    transform: rotateY(-10deg) rotateX(6deg) rotateZ(-1deg);
    transform-style: preserve-3d;
}

.mockup-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 80%;
    height: 80%;
    transform: translate(-50%, -50%) translateZ(-50px);
    background: radial-gradient(circle, var(--neon-purple-glow) 0%, transparent 70%);
    filter: blur(40px);
}

/* Mockup Card Design */
.mockup-card {
    position: absolute;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(20px); /* Sharper background definition */
    border-radius: 16px;
    box-shadow: var(--glass-shadow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    transform-style: preserve-3d;
}

.mockup-card:hover {
    transform: translateY(-4px) translateZ(10px) !important;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.12);
}

[data-theme="dark"] .mockup-card:hover {
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.55);
}

/* Floating Animations */
.floating-card-slow { animation: float-slow-anim 8s infinite alternate ease-in-out; }
.floating-card-medium { animation: float-med-anim 6.5s infinite alternate ease-in-out; }
.floating-card-fast { animation: float-fast-anim 5s infinite alternate ease-in-out; }

@keyframes float-slow-anim {
    0% { transform: translateY(0) translateZ(0); }
    100% { transform: translateY(-10px) translateZ(8px); }
}

@keyframes float-med-anim {
    0% { transform: translateY(0) translateZ(12px); }
    100% { transform: translateY(-14px) translateZ(20px); }
}

@keyframes float-fast-anim {
    0% { transform: translateY(0) translateZ(24px); }
    100% { transform: translateY(-16px) translateZ(36px); }
}

/* Staggered Floating Cards (Reduced Overlap, Clean Depth Layering) */

/* Card 1: Main Response */
.main-response-card {
    top: 5%;
    left: 0%;
    width: 95%; /* Larger central dashboard */
    z-index: 1;
}

.card-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 1.2rem;
    border-bottom: 1px solid var(--glass-border);
}

.window-dots {
    display: flex;
    gap: 0.4rem;
}

.window-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #10b981; }

.card-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.model-tag {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.2rem 0.5rem;
    background: rgba(99, 102, 241, 0.08);
    border-radius: 4px;
    color: var(--primary);
}

.card-content {
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.claim-bubble {
    background: rgba(0, 0, 0, 0.02);
    border-radius: 10px;
    padding: 0.8rem;
    border: 1px solid rgba(0, 0, 0, 0.03);
}

[data-theme="dark"] .claim-bubble {
    background: rgba(255, 255, 255, 0.02);
    border-color: rgba(255, 255, 255, 0.03);
}

.claim-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.claim-label {
    color: var(--text-muted);
}

.badge-status-verified {
    color: #10b981;
}

.badge-status-contradicted {
    color: #ef4444;
}

.claim-text {
    font-size: 0.85rem;
    line-height: 1.4;
    color: var(--text-main);
}

.hl-green {
    background: rgba(16, 185, 129, 0.12);
    border-bottom: 2px solid #10b981;
    padding: 0.05rem 0.2rem;
    border-radius: 2px;
    font-weight: 500;
}

.hl-red {
    background: rgba(239, 68, 68, 0.12);
    border-bottom: 2px solid #ef4444;
    padding: 0.05rem 0.2rem;
    border-radius: 2px;
    font-weight: 500;
}

/* Card 2: Truth Score */
.truth-score-card {
    top: 52%;
    right: -8%; /* Pushed right and stagger positioning */
    width: 260px;
    z-index: 3;
    padding: 1rem 1.2rem;
}

.gauge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.gauge-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-main);
}

.badge-high-risk {
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    background: rgba(239, 68, 68, 0.08);
    color: #ef4444;
    border-radius: 20px;
    font-weight: 600;
}

.gauge-container {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.circular-chart-mock {
    max-width: 50px;
    max-height: 50px;
}

.circle-bg-mock {
    fill: none;
    stroke: rgba(0, 0, 0, 0.05);
    stroke-width: 3.8;
}

[data-theme="dark"] .circle-bg-mock {
    stroke: rgba(255, 255, 255, 0.05);
}

.circle-path-mock {
    fill: none;
    stroke-width: 3.8;
    stroke-linecap: round;
    stroke: #ef4444;
}

.percentage-mock {
    fill: var(--text-main);
    font-family: inherit;
    font-weight: 700;
    font-size: 0.65em;
    text-anchor: middle;
}

.gauge-info {
    text-align: left;
}

.g-lbl {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-main);
}

.g-desc {
    font-size: 0.65rem;
    color: var(--text-muted);
    line-height: 1.25;
}

/* Card 3: Checklist */
.checklist-card {
    top: 58%;
    left: -10%; /* Staggered offset to bottom left */
    width: 250px;
    z-index: 4;
    padding: 1rem;
}

.checklist-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid var(--glass-border);
    padding-bottom: 0.5rem;
}

.chk-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-main);
}

.pulse-indicator-mock {
    position: relative;
    display: flex;
    width: 8px;
    height: 8px;
}

.ping-mock {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: #3b82f6;
    animation: ping-mock-anim 1.5s infinite;
}

.dot-mock {
    position: relative;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #3b82f6;
}

@keyframes ping-mock-anim {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(2.5); opacity: 0; }
}

.checklist-items-mock {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.chk-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-muted);
}

.chk-item.active {
    color: var(--text-main);
}

.chk-item i {
    font-size: 0.8rem;
}

.chk-item.active i {
    color: #10b981;
}

.chk-item.pending i {
    color: #3b82f6;
}

/* Card 4: Graph Card */
.graph-card {
    top: -12%;
    right: -2%; /* Pushed top right staggered position */
    width: 170px;
    z-index: 2;
    padding: 0.8rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

.graph-info-mock {
    display: flex;
    justify-content: space-between;
    font-size: 0.65rem;
    font-weight: 600;
}

.g-meta-title { color: var(--text-muted); }
.g-meta-val { color: #ef4444; }

.graph-svg-mock {
    margin-top: 0.2rem;
}

/* Decorative Elements */
.deco-element {
    position: absolute;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    color: var(--primary);
    font-size: 0.8rem;
}

.shape-shield { top: 32%; right: -8%; z-index: 2; }
.shape-heartbeat { bottom: 42%; left: 8%; z-index: 2; color: #ef4444; }
.shape-check { top: 12%; left: -6%; z-index: 2; color: #10b981; }

/* === Premium Stats Section === */
.premium-stats-section {
    position: relative;
    padding: 64px 0; /* Spacing System */
    z-index: 10;
}

.stats-grid-premium {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
}

.stat-card-premium {
    position: relative;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    text-align: left; /* Better Alignment */
    box-shadow: var(--glass-shadow);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    min-height: 230px; /* Equal Heights Constraint */
    height: 100%;
}

.stat-card-premium:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.08);
}

.stat-card-premium .scp-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.05) 0%, transparent 60%);
    pointer-events: none;
    transition: transform 0.5s ease;
}

.stat-card-premium:hover .scp-glow {
    transform: translate(10%, 10%);
}

.stat-num-premium {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.75rem;
}

.stat-label-premium {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 0.5rem;
}

.stat-desc-premium {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* === Premium Workflow Section === */
.premium-workflow-section {
    position: relative;
    padding: 64px 0; /* Spacing System */
    z-index: 10;
}

.section-label-premium {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    color: var(--primary);
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 1rem;
}

.section-label-premium .line-alt {
    height: 2px;
    width: 40px;
    background: linear-gradient(90deg, transparent, var(--primary));
}

.section-label-premium .line-alt:last-child {
    background: linear-gradient(90deg, var(--primary), transparent);
}

.section-title-premium {
    font-size: 2.2rem;
    font-weight: 800;
    text-align: center;
    color: var(--text-main);
    margin-bottom: 4rem;
}

.workflow-steps-premium {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
    align-items: center;
    gap: 1rem;
}

.wsp-item {
    position: relative;
    text-align: center;
    padding: 2rem 1.5rem;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.01);
    transition: all 0.3s ease;
}

.wsp-item:hover {
    transform: translateY(-5px);
    border-color: var(--primary);
}

.wsp-num {
    position: absolute;
    top: 1rem;
    right: 1.25rem;
    font-size: 1.8rem;
    font-weight: 900;
    color: rgba(99, 102, 241, 0.08);
}

.wsp-icon {
    width: 55px;
    height: 55px;
    border-radius: 14px;
    background: rgba(99, 102, 241, 0.08);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    color: var(--primary);
    margin-bottom: 1.5rem;
}

.wsp-item h4 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 0.5rem;
}

.wsp-item p {
    font-size: 0.85rem;
    color: var(--text-muted);
    line-height: 1.5;
}

.wsp-connector {
    width: 30px;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    opacity: 0.3;
}

/* Responsive Breakpoints */
@media (max-width: 1024px) {
    .premium-hero-container {
        grid-template-columns: 1fr;
        gap: 5rem;
        text-align: center;
    }
    .hero-left-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .premium-hero-subtitle {
        max-width: 100%;
    }
    .hero-trust-badges {
        justify-content: center;
    }
    .stats-grid-premium {
        grid-template-columns: repeat(2, 1fr);
    }
    .workflow-steps-premium {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    .wsp-connector {
        display: none;
    }
}

@media (max-width: 640px) {
    .premium-hero-title {
        font-size: 2.8rem;
    }
    .stats-grid-premium {
        grid-template-columns: 1fr;
    }
    .mockup-scene {
        transform: none;
        max-width: 100%;
    }
    .truth-score-card {
        right: 2%;
    }
    .checklist-card {
        left: 2%;
    }
}
"""

with open(css_path, "w", encoding="utf-8") as f:
    f.writelines(kept_lines)
    f.write(new_css)

print("CSS Redesign Block successfully updated programmatically.")
