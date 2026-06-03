import re

# 1. Update static/index.html (workflow section)
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Locate workflow section to replace
workflow_pattern = r'<!-- 3\. How It Works -->\s*<section class="workflow-section">.*?</section>'
new_workflow_html = """<!-- 3. How It Works -->
        <section class="workflow-section">
            <div class="section-label"><span class="line"></span> Verification Pipeline <span class="line"></span></div>
            <div class="workflow-flow-vertical">
                <div class="workflow-box">
                    <div class="workflow-box-icon"><i class="fa-solid fa-keyboard"></i></div>
                    <div class="workflow-box-content">
                        <h4>User Input</h4>
                        <p>Submit any prompt and response pair to the diagnostic tool.</p>
                    </div>
                </div>
                <div class="workflow-arrow-v">
                    <i class="fa-solid fa-arrow-down"></i>
                </div>
                <div class="workflow-box">
                    <div class="workflow-box-icon"><i class="fa-solid fa-robot"></i></div>
                    <div class="workflow-box-content">
                        <h4>AI Response</h4>
                        <p>The backbone language model generates or runs the initial text.</p>
                    </div>
                </div>
                <div class="workflow-arrow-v">
                    <i class="fa-solid fa-arrow-down"></i>
                </div>
                <div class="workflow-box">
                    <div class="workflow-box-icon"><i class="fa-solid fa-shield-halved"></i></div>
                    <div class="workflow-box-content">
                        <h4>TruthLens Verification</h4>
                        <p>Parallel agents verify claims using NLI and web search signals.</p>
                    </div>
                </div>
                <div class="workflow-arrow-v">
                    <i class="fa-solid fa-arrow-down"></i>
                </div>
                <div class="workflow-box">
                    <div class="workflow-box-icon"><i class="fa-solid fa-gauge-high"></i></div>
                    <div class="workflow-box-content">
                        <h4>Risk Score</h4>
                        <p>Get a detailed report with highlighted token-level confidence.</p>
                    </div>
                </div>
            </div>
        </section>"""

if re.search(workflow_pattern, html, re.DOTALL):
    html = re.sub(workflow_pattern, new_workflow_html, html, flags=re.DOTALL)
    print("HTML workflow section updated successfully!")
else:
    print("ERROR: Workflow section pattern not matched in HTML!")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)


# 2. Update static/style.css
with open("static/style.css", "r", encoding="utf-8") as f:
    css = f.read()

# Let's remove the first duplicate/broken hero block
duplicate_block = """/* Split Hero Section */
.hero-section {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 4rem;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 5rem 2rem 5rem;
  min-height: 75vh;
}

@media (max-width: 968px) {
  .hero-section {
    grid-template-columns: 1fr;
    gap: 3rem;
    padding: 3rem 1.5rem;
    text-align: center;
  }
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1.5rem;
}

@media (max-width: 968px) {
  .hero-content {
    align-items: center;
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(79, 70, 229, 0.06);
  border: 1px solid rgba(79, 70, 229, 0.15);
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--primary);
}

.hero-section h1 {
  font-size: 3.2rem;"""

if duplicate_block in css:
    css = css.replace(duplicate_block, "/* Removed duplicate broken hero block */")
    print("CSS duplicate block removed successfully!")
else:
    # Try with slight whitespace normalization
    print("Duplicate block not found exactly. We will search dynamically.")
    normalized_dup = re.sub(r'\s+', ' ', duplicate_block).strip()
    # Let's search using a regex
    pattern = r'/\* Split Hero Section \*/\s*\.hero-section\s*\{.*?\.hero-section\s*h1\s*\{\s*font-size:\s*3\.2rem;'
    if re.search(pattern, css, re.DOTALL):
        css = re.sub(pattern, "/* Removed duplicate broken hero block */", css, flags=re.DOTALL)
        print("CSS duplicate block removed via regex!")
    else:
        print("WARNING: Could not find duplicate block to remove!")

# Append layout overrides at the end of style.css
overrides = """
/* ==========================================
   LAYOUT CORRECTIONS (USER REQUIREMENTS)
   ========================================== */

/* 1. Hero Section Grid & Height */
.hero, .hero-section {
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  align-items: center !important;
  height: 80vh !important;
  min-height: 80vh !important;
  gap: 40px !important;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  box-sizing: border-box;
}

/* 2. Alternating Features Columns */
.feature-row {
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  align-items: center !important;
  gap: 60px !important;
  margin: 100px auto !important;
  max-width: 1200px;
  padding: 0 2rem;
  box-sizing: border-box;
  direction: ltr !important; /* Ensure layout direction is left-to-right */
}

/* Reset any flex/direction alternation from previous stylesheet iterations */
.feature-row:nth-child(even) {
  direction: ltr !important;
}

.feature-row:nth-child(even) .feature-text-col,
.feature-row:nth-child(even) .feature-visual-col {
  direction: ltr !important;
}

/* 3. Statistics Grid & Cards styling */
.stats, .stats-grid {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 30px !important;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  box-sizing: border-box;
}

.stat-card, .stat-item {
  padding: 30px !important;
  background: white !important;
  border-radius: 20px !important;
  box-shadow: 0 8px 20px rgba(0,0,0,.08) !important;
  text-align: center !important;
  transition: all 0.3s ease;
}

.stat-card:hover, .stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px rgba(0,0,0,.12);
}

/* 4. Workflow Section (Centered Flowchart) */
.workflow-flow-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  max-width: 550px;
  margin: 3rem auto 0;
  padding: 0 1.5rem;
}

.workflow-box {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: var(--white);
  border: 1px solid var(--panel-border);
  border-radius: 16px;
  padding: 1.25rem 1.75rem;
  width: 100%;
  box-shadow: var(--shadow-soft);
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.workflow-box:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-premium);
  border-color: var(--primary);
}

.workflow-box-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(79, 70, 229, 0.08);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  flex-shrink: 0;
}

.workflow-box-content {
  text-align: left;
}

.workflow-box-content h4 {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-main);
  margin: 0 0 0.25rem 0;
}

.workflow-box-content p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin: 0;
}

.workflow-arrow-v {
  font-size: 1.5rem;
  color: var(--primary);
  opacity: 0.7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 30px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-5px);
  }
  60% {
    transform: translateY(-2px);
  }
}

/* 5. Dark Navbar */
.navbar {
  background: #161b3d !important;
  color: white !important;
}

.navbar a.nav-link {
  color: rgba(255, 255, 255, 0.7) !important;
}

.navbar a.nav-link:hover, .navbar a.nav-link.active {
  color: #ffffff !important;
}

/* 6. Mobile Responsiveness */
@media(max-width:768px){
  .hero, .hero-section {
    grid-template-columns: 1fr !important;
    height: auto !important;
    min-height: auto !important;
    padding: 3rem 1.5rem !important;
    gap: 30px !important;
    text-align: center;
  }
  
  .hero-content {
    align-items: center !important;
  }
  
  .hero-content h1 {
    text-align: center !important;
    font-size: 2.2rem !important;
  }
  
  .hero-subtitle {
    text-align: center !important;
  }
  
  .hero-actions {
    justify-content: center !important;
  }

  .feature-row {
    grid-template-columns: 1fr !important;
    gap: 40px !important;
    margin: 60px auto !important;
    padding: 0 1.5rem !important;
  }
  
  /* On mobile, stack text above visual for consistency */
  .feature-row .feature-text-col {
    order: 1 !important;
  }
  .feature-row .feature-visual-col {
    order: 2 !important;
  }

  .stats, .stats-grid {
    grid-template-columns: 1fr !important;
    gap: 20px !important;
    padding: 0 1.5rem !important;
  }
  
  .workflow-flow-vertical {
    padding: 0 1rem !important;
  }
}
"""

css += overrides

with open("static/style.css", "w", encoding="utf-8") as f:
    f.write(css)

print("style.css successfully updated with overrides!")
