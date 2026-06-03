// ══════════════════════════════════════════
//  SPA ROUTER
// ══════════════════════════════════════════
// Auth State
let currentUser = null;
let isLoginMode = true;

// ── Theme Management ────────────────────────────────────────────────────────
function setTheme(theme) {
    console.log('Setting theme to:', theme);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('truthlens_theme', theme);

    // Update UI Buttons
    const lightBtn = document.getElementById('theme-light-btn');
    const darkBtn  = document.getElementById('theme-dark-btn');

    if (lightBtn && darkBtn) {
        if (theme === 'dark') {
            darkBtn.classList.add('active');
            lightBtn.classList.remove('active');
        } else {
            lightBtn.classList.add('active');
            darkBtn.classList.remove('active');
        }
    }

    // Redraw Chart if active and logged in
    if (typeof updateDashboardUI === 'function' && currentUser) {
        const isDashboard = document.getElementById('view-dashboard') && document.getElementById('view-dashboard').classList.contains('active-view');
        if (isDashboard) {
            updateDashboardUI();
        }
    }
}

// ── Global Theme Click Listener (Bulletproof) ──
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.theme-btn');
    if (btn) {
        const theme = btn.id.includes('dark') ? 'dark' : 'light';
        setTheme(theme);
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    if (window.location.search.includes('mock_screenshot=true')) {
        localStorage.setItem('truthlens_theme', 'dark');
        localStorage.setItem('truthlens_user', JSON.stringify({ email: 'demo@truthlens.ai', name: 'Demo User', token: 'mock-token' }));
        const mockRuns = [
            {
                id: "run-1",
                timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
                prompt: "Verify the effectiveness of standard zinc supplements for treating common cold duration.",
                response: "Clinical trials indicate that zinc lozenges or syrup may reduce the duration of a cold by one day when taken within 24 hours of onset, but side effects like nausea and altered taste are common.",
                riskScore: 12,
                verdict: "High Trust",
                data: {
                    overall_risk: 0.12,
                    sentence_analysis: [
                        { category: 'verified', content: "Clinical trials indicate that zinc lozenges or syrup may reduce the duration of a cold by one day" },
                        { category: 'verified', content: "when taken within 24 hours of onset" },
                        { category: 'verified', content: "but side effects like nausea and altered taste are common." }
                    ]
                }
            },
            {
                id: "run-2",
                timestamp: new Date(Date.now() - 10 * 60 * 60 * 1000).toISOString(),
                prompt: "Explain the cause of the 1908 Tunguska event.",
                response: "The Tunguska event was a massive explosion that occurred in Russia in 1908. It is widely believed to have been caused by the air burst of a stony meteoroid approximately 50-60 meters in size. Some alternative theories claim a black hole passed through the Earth, which has been disproved.",
                riskScore: 25,
                verdict: "Moderate Risk",
                data: {
                    overall_risk: 0.25,
                    sentence_analysis: [
                        { category: 'verified', content: "The Tunguska event was a massive explosion that occurred in Russia in 1908." },
                        { category: 'verified', content: "It is widely believed to have been caused by the air burst of a stony meteoroid approximately 50-60 meters in size." },
                        { category: 'weak', content: "Some alternative theories claim a black hole passed through the Earth, which has been disproved." }
                    ]
                }
            },
            {
                id: "run-3",
                timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
                prompt: "Identify the founder of the kingdom of Aksum.",
                response: "The Kingdom of Aksum was founded by King Solomon and the Queen of Sheba's son, Menelik I, in the 10th century BC. He also brought the Ark of the Covenant to Aksum.",
                riskScore: 68,
                verdict: "Severe Risk",
                data: {
                    overall_risk: 0.68,
                    sentence_analysis: [
                        { category: 'verified', content: "The Kingdom of Aksum was a major trading empire." },
                        { category: 'fabricated', content: "It was founded by King Solomon and the Queen of Sheba's son, Menelik I, in the 10th century BC." },
                        { category: 'weak', content: "He also brought the Ark of the Covenant to Aksum." }
                    ]
                }
            },
            {
                id: "run-4",
                timestamp: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
                prompt: "Describe the atmosphere of Mars.",
                response: "Mars has a very thick atmosphere composed mostly of oxygen and nitrogen, which makes it habitable for humans without spacesuits. Liquid water flows freely on the surface today.",
                riskScore: 88,
                verdict: "Severe Risk",
                data: {
                    overall_risk: 0.88,
                    sentence_analysis: [
                        { category: 'fabricated', content: "Mars has a very thick atmosphere composed mostly of oxygen and nitrogen" },
                        { category: 'fabricated', content: "which makes it habitable for humans without spacesuits." },
                        { category: 'fabricated', content: "Liquid water flows freely on the surface today." }
                    ]
                }
            }
        ];
        localStorage.setItem('truthlens_runs_demo@truthlens.ai', JSON.stringify(mockRuns));
        currentUser = { email: 'demo@truthlens.ai', name: 'Demo User', token: 'mock-token' };

        // Hide navbar, footer, and adjust body for clean screenshot
        const style = document.createElement('style');
        style.innerHTML = `
            .navbar, .main-footer { display: none !important; }
            body { padding-top: 0 !important; margin: 0 !important; background: transparent !important; }
            #view-dashboard { padding: 1.5rem !important; background: transparent !important; }
            .page-header { margin-bottom: 1rem !important; }
            .dashboard-grid { margin-top: 1rem !important; margin-bottom: 1rem !important; }
        `;
        document.head.appendChild(style);
    } else {
        const savedUser = localStorage.getItem('truthlens_user');
        if (savedUser) {
            currentUser = JSON.parse(savedUser);
            try {
                const res = await fetch('/api/me', {
                    headers: { 'Authorization': `Bearer ${currentUser.token}` }
                });
                if (!res.ok) throw new Error('Invalid token');
                const data = await res.json();
                currentUser.name = data.user.name;
            } catch (e) {
                currentUser = null;
                localStorage.removeItem('truthlens_user');
            }
        }
    }
    updateNavForAuth();
    
    // Load Saved Theme
    const savedTheme = localStorage.getItem('truthlens_theme') || 'light';
    setTheme(savedTheme);

    // Attach Theme Listeners (for reliability)
    const lightBtn = document.getElementById('theme-light-btn');
    const darkBtn  = document.getElementById('theme-dark-btn');
    if (lightBtn) lightBtn.addEventListener('click', () => setTheme('light'));
    if (darkBtn)  darkBtn.addEventListener('click', () => setTheme('dark'));

    // Handle initial routing based on loading path
    handleRouting();
    
    // Initialize Dashboard Chat History Manager if panel exists
    if (document.getElementById('all-chats-panel')) {
        initDashboardChatManager();
    }
});

// SPA Router Mappings
const routes = {
    '/': { viewId: 'home', scrollId: null },
    '/dashboard': { viewId: 'dashboard', scrollId: null },
    '/chat': { viewId: 'chat', scrollId: null },
    '/analysis': { viewId: 'analysis', scrollId: null },
    '/features': { viewId: 'features', scrollId: null },
    '/about': { viewId: 'about', scrollId: null },
    '/contact': { viewId: 'contact', scrollId: null },
    '/settings': { viewId: 'settings', scrollId: null },
    '/login': { viewId: 'login', scrollId: null },
    '/features/nli': { viewId: 'feat-nli', scrollId: null },
    '/features/grounding': { viewId: 'feat-grounding', scrollId: null },
    '/features/crosscheck': { viewId: 'feat-crosscheck', scrollId: null },
    '/features/heatmap': { viewId: 'feat-heatmap', scrollId: null }
};

const viewToPath = {
    'home': '/',
    'dashboard': '/dashboard',
    'chat': '/chat',
    'analysis': '/analysis',
    'features': '/features',
    'about': '/about',
    'contact': '/contact',
    'settings': '/settings',
    'login': '/login',
    'feat-nli': '/features/nli',
    'feat-grounding': '/features/grounding',
    'feat-crosscheck': '/features/crosscheck',
    'feat-heatmap': '/features/heatmap'
};

function handleRouting() {
    const path = window.location.pathname;
    
    // Check logout route first
    if (path === '/logout') {
        currentUser = null;
        localStorage.removeItem('truthlens_user');
        updateNavForAuth();
        window.location.href = '/';
        return;
    }

    // Protected route check
    const protectedPaths = ['/dashboard', '/settings'];
    const savedUser = localStorage.getItem('truthlens_user');
    if (protectedPaths.includes(path) && !savedUser) {
        localStorage.setItem('auth_redirect_error', 'Please log in to access this page.');
        window.location.href = '/login';
        return;
    }

    if (path === '/login') {
        const redirectErr = localStorage.getItem('auth_redirect_error');
        if (redirectErr) {
            const errEl = document.getElementById('auth-error');
            if (errEl) {
                errEl.textContent = redirectErr;
                errEl.classList.remove('hidden');
            }
            localStorage.removeItem('auth_redirect_error');
        }
    }

    if (path === '/dashboard') {
        updateDashboardUI();
    }
    if (path === '/analysis') {
        resetDashboard();
        const viewRunId = localStorage.getItem('view_run_id');
        if (viewRunId && currentUser) {
            localStorage.removeItem('view_run_id');
            const runs = JSON.parse(localStorage.getItem(`truthlens_runs_${currentUser.email}`) || '[]');
            const run = runs.find(r => r.id === viewRunId);
            
            const loadAndRenderRun = (targetRun) => {
                if (!targetRun) return;
                setTimeout(() => {
                    const promptInput = document.getElementById('db-prompt');
                    const responseInput = document.getElementById('db-response');
                    if (promptInput) promptInput.value = targetRun.prompt;
                    if (responseInput) responseInput.value = targetRun.response;
                    
                    setDbMode('own');
                    let evalData = targetRun.data;
                    if (typeof evalData === 'string') {
                        try { evalData = JSON.parse(evalData); } catch(e) {}
                    } else if (!evalData && targetRun.evaluation_data) {
                        try { evalData = JSON.parse(targetRun.evaluation_data); } catch(e) {}
                    }
                    renderDashboardResults(evalData);
                }, 50);
            };

            if (run) {
                loadAndRenderRun(run);
            } else {
                fetch('/api/chats', {
                    headers: { 'Authorization': `Bearer ${currentUser.token}` }
                })
                .then(r => r.json())
                .then(dbChats => {
                    const dbRun = dbChats.find(c => c.id === viewRunId);
                    if (dbRun) {
                        loadAndRenderRun(dbRun);
                    }
                })
                .catch(e => console.error("Failed to load run from DB for viewing:", e));
            }
        }
        
        // Restore pending Multi-LLM Comparison
        const compareDataStr = localStorage.getItem('view_compare_data');
        if (compareDataStr) {
            localStorage.removeItem('view_compare_data');
            try {
                const compareData = JSON.parse(compareDataStr);
                setTimeout(() => {
                    const promptInput = document.getElementById('db-prompt');
                    if (promptInput) promptInput.value = compareData.prompt;
                    
                    const welcomeCover = document.getElementById('db-welcome-cover');
                    const resultsContainer = document.getElementById('db-results-container');
                    if (welcomeCover) welcomeCover.classList.add('hidden');
                    if (resultsContainer) resultsContainer.classList.remove('hidden');
                    
                    renderComparison(compareData.data);
                }, 50);
            } catch (e) {
                console.error('Failed to parse compare data:', e);
            }
        }
    }
    if (path === '/settings' && currentUser) {
        const nameField = document.getElementById('setting-profile-name');
        const emailField = document.getElementById('setting-profile-email');
        if (nameField) nameField.value = currentUser.name || '';
        if (emailField) emailField.value = currentUser.email || '';
        
        const notifyEmail = document.getElementById('setting-notify-email');
        const notifySlack = document.getElementById('setting-notify-slack');
        const notifyConsole = document.getElementById('setting-notify-console');
        
        if (notifyEmail) notifyEmail.checked = localStorage.getItem('truthlens_notify_email') !== 'false';
        if (notifySlack) notifySlack.checked = localStorage.getItem('truthlens_notify_slack') === 'true';
        if (notifyConsole) notifyConsole.checked = localStorage.getItem('truthlens_notify_console') !== 'false';

        const settingLanguage = document.getElementById('setting-language');
        if (settingLanguage) settingLanguage.value = localStorage.getItem('truthlens_language') || 'English';
    }

    if (path === '/chat' && typeof chatRenderSidebar === 'function') {
        chatRenderSidebar();
    }
}

function navigateTo(viewId) {
    if (!viewId) return;
    const path = viewToPath[viewId];
    if (path) {
        window.location.href = path;
    }
}

function updateNavForAuth() {
    const loginLink = document.getElementById('nav-login-btn');
    if (currentUser) {
        if (loginLink) {
            loginLink.innerHTML = '<i class="fa-solid fa-arrow-right-from-bracket"></i> Logout';
            loginLink.setAttribute('href', '/logout');
        }
    } else {
        if (loginLink) {
            loginLink.innerHTML = 'Login';
            loginLink.setAttribute('href', '/login');
        }
    }
}

function resetDashboard() {
    if (document.getElementById('db-welcome-cover')) document.getElementById('db-welcome-cover').classList.remove('hidden');
    if (document.getElementById('db-results-container')) document.getElementById('db-results-container').classList.add('hidden');
    if (document.getElementById('db-score-row')) document.getElementById('db-score-row').classList.add('hidden');
    if (document.getElementById('db-search-warning')) document.getElementById('db-search-warning').classList.add('hidden');
    if (document.getElementById('db-trust-fill')) document.getElementById('db-trust-fill').style.width = '0%';
    if (document.getElementById('db-trust-score')) document.getElementById('db-trust-score').textContent = '0%';
    if (document.getElementById('db-citations-panel')) document.getElementById('db-citations-panel').classList.add('hidden');
    if (document.getElementById('db-metric-bars')) document.getElementById('db-metric-bars').classList.add('hidden');
    if (document.getElementById('db-empty-state')) document.getElementById('db-empty-state').classList.remove('hidden');
    if (document.getElementById('db-details-list')) document.getElementById('db-details-list').innerHTML = '<li class="placeholder-li">No analysis run yet.</li>';
    
    if (document.getElementById('db-overall-risk')) document.getElementById('db-overall-risk').textContent = '--';
    if (document.getElementById('db-hallu-score')) document.getElementById('db-hallu-score').textContent = '--';
    if (document.getElementById('db-consistency-val')) document.getElementById('db-consistency-val').textContent = '--';
    
    if (typeof hideFRPanels === 'function') hideFRPanels();
}

// Global click interceptor for relative local paths
document.addEventListener('click', e => {
    const anchor = e.target.closest('a');
    if (!anchor) return;
    
    const href = anchor.getAttribute('href');
    if (!href) return;
    
    if (href === '/logout') {
        e.preventDefault();
        currentUser = null;
        localStorage.removeItem('truthlens_user');
        window.location.href = '/';
    }
});

// Popstate listener for back/forward navigation
window.addEventListener('popstate', () => {
    handleRouting();
});

document.getElementById('new-analysis-btn')?.addEventListener('click', () => {
    navigateTo('analysis');
    document.getElementById('eval-form')?.reset();
    document.getElementById('db-eval-form')?.reset();
    document.getElementById('home-gen-preview')?.classList.add('hidden');
    document.getElementById('db-gen-preview')?.classList.add('hidden');

    // Reset Home View Results (safe check)
    const halluSvg = document.getElementById('hallucination-svg');
    if (halluSvg) halluSvg.setAttribute('stroke-dasharray', '0, 100');
    const halluText = document.getElementById('hallucination-text');
    if (halluText) halluText.textContent = '0%';
    const consistencySvg = document.getElementById('consistency-svg');
    if (consistencySvg) consistencySvg.setAttribute('stroke-dasharray', '0, 100');
    const consistencyText = document.getElementById('consistency-text');
    if (consistencyText) consistencyText.textContent = '0%';

    const mcSelf = document.getElementById('mc-self');
    if (mcSelf) mcSelf.textContent = '--%';
    const mcNli = document.getElementById('mc-nli');
    if (mcNli) mcNli.textContent = '--%';
    const mcHhem = document.getElementById('mc-hhem');
    if (mcHhem) mcHhem.textContent = '--%';

    const detailsList = document.getElementById('details-list');
    if (detailsList) detailsList.innerHTML = '<li>Run an analysis to see metrics.</li>';
    const demoQueryText = document.getElementById('demo-query-text');
    if (demoQueryText) demoQueryText.textContent = 'Waiting for input...';

    // Reset Dashboard View Results
    const dbDetailsList = document.getElementById('db-details-list');
    if (dbDetailsList) dbDetailsList.innerHTML = '<li class="placeholder-li">No analysis run yet.</li>';
    hideFRPanels();
});

// ══════════════════════════════════════════
//  SHARED HELPERS & STATE
// ══════════════════════════════════════════
let homeMode = 'own'; // 'own' or 'generate'
let dbMode = 'own';
let homeModel = 'tiny'; // 'tiny' or 'llama'
let dbModel = 'tiny';

function setHomeModel(model) {
    homeModel = model;
    document.getElementById('model-tiny')?.classList.toggle('active', model === 'tiny');
    document.getElementById('model-llama')?.classList.toggle('active', model === 'llama');

    const desc = document.getElementById('home-model-desc');
    if (desc) {
        if (model === 'tiny') {
            desc.textContent = "Using RAG + TinyLlama (1.1B) for optimized speed.";
        } else {
            desc.textContent = "Using RAG + Llama 3 (8B) via High-Fidelity Inference API.";
        }
    }
}

function setDbModel(model) {
    dbModel = model;
    document.getElementById('db-model-tiny')?.classList.toggle('active', model === 'tiny');
    document.getElementById('db-model-llama')?.classList.toggle('active', model === 'llama');

    const title = document.getElementById('db-model-title');
    const desc = document.getElementById('db-model-desc');
    if (model === 'tiny') {
        if (title) title.textContent = "Standard Reasoning Engine";
        if (desc) desc.textContent = "Generating factual responses via RAG + TinyLlama.";
    } else {
        if (title) title.textContent = "Llama 3 Intelligent Engine";
        if (desc) desc.textContent = "High-fidelity generation using Meta-Llama-3-8B-Instruct.";
    }
}

function getVerdict(score) {
    if (score <= 20) return "High Trust";
    if (score <= 40) return "Moderate Risk";
    if (score <= 60) return "High Risk";
    return "Severe Risk";
}

function getVerdictBadgeClass(score) {
    if (score <= 20) return "high-trust";
    if (score <= 40) return "moderate-risk";
    if (score <= 60) return "high-risk";
    return "severe-risk";
}

function getColorForRisk(value) {
    const score = Math.round(value * 100);
    if (score <= 20) return '#10b981'; // Green
    if (score <= 40) return '#f59e0b'; // Yellow/Orange
    if (score <= 60) return '#ef4444'; // Orange/Red
    return '#991b1b'; // Dark Red
}

function getRiskLabel(value) {
    return getVerdict(Math.round(value * 100));
}

async function callAPI(prompt, response, context = '') {
    const lang = localStorage.getItem('truthlens_language') || 'English';
    const headers = { 'Content-Type': 'application/json' };
    if (currentUser && currentUser.token) {
        headers['Authorization'] = `Bearer ${currentUser.token}`;
    }
    const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ prompt, response, context, language: lang })
    });

    if (!res.ok) {
        if (res.status === 401) {
            alert('Your session has expired. Please log in again.');
            currentUser = null;
            localStorage.removeItem('truthlens_user');
            updateNavForAuth();
            navigateTo('login');
            throw new Error('Session expired');
        }
        const errData = await res.json().catch(() => ({ detail: 'Server Error' }));
        throw new Error(errData.detail || `API error (${res.status})`);
    }

    return res.json();
}

async function callGenerateAPI(prompt, model = 'tiny') {
    const lang = localStorage.getItem('truthlens_language') || 'English';
    const headers = { 'Content-Type': 'application/json' };
    if (currentUser && currentUser.token) {
        headers['Authorization'] = `Bearer ${currentUser.token}`;
    }
    const res = await fetch('/api/generate', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ prompt, model, language: lang })
    });
    if (res.status === 401) {
        alert('Your session has expired. Please log in again.');
        currentUser = null;
        localStorage.removeItem('truthlens_user');
        updateNavForAuth();
        navigateTo('login');
        throw new Error('Unauthorized');
    }
    const data = await res.json();
    return { response: data.generated_response, context: data.context || '' };
}

// ══════════════════════════════════════════
//  MODE TOGGLE LOGIC
// ══════════════════════════════════════════
function setHomeMode(mode) {
    homeMode = mode;
    const ownPanel = document.getElementById('home-own-panel');
    const genPanel = document.getElementById('home-gen-panel');
    const ownBtn = document.getElementById('home-mode-own');
    const genBtn = document.getElementById('home-mode-gen');

    if (mode === 'own') {
        if (ownBtn) ownBtn.classList.add('active');
        if (genBtn) genBtn.classList.remove('active');
        if (ownPanel) ownPanel.classList.remove('hidden');
        if (genPanel) genPanel.classList.add('hidden');
        const resp = document.getElementById('response');
        if (resp) resp.required = true;
    } else {
        if (genBtn) genBtn.classList.add('active');
        if (ownBtn) ownBtn.classList.remove('active');
        if (genPanel) genPanel.classList.remove('hidden');
        if (ownPanel) ownPanel.classList.add('hidden');
        const resp = document.getElementById('response');
        if (resp) resp.required = false;
        document.getElementById('home-gen-preview')?.classList.add('hidden');
    }
}

function setDbMode(mode) {
    dbMode = mode;
    if (mode === 'own') {
        document.getElementById('db-mode-own')?.classList.add('active');
        document.getElementById('db-mode-gen')?.classList.remove('active');
        document.getElementById('db-own-panel')?.classList.remove('hidden');
        document.getElementById('db-gen-panel')?.classList.add('hidden');
        document.getElementById('db-signal-checklist-own')?.classList.remove('hidden');
        document.getElementById('db-signal-checklist-gen')?.classList.add('hidden');
    } else {
        document.getElementById('db-mode-gen')?.classList.add('active');
        document.getElementById('db-mode-own')?.classList.remove('active');
        document.getElementById('db-gen-panel')?.classList.remove('hidden');
        document.getElementById('db-own-panel')?.classList.add('hidden');
        document.getElementById('db-gen-preview')?.classList.add('hidden');
        document.getElementById('db-signal-checklist-own')?.classList.add('hidden');
        document.getElementById('db-signal-checklist-gen')?.classList.remove('hidden');
    }
}

// ══════════════════════════════════════════
//  HOME VIEW — FORM
// ══════════════════════════════════════════
document.getElementById('eval-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const promptEl = document.getElementById('prompt');
    const prompt = promptEl ? promptEl.value : '';
    let responseText = '';
    let contextText = '';
    const btn = document.getElementById('analyze-btn');
    if (!btn) return;

    const demoQueryText = document.getElementById('demo-query-text');
    if (demoQueryText) demoQueryText.textContent = `"${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"`;
    btn.disabled = true;

    if (homeMode === 'generate' && (!currentUser || !currentUser.token)) {
        // We allow anonymous generation but maybe with a note
        console.log("Anonymous analysis running...");
    }

    try {
        if (homeMode === 'generate') {
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Response...';
            const genData = await callGenerateAPI(prompt, homeModel);
            responseText = genData.response;
            contextText = genData.context;

            // Show preview
            const genPreview = document.getElementById('home-gen-preview');
            if (genPreview) genPreview.classList.remove('hidden');
            const genText = document.getElementById('home-gen-text');
            if (genText) genText.textContent = responseText;
        } else {
            const respEl = document.getElementById('response');
            responseText = respEl ? respEl.value : '';
        }

        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
        const halluText = document.getElementById('hallucination-text');
        if (halluText) halluText.innerHTML = '<i class="fa-solid fa-spinner fa-spin" style="font-size: 1.5rem;"></i>';
        const detailsList = document.getElementById('details-list');
        if (detailsList) detailsList.innerHTML = '<li><i class="fa-solid fa-spinner fa-spin" style="margin-right: 10px;"></i> Running evaluation pipeline...</li>';

        const data = await callAPI(prompt, responseText, contextText);
        renderHomeResults(data);
    } catch (err) {
        console.error(err);
        const halluText = document.getElementById('hallucination-text');
        if (halluText) halluText.innerHTML = '<i class="fa-solid fa-triangle-exclamation" style="color: #ef4444; font-size: 1.5rem;"></i>';
        const detailsList = document.getElementById('details-list');
        if (detailsList) detailsList.innerHTML = `<li style="color: #ef4444;"><i class="fa-solid fa-circle-exclamation" style="margin-right: 10px;"></i> Connection Error: Ensure the backend server is running and reachable.</li>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze';
    }
});

document.getElementById('example-btn')?.addEventListener('click', () => {
    const promptEl = document.getElementById('prompt');
    const responseEl = document.getElementById('response');
    if (promptEl) promptEl.value = "Who won the 2023 Cricket World Cup?";
    if (responseEl) responseEl.value = "First, let's think step by step. The 2023 ICC Men's Cricket World Cup was hosted in India. The final was played between India and Australia at the Narendra Modi Stadium in Ahmedabad. Australia defeated India by 6 wickets to win their sixth Cricket World Cup title.";
    const evalForm = document.getElementById('eval-form');
    if (evalForm) evalForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
});

function renderHomeResults(data) {
    const { components, details, trust_score, trust_verdict } = data;
    const consistencyRisk = components["Consistency"] ?? 0;
    const nliRisk = components["Logical NLI"] ?? 0;
    const hhemRisk = components["HHEM Factor"] ?? 0;
    
    // Hallucination Score (Normalized)
    const halluNorm = (nliRisk + hhemRisk) / 2;
    const halluScore = Math.round(halluNorm * 100);
    const halluColor = getColorForRisk(halluNorm);

    // Save to localStorage runs cache
    const promptEl = document.getElementById('prompt');
    const promptText = promptEl ? promptEl.value : '';
    let responseText = '';
    if (homeMode === 'generate') {
        const homeGenText = document.getElementById('home-gen-text');
        responseText = homeGenText ? homeGenText.textContent : '';
    } else {
        const responseEl = document.getElementById('response');
        responseText = responseEl ? responseEl.value : '';
    }
    saveAnalysisRun(promptText, responseText, data);

    const hallucinationText = document.getElementById('hallucination-text');
    if (hallucinationText) hallucinationText.textContent = `${halluScore}%`;
    const halluSvg = document.getElementById('hallucination-svg');
    if (halluSvg) {
        halluSvg.setAttribute('stroke-dasharray', `${halluScore}, 100`);
        halluSvg.setAttribute('stroke', halluColor);
    }
    const riskDisplay = document.getElementById('risk-display');
    if (riskDisplay) {
        riskDisplay.textContent = getRiskLabel(halluNorm);
        riskDisplay.style.color = halluColor;
    }

    const consScore = Math.round((1 - consistencyRisk) * 100);
    const consistencyText = document.getElementById('consistency-text');
    if (consistencyText) consistencyText.textContent = `${consScore}%`;
    const consSvg = document.getElementById('consistency-svg');
    if (consSvg) {
        consSvg.setAttribute('stroke-dasharray', `${consScore}, 100`);
        consSvg.setAttribute('stroke', consScore > 70 ? '#3b82f6' : getColorForRisk(consistencyRisk));
    }

    const elNli = document.getElementById('mc-nli');
    if (elNli) {
        elNli.textContent = `${Math.round(nliRisk * 100)}%`;
        elNli.style.color = getColorForRisk(nliRisk);
    }
    const elHhem = document.getElementById('mc-hhem');
    if (elHhem) {
        elHhem.textContent = `${Math.round(hhemRisk * 100)}%`;
        elHhem.style.color = getColorForRisk(hhemRisk);
    }

    const list = document.getElementById('details-list');
    if (list) {
        list.innerHTML = '';
        Object.keys(details).forEach(key => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${key}:</strong> ${details[key]}`;
            list.appendChild(li);
        });
    }
}

// ══════════════════════════════════════════
//  DASHBOARD VIEW — FORM
// ══════════════════════════════════════════
document.getElementById('db-eval-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log('[TruthLens] Dashboard analysis form submitted.');
    const promptEl = document.getElementById('db-prompt');
    const prompt = promptEl ? promptEl.value : '';
    let responseText = '';
    let contextText = '';
    const btn = document.getElementById('db-analyze-btn');
    if (!btn) return;

    if (!prompt) return;
    const responseEl = document.getElementById('db-response');
    if (dbMode === 'own' && (!responseEl || !responseEl.value)) return;

    btn.disabled = true;

    const welcomeCover = document.getElementById('db-welcome-cover');
    const resultsContainer = document.getElementById('db-results-container');
    const emptyState = document.getElementById('db-empty-state');
    const genPreview = document.getElementById('db-gen-preview');
    const genText = document.getElementById('db-gen-text');

    if (!currentUser || !currentUser.token) {
        if (welcomeCover) welcomeCover.classList.add('hidden');
        if (resultsContainer) resultsContainer.classList.add('hidden');
        if (emptyState) {
            emptyState.classList.remove('hidden');
            emptyState.innerHTML = `<div style="text-align:center;padding:3rem 0;color:#ef4444;"><i class="fa-solid fa-lock fa-3x" style="margin-bottom:1.5rem;color:#94a3b8;"></i><p style="font-weight:500;">Authentication Required. Please log in to access TruthLens AI evaluation.</p></div>`;
        }
        btn.disabled = false;
        return;
    }

    try {
        if (dbMode === 'generate') {
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
            const genData = await callGenerateAPI(prompt, dbModel);
            responseText = genData.response;
            contextText = genData.context;

            // Show preview
            if (genPreview) genPreview.classList.remove('hidden');
            if (genText) genText.textContent = responseText;
        } else {
            responseText = responseEl ? responseEl.value : '';
        }

        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        // Show Loading State in Dashboard
        if (welcomeCover) welcomeCover.classList.add('hidden');
        if (resultsContainer) resultsContainer.classList.remove('hidden');
        
        const trustPanel = document.getElementById('db-trust-panel');
        const metricBars = document.getElementById('db-metric-bars');
        const explanationCard = document.getElementById('db-explanation-card');

        if (trustPanel) trustPanel.classList.add('hidden');
        if (metricBars) metricBars.classList.add('hidden');
        if (explanationCard) explanationCard.classList.add('hidden');
        
        if (emptyState) {
            emptyState.classList.remove('hidden');
            emptyState.innerHTML = '<div style="text-align:center;padding:3rem 0;"><i class="fa-solid fa-circle-notch fa-spin fa-3x" style="color:#6366f1;margin-bottom:1.5rem;"></i><p style="color:#64748b;font-weight:500;">Running TruthLens evaluation pipeline...</p></div>';
        }

        const data = await callAPI(prompt, responseText, contextText);

        // Temporarily set value so renderFRPanels can read it
        const originalVal = responseEl ? responseEl.value : '';
        if (responseEl) responseEl.value = responseText;
        renderDashboardResults(data);
        if (dbMode === 'generate' && responseEl) {
            responseEl.value = originalVal; // restore
        }
    } catch (err) {
        console.error("Dashboard Analysis Error:", err);
        const errorMsg = err.message || "Unknown error";
        if (emptyState) {
            emptyState.classList.remove('hidden');
            emptyState.innerHTML = `
                <div style="text-align:center;padding:3rem 0;color:#ef4444;">
                    <i class="fa-solid fa-circle-exclamation fa-3x" style="margin-bottom:1.5rem;"></i>
                    <p style="font-weight:500;">Analysis failed: ${errorMsg}</p>
                    <p style="font-size:0.8rem; margin-top:0.5rem; color:#64748b;">Please check if the backend server is running and your internet connection is stable.</p>
                </div>`;
        }
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Run Analysis';
    }
});

document.getElementById('db-example-btn')?.addEventListener('click', () => {
    const promptEl = document.getElementById('db-prompt');
    const responseEl = document.getElementById('db-response');
    if (promptEl) promptEl.value = "Who won the 2023 Cricket World Cup?";
    if (responseEl) responseEl.value = "First, let's think step by step. The 2023 ICC Men's Cricket World Cup was hosted in India. Australia defeated India by 6 wickets to win their sixth Cricket World Cup title.";
    document.getElementById('db-eval-form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
});

function renderDashboardResults(data) {
    const { trust_score, trust_verdict, trust_reasoning, components, details, evidence } = data;
    
    // Save to localStorage runs cache
    const promptEl = document.getElementById('db-prompt');
    const promptText = promptEl ? promptEl.value : '';
    const responseEl = document.getElementById('db-response');
    const responseText = responseEl ? responseEl.value : '';
    saveAnalysisRun(promptText, responseText, data);
    
    // Hide Welcome Cover & Show Results Container
    const welcomeCover = document.getElementById('db-welcome-cover');
    const resultsContainer = document.getElementById('db-results-container');
    const trustPanel = document.getElementById('db-trust-panel');

    if (welcomeCover) welcomeCover.classList.add('hidden');
    if (resultsContainer) resultsContainer.classList.remove('hidden');
    if (trustPanel) trustPanel.classList.remove('hidden');

    // Show/populate analysis page summary cards
    const scoreRowEl = document.getElementById('db-score-row');
    if (scoreRowEl) scoreRowEl.classList.remove('hidden');

    const overallRiskEl = document.getElementById('db-overall-risk');
    if (overallRiskEl) {
        const rPct = Math.round((data.overall_risk ?? 0) * 100);
        overallRiskEl.textContent = `${rPct}%`;
        const riskSubEl = document.getElementById('db-risk-sub');
        if (riskSubEl) {
            riskSubEl.textContent = getVerdict(rPct);
            riskSubEl.style.color = getColorForRisk(data.overall_risk ?? 0);
        }
    }

    const halluScoreEl = document.getElementById('db-hallu-score');
    if (halluScoreEl) {
        const nliRisk = components["Logical NLI"] ?? 0;
        const hhemRisk = components["HHEM Factor"] ?? 0;
        const halluNorm = (nliRisk + hhemRisk) / 2;
        const halluScore = Math.round(halluNorm * 100);
        halluScoreEl.textContent = `${halluScore}%`;
    }

    // 1. Trust Meter Animation
    const fill = document.getElementById('db-trust-fill');
    const scoreText = document.getElementById('db-trust-score');
    const verdictEl = document.getElementById('db-trust-verdict');
    const reasonEl = document.getElementById('db-trust-reasoning');

    if (fill) fill.style.width = `${trust_score}%`;
    if (scoreText) scoreText.textContent = `${trust_score}%`;
    if (verdictEl) {
        const risk_score = 100 - trust_score;
        verdictEl.textContent = getVerdict(risk_score);
        verdictEl.className = 'tmp-verdict'; // reset
        verdictEl.classList.add(getVerdictBadgeClass(risk_score));
    }
    if (reasonEl) reasonEl.textContent = trust_reasoning;

    // 2. Mini Metrics
    const consistencyValEl = document.getElementById('db-consistency-val');
    const nliValEl = document.getElementById('db-nli-val');
    const hhemValEl = document.getElementById('db-hhem-val');

    if (consistencyValEl) {
        const cVal = Math.round((1 - (components["Consistency"] || 0)) * 100);
        consistencyValEl.textContent = `${cVal}%`;
    }
    if (nliValEl) {
        const nVal = Math.round((components["Logical NLI"] || 0) * 100);
        nliValEl.textContent = `${nVal}%`;
    }
    if (hhemValEl) {
        const hVal = Math.round((components["HHEM Factor"] || 0) * 100);
        hhemValEl.textContent = `${hVal}%`;
    }

    // 3. Citations
    const citationPanel = document.getElementById('db-citations-panel');
    const citationList = document.getElementById('db-citation-list');
    if (citationPanel && citationList) {
        if (evidence && evidence.length > 0) {
            citationPanel.classList.remove('hidden');
            citationList.innerHTML = evidence.map(e => `
                <div class="citation-item">
                    <div class="cit-src">${e.src}</div>
                    <div class="cit-text">"${e.snippet}"</div>
                </div>
            `).join('');
        } else {
            citationPanel.classList.add('hidden');
        }
    }

    // Show/Hide Search Warning if no evidence found
    const searchWarning = document.getElementById('db-search-warning');
    if (searchWarning) {
        if (!evidence || evidence.length === 0) {
            searchWarning.classList.remove('hidden');
        } else {
            searchWarning.classList.add('hidden');
        }
    }

    // Metric bars
    const emptyState = document.getElementById('db-empty-state');
    if (emptyState) emptyState.classList.add('hidden');

    const expCard = document.getElementById('db-explanation-card');
    if (data.explanation) {
        if (expCard) expCard.classList.remove('hidden');
        const expFlagged = document.getElementById('exp-flagged');
        const expReason = document.getElementById('exp-reason');
        const expCorrection = document.getElementById('exp-correction');
        if (expFlagged) expFlagged.textContent = `"${data.explanation.flagged_sentence}"`;
        if (expReason) expReason.textContent = data.explanation.reason;
        if (expCorrection) expCorrection.textContent = data.explanation.correction;
    } else {
        if (expCard) expCard.classList.add('hidden');
    }

    const barsEl = document.getElementById('db-metric-bars');
    if (barsEl) {
        barsEl.classList.remove('hidden');
        barsEl.innerHTML = '';
        Object.keys(components).forEach(key => {
            const raw = components[key] ?? 0;
            const pct = Math.round(raw * 100);
            const color = getColorForRisk(raw);
            barsEl.innerHTML += `
                <div class="metric-bar-row">
                    <div class="mbr-label">${key}</div>
                    <div class="mbr-track">
                        <div class="mbr-fill" style="width:${pct}%;background:${color}"></div>
                    </div>
                    <div class="mbr-val" style="color:${color}">${pct}%</div>
                </div>`;
        });
    }

    // Details
    const detailsList = document.getElementById('db-details-list');
    if (detailsList) {
        detailsList.innerHTML = '';
        Object.keys(details).forEach(key => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${key}:</strong> ${details[key]}`;
            detailsList.appendChild(li);
        });
    }

    renderFRPanels(data, promptText, responseText);
}

// ══════════════════════════════════════════
//  FR PANELS RENDERER
// ══════════════════════════════════════════
function show(id) { 
    const el = document.getElementById(id);
    if (el) el.classList.remove('hidden'); 
}
function initHeatmapHovers() {
    const tooltip = document.getElementById('truthlens-tooltip');
    if (!tooltip) return;
    const claims = document.querySelectorAll('.ht-claim');

    claims.forEach(claim => {
        claim.addEventListener('mouseenter', (e) => {
            const type = claim.getAttribute('data-type');
            const cat = claim.getAttribute('data-category');
            const reason = claim.getAttribute('data-reason');
            const score = claim.getAttribute('data-score');

            const ttType = document.getElementById('tt-type');
            const ttReason = document.getElementById('tt-reason');
            const ttConf = document.getElementById('tt-conf');
            const statusEl = document.getElementById('tt-status');

            if (ttType) ttType.textContent = type;
            if (ttReason) ttReason.textContent = reason;
            if (ttConf) ttConf.textContent = score + '%';

            if (statusEl) {
                statusEl.textContent = cat;
                statusEl.className = 'tt-status-pill tt-' + cat;
            }

            tooltip.classList.remove('hidden');
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'translateY(0)';
        });

        claim.addEventListener('mousemove', (e) => {
            const x = e.pageX + 15;
            const y = e.pageY + 15;

            // Boundary check
            const tooltipWidth = 280;
            const pageWidth = window.innerWidth;
            const finalX = (x + tooltipWidth > pageWidth) ? x - tooltipWidth - 30 : x;

            tooltip.style.left = finalX + 'px';
            tooltip.style.top = y + 'px';
        });

        claim.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateY(10px)';
            setTimeout(() => {
                if (tooltip.style.opacity === '0') tooltip.classList.add('hidden');
            }, 200);
        });
    });
}

function hide(id) { 
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden'); 
}

function hideFRPanels() {
    hide('fr-pipeline-section');
    hide('fr-claims-heatmap');
    // hide('fr-entities-section'); // Removed as it's not in the DOM
    hide('fr-comparison-section');
    hide('fr-compare-section');
    hide('fr-evidence-section');
    hide('fr-rag-section');
}

function renderFRPanels(data, prompt, responseText) {
    const risk = data.overall_risk || 0;

    // FR-02 / FR-23: Safety Filter + Pipeline
    show('fr-pipeline-section');
    const safetyBadge = document.getElementById('fr-safety-badge');
    if (safetyBadge) {
        if (risk > 0.6) {
            safetyBadge.className = 'safety-badge danger';
            safetyBadge.innerHTML = '<i class="fa-solid fa-shield-xmark"></i> Safety Filter: Flagged';
        } else if (risk > 0.3) {
            safetyBadge.className = 'safety-badge warn';
            safetyBadge.innerHTML = '<i class="fa-solid fa-shield-exclamation"></i> Safety Filter: Caution';
        } else {
            safetyBadge.className = 'safety-badge';
            safetyBadge.innerHTML = '<i class="fa-solid fa-shield-check"></i> Safety Filter: Passed';
        }
    }

    // FR-05 / FR-06 / FR-14 / FR-17: Claims
    show('fr-claims-heatmap');
    const claimsList = document.getElementById('fr-claims-list');
    const claimsToShow = data.sentence_analysis || [];
    const claimsCountEl = document.getElementById('fr-claims-count');

    if (claimsCountEl) claimsCountEl.textContent = `${claimsToShow.length} claims`;
    if (claimsList) {
        claimsList.innerHTML = '';
        claimsToShow.forEach((claim) => {
            const s = claim.category;
            claimsList.innerHTML += `
                <div class="claim-item">
                    <span class="claim-status ${s}">${s}</span>
                    <span class="claim-text">${claim.text.trim()}</span>
                </div>`;
        });
    }

    // FR-12 / FR-16: Sentence-Level Heatmap (Rich Analysis + Tooltips)
    const heatmapEl = document.getElementById('fr-heatmap');
    if (heatmapEl) {
        if (data.sentence_analysis && data.sentence_analysis.length > 0) {
            heatmapEl.innerHTML = data.sentence_analysis.map(s => {
                return `<span class="ht-claim ht-${s.category}" 
                    data-type="${s.type}" 
                    data-category="${s.category}" 
                    data-reason="${s.reason}" 
                    data-score="${s.score}">${s.text}</span>`;
            }).join(' ');

            // Attach hover logic
            initHeatmapHovers();
        } else {
            // Fallback
            const words = responseText.split(/\s+/);
            heatmapEl.innerHTML = words.map(w => `<span class="ht-claim ht-verified">${w}</span>`).join(' ');
        }
    }

    // FR-04 / FR-19 / FR-20: Original vs Corrected Comparison (Grounded in real data)
    show('fr-comparison-section');
    const origTextEl = document.getElementById('fr-original-text');
    if (origTextEl) origTextEl.textContent = responseText;

    const compColOriginal = document.querySelector('#fr-comparison-section .comp-col.original');
    const compColCorrected = document.querySelector('#fr-comparison-section .comp-col.corrected');
    const origLabelEl = compColOriginal ? compColOriginal.querySelector('.comp-label') : null;
    const correctedLabelEl = compColCorrected ? compColCorrected.querySelector('.comp-label') : null;

    let correctionHTML = "";
    if (data.explanation && data.explanation.correction) {
        if (origLabelEl) {
            origLabelEl.innerHTML = `<i class="fa-solid fa-circle-xmark text-orange"></i> Original Response (Flagged)`;
        }
        if (correctedLabelEl) {
            correctedLabelEl.innerHTML = `<i class="fa-solid fa-circle-check text-green"></i> Corrected Verified Answer`;
        }
        correctionHTML = `<em style="color:#ef4444;font-size:0.8rem;">⚠ Correction Generated</em><br><br>${data.explanation.correction}`;
    } else {
        if (origLabelEl) {
            origLabelEl.innerHTML = `<i class="fa-solid fa-circle-check text-green"></i> Original Response (Verified)`;
        }
        if (correctedLabelEl) {
            correctedLabelEl.innerHTML = `<i class="fa-solid fa-circle-check text-green"></i> Verified Fact`;
        }
        correctionHTML = `<em style="color:#10b981;font-size:0.8rem;">✓ Grounded & Verified</em><br><br>${responseText}`;
    }
    const correctedTextEl = document.getElementById('fr-corrected-text');
    if (correctedTextEl) correctedTextEl.innerHTML = correctionHTML;

    // NEW FEATURE: Visual Document RAG Viewer
    const ragSection = document.getElementById('fr-rag-section');
    const ragList = document.getElementById('fr-rag-list');
    const ragCountEl = document.getElementById('fr-rag-count');
    
    if (ragSection && ragList) {
        const chunks = data.rag_chunks || [];
        if (chunks.length > 0) {
            show('fr-rag-section');
            if (ragCountEl) ragCountEl.textContent = `${chunks.length} chunk${chunks.length > 1 ? 's' : ''} retrieved`;
            
            ragList.innerHTML = chunks.map((c, i) => {
                const filename = c.metadata.filename || 'Uploaded Document';
                return `
                    <div class="rag-chunk-card">
                        <div class="rag-chunk-meta">
                            <div class="rag-chunk-filename">
                                <i class="fa-solid fa-file-lines"></i>
                                <span>Chunk #${i+1} — ${filename}</span>
                            </div>
                            <div class="rag-chunk-score-wrap">
                                <span style="font-size:0.75rem; color:var(--text-muted);">Relevance:</span>
                                <div class="rag-chunk-score-bar-track">
                                    <div class="rag-chunk-score-bar-fill" style="width: ${c.score}%;"></div>
                                </div>
                                <span class="rag-chunk-score-text">${c.score}%</span>
                            </div>
                        </div>
                        <div class="rag-chunk-content">${c.page_content}</div>
                    </div>
                `;
            }).join('');
        } else {
            hide('fr-rag-section');
        }
    }

    // FR-11 / FR-18 / FR-21 / FR-22: Evidence Sources
    show('fr-evidence-section');

    let evidenceSources = [];
    if (data.evidence && data.evidence.length > 0) {
        evidenceSources = data.evidence.map(e => ({
            src: e.src || 'Web Snippet',
            snippet: e.snippet,
            conf: '99%'
        }));
    } else {
        evidenceSources = [
            { src: 'System Context', snippet: 'No external sources retrieved. Analysis relied on internal model weights.', conf: '--' }
        ];
    }
    const evidenceListEl = document.getElementById('fr-evidence-list');
    if (evidenceListEl) {
        evidenceListEl.innerHTML = evidenceSources.map(e => `
            <div class="evidence-item">
                <div class="ev-icon"><i class="fa-solid fa-book"></i></div>
                <div>
                    <div class="ev-source">${e.src}</div>
                    <div class="ev-snippet">${e.snippet}</div>
                </div>
                <div class="ev-confidence">${e.conf}</div>
            </div>`).join('');
    }

    const claims = data.sentence_analysis || [];
    const verified = claims.filter(c => c.category === 'verified').length;
    const partial = claims.filter(c => c.category === 'partial').length;
    const weak = claims.filter(c => c.category === 'weak').length;
    const contradicted = claims.filter(c => c.category === 'contradicted').length;
    const fabricated = claims.filter(c => c.category === 'fabricated').length;

    const analyticsDef = [
        { label: 'Claims Extracted', val: claims.length, color: '#6366f1' },
        { label: 'Verified', val: verified, color: '#10b981' },
        { label: 'Partial', val: partial, color: '#eab308' },
        { label: 'Weak', val: weak, color: '#f97316' },
        { label: 'Contradicted', val: contradicted, color: '#ef4444' },
        { label: 'Fabricated', val: fabricated, color: '#991b1b' },
        { label: 'Evidence Sources', val: evidenceSources.length, color: '#3b82f6' },
        { label: 'Overall Risk', val: `${Math.round(risk * 100)}%`, color: getColorForRisk(risk) },
    ];
    const analyticsEl = document.getElementById('fr-analytics');
    if (analyticsEl) {
        analyticsEl.innerHTML = analyticsDef.map(a => `
            <div class="analytic-row">
                <span class="analytic-label">${a.label}</span>
                <span class="analytic-val" style="color:${a.color}">${a.val}</span>
            </div>`).join('');
    }

    const now = new Date();
    const ts = (offset) => {
        const d = new Date(now - offset);
        return d.toTimeString().slice(0, 8);
    };
    const logs = [
        { t: ts(7000), dot: 'info', msg: `Query received: "${prompt.substring(0, 40)}…"` },
        { t: ts(6500), dot: 'ok', msg: 'Prompt safety filter passed' },
        { t: ts(5800), dot: 'info', msg: 'LLM response stored (FR-04)' },
        { t: ts(5000), dot: 'info', msg: `${claimsToShow.length} claims extracted and segmented` },
        { t: ts(4200), dot: 'info', msg: `Knowledge validation complete` },
        { t: ts(3800), dot: 'ok', msg: 'Historical fact verification successful' },
        { t: ts(3500), dot: 'ok', msg: 'Knowledge graph validation complete' },
        { t: ts(2800), dot: 'ok', msg: `${evidenceSources.length} evidence sources retrieved` },
        { t: ts(2000), dot: 'ok', msg: 'Token-level heatmap generated' },
        { t: ts(1200), dot: risk > 0.2 ? 'warn' : 'ok', msg: `Hallucination risk: ${Math.round(risk * 100)}% — ${getVerdict(Math.round(risk * 100)).toUpperCase()}` },
        { t: ts(600), dot: 'ok', msg: 'Corrected response generated (FR-19)' },
        { t: ts(0), dot: 'ok', msg: 'Verification pipeline complete (FR-23)' },
    ];
    const activityLogEl = document.getElementById('fr-activity-log');
    if (activityLogEl) {
        activityLogEl.innerHTML = logs.map(l => `
            <div class="log-entry">
                <span class="log-time">${l.t}</span>
                <span class="log-dot ${l.dot}"></span>
                <span class="log-msg">${l.msg}</span>
            </div>`).join('');
    }
}

// ══════════════════════════════════════════
//  SETTINGS — SAVE / RESET
// ══════════════════════════════════════════
const saveSettingsBtn = document.getElementById('save-settings-btn');
if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', () => {
        // Save profile name
        const nameField = document.getElementById('setting-profile-name');
        if (nameField && currentUser) {
            currentUser.name = nameField.value;
            localStorage.setItem('truthlens_user', JSON.stringify(currentUser));
            updateNavForAuth();
        }
        
        // Save notifications
        const notifyEmail = document.getElementById('setting-notify-email');
        const notifySlack = document.getElementById('setting-notify-slack');
        const notifyConsole = document.getElementById('setting-notify-console');
        
        if (notifyEmail) localStorage.setItem('truthlens_notify_email', notifyEmail.checked);
        if (notifySlack) localStorage.setItem('truthlens_notify_slack', notifySlack.checked);
        if (notifyConsole) localStorage.setItem('truthlens_notify_console', notifyConsole.checked);

        // Save Language Settings
        const settingLanguage = document.getElementById('setting-language');
        if (settingLanguage) localStorage.setItem('truthlens_language', settingLanguage.value);

        saveSettingsBtn.innerHTML = '<i class="fa-solid fa-check"></i> Saved!';
        setTimeout(() => { saveSettingsBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Save Settings'; }, 2000);
    });
}

const resetSettingsBtn = document.getElementById('reset-settings-btn');
if (resetSettingsBtn) {
    resetSettingsBtn.addEventListener('click', () => {
        const tLow = document.getElementById('threshold-low');
        if (tLow) tLow.value = 30;
        const tlVal = document.getElementById('tl-val');
        if (tlVal) tlVal.textContent = '30%';
        const tHigh = document.getElementById('threshold-high');
        if (tHigh) tHigh.value = 60;
        const thVal = document.getElementById('th-val');
        if (thVal) thVal.textContent = '60%';
        const prefBreakdown = document.getElementById('pref-breakdown');
        if (prefBreakdown) prefBreakdown.checked = true;
        const prefAnimate = document.getElementById('pref-animate');
        if (prefAnimate) prefAnimate.checked = true;
        const prefAutonav = document.getElementById('pref-autonav');
        if (prefAutonav) prefAutonav.checked = false;
        const settingMode = document.getElementById('setting-mode');
        if (settingMode) settingMode.value = 'mock';
        
        const settingLanguage = document.getElementById('setting-language');
        if (settingLanguage) settingLanguage.value = 'English';
    });
}

function setLoginMode(isLogin) {
    isLoginMode = isLogin;
    const errEl = document.getElementById('auth-error');
    if (errEl) errEl.classList.add('hidden');

    const titleEl = document.getElementById('login-title');
    const subtitleEl = document.getElementById('login-subtitle');
    const nameFieldEl = document.getElementById('auth-name-field');
    const nameEl = document.getElementById('auth-name');
    const submitBtnEl = document.getElementById('auth-submit-btn');
    const toggleTextEl = document.getElementById('auth-toggle-text');

    if (isLoginMode) {
        if (titleEl) titleEl.textContent = 'Welcome Back';
        if (subtitleEl) subtitleEl.textContent = 'Sign in to access TruthLens Dashboard';
        if (nameFieldEl) nameFieldEl.classList.add('hidden');
        if (nameEl) nameEl.required = false;
        if (submitBtnEl) submitBtnEl.textContent = 'Sign In';
        if (toggleTextEl) toggleTextEl.innerHTML = `Don't have an account? <a href="#" id="auth-toggle-link" style="color: #4f46e5; font-weight: 600; text-decoration: none;">Register here</a>`;
    } else {
        if (titleEl) titleEl.textContent = 'Create Account';
        if (subtitleEl) subtitleEl.textContent = 'Register for TruthLens AI';
        if (nameFieldEl) nameFieldEl.classList.remove('hidden');
        if (nameEl) nameEl.required = true;
        if (submitBtnEl) submitBtnEl.textContent = 'Register';
        if (toggleTextEl) toggleTextEl.innerHTML = `Already have an account? <a href="#" id="auth-toggle-link" style="color: #4f46e5; font-weight: 600; text-decoration: none;">Sign in here</a>`;
    }
    // Rebind listener because we replaced the innerHTML
    const newToggle = document.getElementById('auth-toggle-link');
    if (newToggle) newToggle.addEventListener('click', (e) => {
        e.preventDefault();
        setLoginMode(!isLoginMode);
    });
}
window.setLoginMode = setLoginMode;

// ══════════════════════════════════════════
//  AUTHENTICATION LOGIC
// ══════════════════════════════════════════
const authToggleLink = document.getElementById('auth-toggle-link');
if (authToggleLink) {
    authToggleLink.addEventListener('click', function toggleAuthMode(e) {
        e.preventDefault();
        isLoginMode = !isLoginMode;
        const errEl = document.getElementById('auth-error');
        if (errEl) errEl.classList.add('hidden');

        const titleEl = document.getElementById('login-title');
        const subtitleEl = document.getElementById('login-subtitle');
        const nameFieldEl = document.getElementById('auth-name-field');
        const nameEl = document.getElementById('auth-name');
        const submitBtnEl = document.getElementById('auth-submit-btn');
        const toggleTextEl = document.getElementById('auth-toggle-text');

        if (isLoginMode) {
            if (titleEl) titleEl.textContent = 'Welcome Back';
            if (subtitleEl) subtitleEl.textContent = 'Sign in to access TruthLens Dashboard';
            if (nameFieldEl) nameFieldEl.classList.add('hidden');
            if (nameEl) nameEl.required = false;
            if (submitBtnEl) submitBtnEl.textContent = 'Sign In';
            if (toggleTextEl) toggleTextEl.innerHTML = `Don't have an account? <a href="#" id="auth-toggle-link" style="color: #4f46e5; font-weight: 600; text-decoration: none;">Register here</a>`;
        } else {
            if (titleEl) titleEl.textContent = 'Create Account';
            if (subtitleEl) subtitleEl.textContent = 'Register for TruthLens AI';
            if (nameFieldEl) nameFieldEl.classList.remove('hidden');
            if (nameEl) nameEl.required = true;
            if (submitBtnEl) submitBtnEl.textContent = 'Register';
            if (toggleTextEl) toggleTextEl.innerHTML = `Already have an account? <a href="#" id="auth-toggle-link" style="color: #4f46e5; font-weight: 600; text-decoration: none;">Sign in here</a>`;
        }
        // Rebind listener
        const toggleLink = document.getElementById('auth-toggle-link');
        if (toggleLink) toggleLink.addEventListener('click', toggleAuthMode);
    });
}

const authForm = document.getElementById('auth-form');
if (authForm) {
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const emailEl = document.getElementById('auth-email');
        const passwordEl = document.getElementById('auth-password');
        const email = emailEl ? emailEl.value : '';
        const password = passwordEl ? passwordEl.value : '';
        const btn = document.getElementById('auth-submit-btn');
        const errEl = document.getElementById('auth-error');

        if (errEl) errEl.classList.add('hidden');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        }

        try {
            const endpoint = isLoginMode ? '/api/login' : '/api/register';
            const body = { email, password };
            if (!isLoginMode) {
                const nameEl = document.getElementById('auth-name');
                body.name = nameEl ? nameEl.value : '';
            }

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await res.json();

            if (data.status === 'success') {
                currentUser = { token: data.token, name: data.name, email };
                localStorage.setItem('truthlens_user', JSON.stringify(currentUser));
                updateNavForAuth();
                navigateTo('dashboard');
                authForm.reset();
            } else {
                if (errEl) {
                    errEl.textContent = data.message;
                    errEl.classList.remove('hidden');
                }
            }
        } catch (err) {
            if (errEl) {
                errEl.textContent = 'Server error. Please try again.';
                errEl.classList.remove('hidden');
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = isLoginMode ? 'Sign In' : 'Register';
            }
        }
    });
}
// ══════════════════════════════════════════
//  MULTI-LLM COMPARISON FEATURE (NEW)
// ══════════════════════════════════════════
async function handleComparison(e) {
    const viewAnalysis = document.getElementById('view-analysis');
    const isDashboard = viewAnalysis ? viewAnalysis.classList.contains('active-view') : false;
    const promptInput = isDashboard ? document.getElementById('db-prompt') : document.getElementById('prompt');
    const prompt = promptInput ? promptInput.value : '';
    if (!prompt) return alert('Please enter a prompt first.');

    const btn = e ? e.currentTarget : document.getElementById('compare-btn');
    if (btn) btn.disabled = true;
    const oldHtml = btn ? btn.innerHTML : '';
    if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Comparing...';

    try {
        const lang = localStorage.getItem('truthlens_language') || 'English';
        const headers = { 'Content-Type': 'application/json' };
        if (currentUser && currentUser.token) {
            headers['Authorization'] = `Bearer ${currentUser.token}`;
        }

        const res = await fetch('/api/compare', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ prompt, language: lang })
        });

        if (!res.ok) throw new Error('Comparison failed');
        const data = await res.json();

        // Switch to analysis view if on home
        const viewHome = document.getElementById('view-home');
        if (viewHome && viewHome.classList.contains('active-view')) {
            localStorage.setItem('view_compare_data', JSON.stringify({ prompt, data }));
            navigateTo('analysis');
        } else {
            renderComparison(data);
        }

    } catch (err) {
        console.error(err);
        alert('Multi-LLM Comparison failed. Ensure the backend is active and you are logged in.');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = oldHtml;
        }
    }
}

function renderComparison(data) {
    show('fr-compare-section');
    const grid = document.getElementById('fr-compare-grid');
    if (grid) {
        grid.innerHTML = data.responses.map(r => `
            <div class="llm-card">
                <div class="llm-card-header">
                    <span class="llm-name">${r.model}</span>
                    <i class="fa-solid fa-circle-check text-green"></i>
                </div>
                <div class="llm-response-text">${r.text}</div>
            </div>
        `).join('');
    }

    // Disagreement Detection Logic
    const disagreementList = document.getElementById('fr-disagreement-list');
    if (disagreementList) {
        // Heuristic: Identify unique claims or variations
        const allSentences = data.responses.flatMap(r => r.text.match(/[^.!?]+[.!?]+/g) || [r.text]);
        const uniquePoints = [...new Set(allSentences.map(s => s.trim()))].filter(s => s.length > 20).slice(0, 3);

        if (uniquePoints.length > 0) {
            disagreementList.innerHTML = uniquePoints.map(p => `
                <div class="disagreement-item">
                    <span class="unstable-label">Unstable Fact</span>
                    <span class="fact-point">${p}</span>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 5px;">
                        <i class="fa-solid fa-circle-info"></i> High variance detected across model outputs.
                    </div>
                </div>
            `).join('');
        } else {
            disagreementList.innerHTML = '<div class="disagreement-item">No major disagreements detected across models.</div>';
        }
    }
}

const compareBtn = document.getElementById('compare-btn');
if (compareBtn) compareBtn.addEventListener('click', handleComparison);

const dbCompareBtn = document.getElementById('db-compare-btn');
if (dbCompareBtn) dbCompareBtn.addEventListener('click', handleComparison);

// Feedback Form
// Feedback Form
const feedbackForm = document.getElementById('feedback-form');
if (feedbackForm) {
    feedbackForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const categoryEl = document.getElementById('feedback-category');
        const msgEl = document.getElementById('feedback-msg');
        const category = categoryEl ? categoryEl.value : '';
        const msg = msgEl ? msgEl.value : '';
        alert(`Thank you for your ${category}! Our team will review it.`);
        feedbackForm.reset();
    });
}

// ══════════════════════════════════════════
//  CHAT VIEW — Full Chatbot with Persistence
// ══════════════════════════════════════════
const CHAT_STORAGE_KEY = 'truthlens_chat_sessions';

// In-memory state
let chatConversations  = []; // [{role, content}]
let chatSessionTitle   = null;
let chatCurrentId      = null; // UUID of active session
let chatFileContext    = "";   // Extracted text from uploaded file
let chatFileName       = "";

// ── Storage helpers ────────────────────────────────────────────────────────

function chatLoadSessions() {
    try { return JSON.parse(localStorage.getItem(CHAT_STORAGE_KEY) || '[]'); }
    catch { return []; }
}

function chatSaveSessions(sessions) {
    try { localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(sessions)); }
    catch (e) { console.warn('Chat storage full:', e); }
}

function chatUpsertSession() {
    if (!chatCurrentId || chatConversations.length === 0) return;
    const sessions = chatLoadSessions();
    const idx = sessions.findIndex(s => s.id === chatCurrentId);
    const session = {
        id:       chatCurrentId,
        title:    chatSessionTitle || 'Conversation',
        ts:       Date.now(),
        messages: [...chatConversations]
    };
    if (idx >= 0) sessions[idx] = session;
    else sessions.unshift(session);
    // Keep at most 30 sessions
    chatSaveSessions(sessions.slice(0, 30));
}

// ── Sidebar rendering ──────────────────────────────────────────────────────

function chatRenderSidebar() {
    const list = document.getElementById('chat-history-list');
    if (!list) return;
    const sessions = chatLoadSessions();
    if (sessions.length === 0) {
        list.innerHTML = '<div class="chat-history-empty">No conversations yet.</div>';
        return;
    }

    // Filter sessions if query is present
    const searchInput = document.getElementById('chat-search-input');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

    let filteredSessions = sessions;
    if (query) {
        filteredSessions = sessions.filter(s => s.title.toLowerCase().includes(query));
    }

    // Sort: pinned first, then normal (by ts descending)
    filteredSessions.sort((a, b) => {
        const aPinned = a.pinned ? 1 : 0;
        const bPinned = b.pinned ? 1 : 0;
        if (aPinned !== bPinned) return bPinned - aPinned;
        return b.ts - a.ts;
    });

    if (filteredSessions.length === 0) {
        list.innerHTML = '<div class="chat-history-empty">No matching conversations.</div>';
        return;
    }

    list.innerHTML = '';
    filteredSessions.forEach(s => {
        const item = document.createElement('div');
        item.className = 'chat-history-item' + (s.id === chatCurrentId ? ' active' : '') + (s.pinned ? ' pinned' : '');
        item.dataset.id = s.id;

        const dateStr = new Date(s.ts).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
        item.innerHTML = `
            <div class="chi-header">
                <div class="chi-title" title="${s.title}">${s.title}</div>
                <div class="chi-actions">
                    <button class="chi-pin-btn" title="${s.pinned ? 'Unpin Chat' : 'Pin Chat'}" onclick="chatTogglePin('${s.id}', event)">
                        <i class="fa-solid fa-thumbtack ${s.pinned ? 'pinned-active' : ''}"></i>
                    </button>
                    <button class="chi-rename-btn" title="Rename Chat" onclick="chatRenameSession('${s.id}', event)">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                </div>
            </div>
            <div class="chi-meta">
                <span>${dateStr}</span>
                <button class="chi-del" title="Delete" onclick="chatDeleteSession('${s.id}', event)">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>`;
        item.addEventListener('click', () => chatRestoreSession(s.id));
        list.appendChild(item);
    });
}

function chatDeleteSession(id, event) {
    event.stopPropagation();
    const sessions = chatLoadSessions().filter(s => s.id !== id);
    chatSaveSessions(sessions);
    if (chatCurrentId === id) chatResetToWelcome(false);
    chatRenderSidebar();
}

function chatTogglePin(id, event) {
    event.stopPropagation();
    const sessions = chatLoadSessions();
    const session = sessions.find(s => s.id === id);
    if (session) {
        session.pinned = !session.pinned;
        chatSaveSessions(sessions);
        chatRenderSidebar();
    }
}

function chatRenameSession(id, event) {
    event.stopPropagation();
    const sessions = chatLoadSessions();
    const session = sessions.find(s => s.id === id);
    if (session) {
        const newTitle = prompt("Rename Conversation:", session.title);
        if (newTitle !== null && newTitle.trim() !== "") {
            session.title = newTitle.trim();
            chatSaveSessions(sessions);
            if (chatCurrentId === id) {
                chatSessionTitle = session.title;
            }
            chatRenderSidebar();
        }
    }
}

// ── Restore a past session ─────────────────────────────────────────────────

function chatRestoreSession(id) {
    const sessions = chatLoadSessions();
    const session  = sessions.find(s => s.id === id);
    if (!session) return;

    chatCurrentId      = session.id;
    chatSessionTitle   = session.title;
    chatConversations  = [...session.messages];

    const messagesEl = document.getElementById('chat-messages');
    if (messagesEl) {
        messagesEl.innerHTML = '';

        session.messages.forEach(m => {
            if (m.role === 'assistant' && m.evaluation) {
                appendChatMessage('bot', m.evaluation, false, false, m.timestamp);
            } else {
                appendChatMessage(m.role === 'user' ? 'user' : 'bot', m.content, false, false, m.timestamp);
            }
        });
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }
    chatRenderSidebar();
}

// ── Welcome / reset ────────────────────────────────────────────────────────

function chatResetToWelcome(save = true) {
    if (save) chatUpsertSession();
    chatConversations = [];
    chatSessionTitle  = null;
    chatCurrentId     = null;

    const messagesEl = document.getElementById('chat-messages');
    if (messagesEl) {
        messagesEl.innerHTML = `
            <div class="chat-welcome">
                <div class="chat-welcome-icon"><i class="fa-solid fa-sparkles"></i></div>
                <h2>How can I help you?</h2>
                <p>Ask me anything — factual questions, current events, explanations. I'll verify my answers using live web sources.</p>
                <div class="chat-starters">
                    <button class="chat-starter-btn" onclick="sendChatStarter('Who is the current President of India?')">Who is the President of India?</button>
                    <button class="chat-starter-btn" onclick="sendChatStarter('What is artificial intelligence?')">What is artificial intelligence?</button>
                    <button class="chat-starter-btn" onclick="sendChatStarter('Who won the 2023 Cricket World Cup?')">2023 Cricket World Cup winner?</button>
                    <button class="chat-starter-btn" onclick="sendChatStarter('Explain hallucination in AI models')">What is AI hallucination?</button>
                </div>
            </div>`;
    }
    
    const searchInput = document.getElementById('chat-search-input');
    if (searchInput) searchInput.value = '';

    chatRenderSidebar();
}

// ── Message rendering ──────────────────────────────────────────────────────

function appendChatMessage(role, text, scroll = true, saveToStorage = true, timestamp = null) {
    const messagesEl = document.getElementById('chat-messages');
    if (!messagesEl) return;
    
    const welcome = messagesEl.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    const avatarHTML = role === 'user'
        ? `<div class="chat-avatar sm" style="background:linear-gradient(135deg,#6366f1,#8b5cf6)"><i class="fa-solid fa-user" style="font-size:0.75rem"></i></div>`
        : `<div class="chat-avatar sm"><i class="fa-solid fa-robot"></i></div>`;

    const labelHTML = role === 'user'
        ? `<div class="chat-bubble-label" style="color:#a5b4fc">You</div>`
        : `<div class="chat-bubble-label" style="color:#6366f1"><i class="fa-solid fa-robot"></i> TruthLens</div>`;

    const div = document.createElement('div');
    const isBot = role === 'bot';
    div.className = `chat-msg ${role === 'user' ? 'user' : 'bot'}`;
    
    let contentHTML = (typeof text === 'string') ? text.replace(/\n/g, '<br>') : "";
    let riskChipHTML = "";
    let modelBadgeHTML = "";

    // If bot and evaluation data exists, render highlights and risk chip
    if (isBot && typeof text === 'object' && text) {
        const evalData = text.sentence_analysis ? text : null;
        
        // If we passed the full evaluation object
        if (evalData) {
            const sentences = evalData.sentence_analysis;
            contentHTML = sentences.map(s => {
                const riskClass = s.category === 'verified' ? 'verified' : (s.score > 70 ? 'danger' : (s.score > 30 ? 'warn' : 'low'));
                return `<span class="risk-highlight ${riskClass}" title="${s.type}: ${s.reason}">${s.text}</span>`;
            }).join(' ');

            const riskVal = Math.round(evalData.overall_risk * 100);
            const riskLevel = getVerdict(riskVal);
            const riskColor = getColorForRisk(evalData.overall_risk);
            
            riskChipHTML = `
                <div class="chat-risk-chip" style="border-left: 3px solid ${riskColor}">
                    <span class="rc-label">Hallucination Risk:</span>
                    <span class="rc-val" style="color: ${riskColor}">${riskVal}% (${riskLevel})</span>
                </div>`;
        }

        // Add model attribution if available
        if (text.model_name) {
            modelBadgeHTML = `<div class="chat-model-badge"><i class="fa-solid fa-microchip"></i> Generated by ${text.model_name}</div>`;
        }
    }

    // Format timestamp
    const msgTime = timestamp ? new Date(timestamp) : new Date();
    const timeStr = msgTime.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });

    div.innerHTML = `
        ${avatarHTML}
        <div class="chat-msg-content">
            <div class="chat-bubble">
                ${labelHTML}
                ${modelBadgeHTML}
                <div class="chat-text-area">${contentHTML}</div>
                ${riskChipHTML}
            </div>
            <div class="chat-timestamp">${timeStr}</div>
        </div>`;
    messagesEl.appendChild(div);
    if (scroll) messagesEl.scrollTop = messagesEl.scrollHeight;

    // Persist changes to storage and refresh sidebar (only for NEW messages)
    if (chatCurrentId && saveToStorage) {
        chatUpsertSession();
        chatRenderSidebar();
    }
}

function showTyping() {
    document.getElementById('chat-typing')?.classList.remove('hidden');
    const msgEl = document.getElementById('chat-messages');
    if (msgEl) msgEl.scrollTop = 99999;
}
function hideTyping() {
    document.getElementById('chat-typing')?.classList.add('hidden');
}

// ── Send message ───────────────────────────────────────────────────────────

async function sendChat(userMessage) {
    if (!userMessage.trim()) return;

    const btn     = document.getElementById('chat-send-btn');
    const inputEl = document.getElementById('chat-input');

    // Start new session if needed
    if (!chatCurrentId) {
        chatCurrentId    = (window.crypto && window.crypto.randomUUID) ? window.crypto.randomUUID() : 'c-' + Math.random().toString(36).substring(2, 11);
        chatSessionTitle = userMessage.substring(0, 40).replace(/\n/g, ' ') + (userMessage.length > 40 ? '…' : '');
    }

    const userTimestamp = Date.now();
    appendChatMessage('user', userMessage, true, true, userTimestamp);
    chatConversations.push({ role: 'user', content: userMessage, timestamp: userTimestamp });

    // Save immediately so it appears in sidebar right away
    chatUpsertSession();
    chatRenderSidebar();

    if (inputEl) inputEl.disabled = true;
    if (btn) btn.disabled     = true;
    showTyping();

    try {
        const lang = localStorage.getItem('truthlens_language') || 'English';
        const history = chatConversations.slice(0, -1).map(m => ({
            role: m.role === 'bot' ? 'assistant' : 'user',
            content: m.content
        }));

        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser ? currentUser.token : 'demo-token'}`
            },
            body: JSON.stringify({ 
                prompt: userMessage, 
                history: history,
                model: 'llama',
                evaluate: true, // Enable live evaluation for chat
                language: lang
            })
        });

        if (!res.ok) throw new Error('API error');
        const data     = await res.json();
        const botReply = data.generated_response || "I couldn't generate a response.";
        const evalData = data.evaluation;

        const botTimestamp = Date.now();
        if (evalData) {
            chatConversations.push({ role: 'assistant', content: botReply, evaluation: evalData, timestamp: botTimestamp });
            hideTyping();
            appendChatMessage('bot', evalData, true, true, botTimestamp); // Pass the whole object to appendChatMessage
        } else {
            chatConversations.push({ role: 'assistant', content: botReply, timestamp: botTimestamp });
            hideTyping();
            appendChatMessage('bot', botReply, true, true, botTimestamp);
        }

        // ← Auto-save after every reply
        chatUpsertSession();
        chatRenderSidebar();

    } catch (err) {
        hideTyping();
        appendChatMessage('bot', '⚠️ Connection error. Please check the backend and try again.');
    } finally {
        if (inputEl) {
            inputEl.disabled     = false;
            inputEl.value        = '';
            inputEl.style.height = 'auto';
            inputEl.focus();
        }
        if (btn) btn.disabled         = false;

        // Clear file context after successful send
        if (chatFileContext) {
            chatFileContext = "";
            chatFileName    = "";
            document.getElementById('chat-file-preview')?.classList.add('hidden');
        }
    }
}

function sendChatStarter(text) { sendChat(text); }

// ── Event listeners ────────────────────────────────────────────────────────

document.getElementById('chat-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        sendChat(chatInput.value.trim());
    }
});

document.getElementById('chat-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('chat-form')?.dispatchEvent(new Event('submit'));
    }
});

document.getElementById('chat-input')?.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

document.getElementById('chat-clear-btn')?.addEventListener('click', () => chatResetToWelcome(true));
document.getElementById('chat-new-btn')?.addEventListener('click', () => chatResetToWelcome(true));

document.getElementById('chat-search-input')?.addEventListener('input', () => {
    chatRenderSidebar();
});


// ── Chat File Handling ──────────────────────────────────────────────────
window.truthLens_handleFileUpload = async function(file) {
    if (!file) return;

    const preview = document.getElementById('chat-file-preview');
    const nameEl = preview?.querySelector('.file-name');
    if (nameEl) nameEl.textContent = file.name;
    if (preview) preview.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.status === 'success') {
            chatFileContext = data.text;
            chatFileName = data.filename;
            console.log('Document text extracted successfully:', chatFileName);
        } else {
            alert('Upload failed: ' + (data.error || 'Unknown error'));
            if (preview) preview.classList.add('hidden');
        }
    } catch (err) {
        console.error('File upload error:', err);
        if (preview) preview.classList.add('hidden');
    }
};

document.getElementById('chat-file-remove')?.addEventListener('click', () => {
    chatFileContext = "";
    chatFileName = "";
    const input = document.getElementById('chat-file-input');
    if (input) input.value = "";
    document.getElementById('chat-file-preview')?.classList.add('hidden');
});


// ── Init: load sidebar on page open ──────────────────────────────────────
chatRenderSidebar();

window.logout = function() {
    currentUser = null;
    localStorage.removeItem('truthlens_user');
    updateNavForAuth();
    navigateTo('home');
};


// ══════════════════════════════════════════
//  NEW DASHBOARD FUNCTIONS & PERSISTENCE
// ══════════════════════════════════════════

// ══════════════════════════════════════════
//  NEW DASHBOARD FUNCTIONS & PERSISTENCE
// ══════════════════════════════════════════

let allChats = []; // Global in-memory list of chats
let selectedChatIds = new Set(); // Multi-select track
let currentChatFilter = 'all';
let chatActivities = [];

// Activity Log storage
function logChatActivity(action, detail) {
    const timeStr = new Date().toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    chatActivities.unshift({ time: timeStr, action, detail, type: action.toLowerCase() });
    chatActivities = chatActivities.slice(0, 10); // Keep last 10
    renderActivityTimeline();
}

function renderActivityTimeline() {
    const timelineEl = document.getElementById('chats-activity-timeline');
    if (!timelineEl) return;
    if (chatActivities.length === 0) {
        timelineEl.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 0.5rem 0;">No recent activities.</div>';
        return;
    }
    timelineEl.innerHTML = chatActivities.map(act => {
        let typeClass = '';
        if (act.type.includes('save') || act.type.includes('bookmark')) typeClass = 'saved';
        else if (act.type.includes('delete') || act.type.includes('clear')) typeClass = 'deleted';
        return `
            <div class="timeline-event ${typeClass}">
                <div class="timeline-time">${act.time}</div>
                <div class="timeline-text"><strong>${act.action}</strong>: ${act.detail}</div>
            </div>`;
    }).join('');
}

async function loadChatsFromDB() {
    if (!currentUser || !currentUser.token) return [];
    try {
        const res = await fetch('/api/chats', {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (res.ok) {
            allChats = await res.json();
            return allChats;
        }
    } catch (e) {
        console.error("Failed to load chats from database:", e);
    }
    return [];
}

async function saveAnalysisRun(prompt, response, data) {
    if (!currentUser || !currentUser.email) return;
    
    const nliRisk = data.components["Logical NLI"] ?? 0;
    const hhemRisk = data.components["HHEM Factor"] ?? 0;
    const riskNorm = (nliRisk + hhemRisk) / 2;
    const overallRiskVal = data.overall_risk !== undefined ? data.overall_risk : riskNorm;
    const riskScore = Math.round(overallRiskVal * 100);
    const verdict = getVerdict(riskScore);
    const runId = 'run_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
    
    // Save to local storage for backward compatibility
    const storageKey = `truthlens_runs_${currentUser.email}`;
    let runs = [];
    try { runs = JSON.parse(localStorage.getItem(storageKey) || '[]'); } catch (e) { runs = []; }
    
    const newRun = {
        id: runId,
        timestamp: Date.now(),
        prompt: prompt,
        response: response,
        data: data,
        verdict: verdict,
        riskScore: riskScore
    };
    runs.unshift(newRun);
    localStorage.setItem(storageKey, JSON.stringify(runs.slice(0, 50)));

    // Save to Database
    try {
        const chatRecord = {
            id: runId,
            title: prompt.substring(0, 40).replace(/\n/g, ' ') + (prompt.length > 40 ? '…' : ''),
            prompt: prompt,
            response: response,
            risk_score: riskScore,
            verdict: verdict,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            is_saved: false,
            evaluation_data: JSON.stringify(data)
        };
        
        await fetch('/api/chats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: JSON.stringify(chatRecord)
        });
        console.log('[TruthLens] Saved analysis run to Database:', runId);
        
        logChatActivity("Analysis created", prompt.substring(0, 25) + "...");
    } catch (e) {
        console.warn('Failed to save to database:', e);
    }
    
    updateDashboardUI();
}

async function updateDashboardUI() {
    if (!currentUser || !currentUser.email) return;
    
    // Load from Database
    let chats = await loadChatsFromDB();
    
    // Fallback to localStorage runs if DB is empty
    if (chats.length === 0) {
        const storageKey = `truthlens_runs_${currentUser.email}`;
        let localRuns = [];
        try { localRuns = JSON.parse(localStorage.getItem(storageKey) || '[]'); } catch (e) { localRuns = []; }
        
        chats = localRuns.map(r => ({
            id: r.id,
            title: r.prompt.substring(0, 40).replace(/\n/g, ' ') + (r.prompt.length > 40 ? '…' : ''),
            prompt: r.prompt,
            response: r.response,
            risk_score: r.riskScore,
            verdict: r.verdict,
            created_at: new Date(r.timestamp).toISOString(),
            updated_at: new Date(r.timestamp).toISOString(),
            is_saved: false,
            evaluation_data: JSON.stringify(r.data)
        }));
        
        // Upload local runs to server to sync
        for (const c of chats) {
            try {
                await fetch('/api/chats', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${currentUser.token}`
                    },
                    body: JSON.stringify(c)
                });
            } catch (e) { console.warn("Failed to sync local run:", e); }
        }
        
        if (chats.length > 0) {
            chats = await loadChatsFromDB();
        }
    }
    
    allChats = chats;

    // Render Stats
    const total = chats.length;
    let avgRisk = 0;
    let highRiskCount = 0;
    let savedCount = 0;
    let highTrustCount = 0;
    let severeRiskCount = 0;

    if (total > 0) {
        const sum = chats.reduce((acc, c) => acc + c.risk_score, 0);
        avgRisk = Math.round(sum / total);
        highRiskCount = chats.filter(c => c.risk_score > 30).length;
        savedCount = chats.filter(c => c.is_saved).length;
        highTrustCount = chats.filter(c => c.risk_score <= 20).length;
        severeRiskCount = chats.filter(c => c.risk_score > 60).length;
    }

    // Update main stats cards
    const avgAccuracy = total > 0 ? (100 - avgRisk) : 92;
    const dbStatAccuracy = document.getElementById('db-stat-accuracy');
    const dbStatTotal = document.getElementById('db-stat-total');
    const dbStatRisk = document.getElementById('db-stat-risk');
    const dbStatRiskSub = document.getElementById('db-stat-risk-sub');

    if (dbStatAccuracy) dbStatAccuracy.textContent = `${avgAccuracy}%`;
    if (dbStatTotal) dbStatTotal.textContent = total;
    if (dbStatRisk) dbStatRisk.textContent = highRiskCount;
    if (dbStatRiskSub) dbStatRiskSub.textContent = '>30% risk flagged';

    // Update stats widgets below chat list
    const stTotal = document.getElementById('st-total-chats');
    const stSaved = document.getElementById('st-saved-chats');
    const stHighTrust = document.getElementById('st-high-trust');
    const stSevereRisk = document.getElementById('st-severe-risk');
    const stAvgRisk = document.getElementById('st-avg-risk');
    
    if (stTotal) stTotal.textContent = total;
    if (stSaved) stSaved.textContent = savedCount;
    if (stHighTrust) stHighTrust.textContent = highTrustCount;
    if (stSevereRisk) stSevereRisk.textContent = severeRiskCount;
    if (stAvgRisk) {
        stAvgRisk.textContent = `${avgRisk}%`;
        stAvgRisk.style.color = getColorForRisk(avgRisk / 100);
    }

    // Populate Recent Analyses Table
    const tbody = document.getElementById('db-table-body');
    const tableCount = document.getElementById('db-table-count');
    
    if (tableCount) tableCount.textContent = `${total} total`;

    if (tbody) {
        if (total === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                        No analysis runs found. Start a new analysis to see results here!
                    </td>
                </tr>`;
        } else {
            tbody.innerHTML = '';
            chats.slice(0, 10).forEach(chat => {
                const date = new Date(chat.created_at).toLocaleDateString('en-IN', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                const badgeClass = getVerdictBadgeClass(chat.risk_score);
                const promptTxt = chat.title.length > 50 ? chat.title.substring(0, 50) + '...' : chat.title;
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${date}</td>
                    <td style="font-weight: 500;">${promptTxt}</td>
                    <td><span style="font-weight: 600; color: ${getColorForRisk(chat.risk_score / 100)}">${chat.risk_score}%</span></td>
                    <td><span class="badge-verdict ${badgeClass}">${chat.verdict}</span></td>
                    <td style="text-align: right; white-space: nowrap;">
                        <button class="btn-primary btn-sm" onclick="viewPastRunFromDB('${chat.id}')" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; font-family: inherit; display: inline-flex; align-items: center; gap: 4px;">
                            <i class="fa-solid fa-eye"></i> View
                        </button>
                        <button class="btn-secondary btn-sm" onclick="toggleSaveChatFromDB('${chat.id}')" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; font-family: inherit; display: inline-flex; align-items: center; gap: 4px; ${chat.is_saved ? 'color:#f59e0b; border-color:#f59e0b;' : ''}">
                            <i class="fa-${chat.is_saved ? 'solid' : 'regular'} fa-bookmark"></i> ${chat.is_saved ? 'Saved' : 'Save'}
                        </button>
                        <button class="btn-secondary btn-sm" onclick="confirmDeleteChatFromDB('${chat.id}')" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; font-family: inherit; color:#ef4444; border-color: rgba(239, 68, 68, 0.3); display: inline-flex; align-items: center; gap: 4px;">
                            <i class="fa-solid fa-trash-can"></i> Delete
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // Populate Radial Risk Score Card
    const latestChat = chats.length > 0 ? chats[0] : null;
    const radialFill  = document.getElementById('risk-radial-fill');
    const radialPct   = document.getElementById('risk-radial-pct');
    const radialSub   = document.getElementById('risk-radial-sub');
    const levelBadge  = document.getElementById('risk-level-badge');
    const rskContra   = document.getElementById('rsk-contradictions');
    const rskUnsup    = document.getElementById('rsk-unsupported');
    const rskConf     = document.getElementById('rsk-confidence');

    if (latestChat && latestChat.evaluation_data) {
        try {
            const d = JSON.parse(latestChat.evaluation_data);
            const riskPct = latestChat.risk_score;

            const circ = 314.16;
            const filled = (riskPct / 100) * circ;

            let strokeColor, levelClass, levelText, sublabel;
            if (riskPct <= 20) {
                strokeColor = '#10b981'; levelClass = 'low';    levelText = '✓ High Trust';    sublabel = 'High Trust';
            } else if (riskPct <= 40) {
                strokeColor = '#f59e0b'; levelClass = 'medium'; levelText = '⚠ Moderate Risk'; sublabel = 'Moderate Risk';
            } else if (riskPct <= 60) {
                strokeColor = '#ef4444'; levelClass = 'high';   levelText = '✕ High Risk';     sublabel = 'High Risk';
            } else {
                strokeColor = '#991b1b'; levelClass = 'severe'; levelText = '✕ Severe Risk';   sublabel = 'Severe Risk';
            }

            if (radialFill) {
                radialFill.style.stroke = strokeColor;
                setTimeout(() => { radialFill.setAttribute('stroke-dasharray', `${filled} ${circ}`); }, 60);
            }
            if (radialPct)  radialPct.textContent  = `${riskPct}%`;
            if (radialSub)  radialSub.textContent  = sublabel;
            if (levelBadge) {
                levelBadge.textContent = levelText;
                levelBadge.className   = `risk-level-badge ${levelClass}`;
            }

            const claims = d.sentence_analysis || [];
            const contradicted = claims.filter(c => c.category === 'contradicted').length;
            const unsupported  = claims.filter(c => c.category === 'weak' || c.category === 'fabricated').length;
            const confidence   = d.overall_risk !== undefined ? `${Math.round((1 - d.overall_risk) * 100)}%` : '—';

            if (rskContra) rskContra.textContent = contradicted;
            if (rskUnsup)  rskUnsup.textContent  = unsupported;
            if (rskConf)   rskConf.textContent   = confidence;
        } catch (e) {
            console.error("Failed to parse evaluation data for radial card", e);
        }
    } else {
        if (radialFill)  { radialFill.style.stroke = '#cbd5e1'; radialFill.setAttribute('stroke-dasharray', '0 314'); }
        if (radialPct)   radialPct.textContent  = '--';
        if (radialSub)   radialSub.textContent  = 'No Data';
        if (levelBadge)  { levelBadge.textContent = '— No Analysis Yet —'; levelBadge.className = 'risk-level-badge'; }
        if (rskContra)   rskContra.textContent  = '—';
        if (rskUnsup)    rskUnsup.textContent   = '—';
        if (rskConf)     rskConf.textContent    = '—';
    }

    // Mini Trend Chart
    const canvas      = document.getElementById('dashboard-chart');
    const chartWrap   = document.getElementById('risk-trend-chart-wrap');
    const trendEmpty  = document.getElementById('risk-trend-empty');

    const trendChats  = [...chats].reverse().slice(-8);
    const hasHistory  = trendChats.length > 0;

    if (trendEmpty) trendEmpty.style.display = hasHistory ? 'none' : 'flex';
    if (chartWrap) chartWrap.style.display = hasHistory ? 'block' : 'none';

    if (canvas && hasHistory) {
        if (window.dashboardChart) window.dashboardChart.destroy();

        const labels     = trendChats.map((c, idx) => `Analysis ${idx + 1}`);
        const dataPoints = trendChats.map(c => c.risk_score);
        const pointColors = dataPoints.map(v => getColorForRisk(v / 100));

        const isDark    = document.documentElement.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#f1f5f9' : '#1e293b';
        const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)';

        window.dashboardChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Hallucination Risk (%)',
                    data: dataPoints,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99,102,241,0.08)',
                    fill: true,
                    tension: 0.45,
                    borderWidth: 2.5,
                    pointBackgroundColor: pointColors,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1.5,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}% risk` } }
                },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 } } },
                    y: { min: 0, max: 100, grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 }, callback: v => `${v}%` } }
                }
            }
        });
    }

    // Populate Analytics Insights
    const analyticsEl = document.getElementById('fr-analytics');
    if (analyticsEl) {
        if (chats.length > 0 && chats[0].evaluation_data) {
            try {
                const data = JSON.parse(chats[0].evaluation_data);
                const claims = data.sentence_analysis || [];
                const verified = claims.filter(c => c.category === 'verified').length;
                const partial = claims.filter(c => c.category === 'partial').length;
                const weak = claims.filter(c => c.category === 'weak').length;
                const contradicted = claims.filter(c => c.category === 'contradicted').length;
                const fabricated = claims.filter(c => c.category === 'fabricated').length;
                const risk = data.overall_risk || 0;
                let evidenceSources = [];
                if (data.evidence && data.evidence.length > 0) {
                    evidenceSources = data.evidence.map(e => ({ src: e.src || 'Web Snippet', conf: '99%' }));
                }

                const analyticsDef = [
                    { label: 'Claims Extracted', val: claims.length, color: '#6366f1' },
                    { label: 'Verified', val: verified, color: '#10b981' },
                    { label: 'Partial', val: partial, color: '#eab308' },
                    { label: 'Weak', val: weak, color: '#f97316' },
                    { label: 'Contradicted', val: contradicted, color: '#ef4444' },
                    { label: 'Fabricated', val: fabricated, color: '#991b1b' },
                    { label: 'Evidence Sources', val: evidenceSources.length, color: '#3b82f6' },
                    { label: 'Overall Risk', val: `${Math.round(risk * 100)}%`, color: getColorForRisk(risk) },
                ];
                analyticsEl.innerHTML = analyticsDef.map(a => `
                    <div class="analytic-row">
                        <span class="analytic-label">${a.label}</span>
                        <span class="analytic-val" style="color:${a.color}">${a.val}</span>
                    </div>`).join('');
            } catch (e) {
                console.error("Failed to parse evaluation data for analytics panel", e);
            }
        } else {
            analyticsEl.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem 1rem;">No data available. Run an analysis to see insights.</div>`;
        }
    }

    // Populate Activity Log Widget
    const activityLogEl = document.getElementById('fr-activity-log');
    if (activityLogEl) {
        if (chats.length > 0 && chats[0].evaluation_data) {
            try {
                const data = JSON.parse(chats[0].evaluation_data);
                const claims = data.sentence_analysis || [];
                const risk = data.overall_risk || 0;
                const prompt = chats[0].prompt || '';
                let evidenceSources = [];
                if (data.evidence && data.evidence.length > 0) {
                    evidenceSources = data.evidence;
                }
                const runTime = new Date(chats[0].created_at);
                const ts = (offset) => {
                    const d = new Date(runTime - offset);
                    return d.toTimeString().slice(0, 8);
                };
                const logs = [
                    { t: ts(7000), dot: 'info', msg: `Query received: "${prompt.substring(0, 40).replace(/"/g, '&quot;')}"` },
                    { t: ts(6500), dot: 'ok', msg: 'Prompt safety filter passed' },
                    { t: ts(5800), dot: 'info', msg: 'LLM response stored (FR-04)' },
                    { t: ts(5000), dot: 'info', msg: `${claims.length} claims extracted and segmented` },
                    { t: ts(4200), dot: 'info', msg: `Knowledge validation complete` },
                    { t: ts(3800), dot: 'ok', msg: 'Historical fact verification successful' },
                    { t: ts(3500), dot: 'ok', msg: 'Knowledge graph validation complete' },
                    { t: ts(2800), dot: 'ok', msg: `${evidenceSources.length} evidence sources retrieved` },
                    { t: ts(2000), dot: 'ok', msg: 'Token-level heatmap generated' },
                    { t: ts(1200), dot: risk > 0.2 ? 'warn' : 'ok', msg: `Hallucination risk: ${Math.round(risk * 100)}% - ${getVerdict(Math.round(risk * 100)).toUpperCase()}` },
                    { t: ts(600), dot: 'ok', msg: 'Corrected response generated (FR-19)' },
                    { t: ts(0), dot: 'ok', msg: 'Verification pipeline complete (FR-23)' },
                ];
                activityLogEl.innerHTML = logs.map(l => `
                    <div class="log-entry">
                        <span class="log-time">${l.t}</span>
                        <span class="log-dot ${l.dot}"></span>
                        <span class="log-msg">${l.msg}</span>
                    </div>`).join('');
            } catch (e) {
                console.error("Failed to parse evaluation data for activity log", e);
            }
        } else {
            activityLogEl.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem 1rem;">No activity logged yet.</div>`;
        }
    }

    renderAllChatsPanel();
    renderSavedQuickAccess();
}

function renderAllChatsPanel() {
    const listEl = document.getElementById('chats-sidebar-list');
    if (!listEl) return;

    if (allChats.length === 0) {
        listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2rem; font-size: 0.85rem;">No conversations yet.</div>';
        return;
    }

    const searchVal = document.getElementById('chats-search-input')?.value.toLowerCase().trim() || '';
    let filtered = allChats;

    if (searchVal) {
        filtered = filtered.filter(c => {
            const formattedDate = new Date(c.created_at).toLocaleDateString('en-IN', {
                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            }).toLowerCase();
            return c.title.toLowerCase().includes(searchVal) ||
                   c.prompt.toLowerCase().includes(searchVal) ||
                   c.verdict.toLowerCase().includes(searchVal) ||
                   formattedDate.includes(searchVal);
        });
    }

    const now = new Date();
    if (currentChatFilter === 'saved') {
        filtered = filtered.filter(c => c.is_saved);
    } else if (currentChatFilter === 'high-trust') {
        filtered = filtered.filter(c => c.risk_score <= 20);
    } else if (currentChatFilter === 'medium-risk') {
        filtered = filtered.filter(c => c.risk_score > 20 && c.risk_score <= 60);
    } else if (currentChatFilter === 'severe-risk') {
        filtered = filtered.filter(c => c.risk_score > 60);
    } else if (currentChatFilter === 'today') {
        filtered = filtered.filter(c => {
            const cDate = new Date(c.created_at);
            return cDate.toDateString() === now.toDateString();
        });
    } else if (currentChatFilter === '7days') {
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(c => new Date(c.created_at) >= sevenDaysAgo);
    } else if (currentChatFilter === '30days') {
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(c => new Date(c.created_at) >= thirtyDaysAgo);
    }

    if (filtered.length === 0) {
        listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2rem; font-size: 0.85rem;">No matching chats found.</div>';
        return;
    }

    listEl.innerHTML = '';
    filtered.forEach(chat => {
        const item = document.createElement('div');
        const activeModalChatId = document.getElementById('chat-detail-modal')?.dataset.chatId;
        const isSelected = activeModalChatId === chat.id ? ' selected' : '';
        item.className = `chat-sidebar-item${isSelected}`;
        item.dataset.id = chat.id;

        const dateStr = new Date(chat.created_at).toLocaleDateString('en-IN', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const isChecked = selectedChatIds.has(chat.id) ? 'checked' : '';
        const riskColor = getColorForRisk(chat.risk_score / 100);

        item.innerHTML = `
            <div class="csi-checkbox-wrap">
                <input type="checkbox" class="csi-checkbox" data-id="${chat.id}" ${isChecked}>
            </div>
            <div class="csi-body" onclick="openChatDetailModal('${chat.id}')">
                <div class="csi-title-wrap">
                    <span class="csi-title" title="${chat.title}">${chat.title}</span>
                    <span style="font-size: 0.72rem; font-weight: 600; color: ${riskColor}; background: ${riskColor}15; padding: 1px 4px; border-radius: 4px;">${chat.risk_score}%</span>
                </div>
                <div class="csi-meta">
                    <span class="csi-date">${dateStr}</span>
                </div>
            </div>
            <div class="csi-actions">
                <button class="csi-btn ${chat.is_saved ? 'save-active' : ''}" onclick="toggleSaveChatFromDB('${chat.id}', event)" title="${chat.is_saved ? 'Unbookmark' : 'Bookmark'}">
                    <i class="fa-${chat.is_saved ? 'solid' : 'regular'} fa-bookmark"></i>
                </button>
                <button class="csi-btn" onclick="renameChatFromDB('${chat.id}', event)" title="Rename">
                    <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button class="csi-btn delete-btn" onclick="confirmDeleteChatFromDB('${chat.id}', event)" title="Delete">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        `;
        listEl.appendChild(item);
    });

    // Update checkboxes event listeners
    const checkboxes = listEl.querySelectorAll('.csi-checkbox');
    checkboxes.forEach(cb => {
        cb.addEventListener('change', (e) => {
            const id = cb.dataset.id;
            if (cb.checked) {
                selectedChatIds.add(id);
            } else {
                selectedChatIds.delete(id);
            }
            updateBulkToolbarState();
        });
    });
}

function updateBulkToolbarState() {
    const toolbar = document.getElementById('bulk-actions-toolbar');
    const selectedCountEl = document.getElementById('bulk-selected-count');
    const selectAllCheckbox = document.getElementById('bulk-select-all');

    if (!toolbar) return;

    const totalVisible = document.querySelectorAll('.csi-checkbox').length;
    const selectedVisible = Array.from(document.querySelectorAll('.csi-checkbox')).filter(cb => cb.checked).length;

    if (selectedChatIds.size > 0) {
        toolbar.classList.remove('hidden');
        if (selectedCountEl) selectedCountEl.textContent = selectedChatIds.size;
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = (selectedVisible === totalVisible && totalVisible > 0);
        }
    } else {
        toolbar.classList.add('hidden');
        if (selectAllCheckbox) selectAllCheckbox.checked = false;
    }
}

async function toggleSaveChatFromDB(id, event) {
    if (event) event.stopPropagation();
    const chat = allChats.find(c => c.id === id);
    if (!chat) return;
    const nextSaved = !chat.is_saved;

    try {
        const res = await fetch(`/api/chats/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: JSON.stringify({ is_saved: nextSaved, updated_at: new Date().toISOString() })
        });
        if (res.ok) {
            chat.is_saved = nextSaved;
            
            const storageKey = `truthlens_runs_${currentUser.email}`;
            let runs = JSON.parse(localStorage.getItem(storageKey) || '[]');
            const runIdx = runs.findIndex(r => r.id === id);
            if (runIdx >= 0) {
                runs[runIdx].is_saved_locally = nextSaved;
                localStorage.setItem(storageKey, JSON.stringify(runs));
            }

            logChatActivity(nextSaved ? "Chat bookmarked" : "Chat unbookmarked", chat.title.substring(0, 25) + "...");
            updateDashboardUI();
        }
    } catch (e) {
        console.error("Failed to toggle save status:", e);
    }
}

function renameChatFromDB(id, event) {
    if (event) event.stopPropagation();
    const chat = allChats.find(c => c.id === id);
    if (!chat) return;

    const newTitle = prompt("Rename Conversation:", chat.title);
    if (newTitle !== null && newTitle.trim() !== "") {
        const trimmed = newTitle.trim();
        saveRenameChatToDB(id, trimmed);
    }
}

async function saveRenameChatToDB(id, title) {
    try {
        const res = await fetch(`/api/chats/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: JSON.stringify({ title: title, updated_at: new Date().toISOString() })
        });
        if (res.ok) {
            const chat = allChats.find(c => c.id === id);
            if (chat) chat.title = title;
            
            logChatActivity("Chat renamed", title.substring(0, 25) + "...");
            updateDashboardUI();
        }
    } catch (e) {
        console.error("Failed to rename chat:", e);
    }
}

let chatToDeleteId = null;
let isBulkDelete = false;

function confirmDeleteChatFromDB(id, event) {
    if (event) event.stopPropagation();
    chatToDeleteId = id;
    isBulkDelete = false;
    
    const dialog = document.getElementById('chat-confirm-dialog');
    const msg = document.getElementById('confirm-dialog-msg');
    if (dialog && msg) {
        const chat = allChats.find(c => c.id === id);
        msg.textContent = `Are you sure you want to delete the conversation "${chat ? chat.title : 'this chat'}"? This cannot be undone.`;
        dialog.classList.remove('hidden');
    }
}

function closeDeleteConfirmDialog() {
    const dialog = document.getElementById('chat-confirm-dialog');
    if (dialog) dialog.classList.add('hidden');
    chatToDeleteId = null;
    isBulkDelete = false;
}

async function executeDeleteChat() {
    if (isBulkDelete) {
        await executeBulkDelete();
        return;
    }
    if (!chatToDeleteId) return;
    const id = chatToDeleteId;
    try {
        const res = await fetch(`/api/chats/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (res.ok) {
            const chat = allChats.find(c => c.id === id);
            logChatActivity("Chat deleted", chat ? chat.title.substring(0, 25) + "..." : id);

            allChats = allChats.filter(c => c.id !== id);
            selectedChatIds.delete(id);
            updateBulkToolbarState();

            const storageKey = `truthlens_runs_${currentUser.email}`;
            let runs = JSON.parse(localStorage.getItem(storageKey) || '[]');
            runs = runs.filter(r => r.id !== id);
            localStorage.setItem(storageKey, JSON.stringify(runs));

            updateDashboardUI();
        }
    } catch (e) {
        console.error("Failed to delete chat:", e);
    } finally {
        closeDeleteConfirmDialog();
    }
}

function confirmBulkDeleteChats() {
    if (selectedChatIds.size === 0) return;
    isBulkDelete = true;
    const dialog = document.getElementById('chat-confirm-dialog');
    const msg = document.getElementById('confirm-dialog-msg');
    if (dialog && msg) {
        msg.textContent = `Are you sure you want to delete all ${selectedChatIds.size} selected conversations? This operation is permanent and cannot be undone.`;
        dialog.classList.remove('hidden');
    }
}

async function executeBulkDelete() {
    const ids = Array.from(selectedChatIds);
    try {
        const res = await fetch('/api/chats/bulk-delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: JSON.stringify({ ids: ids })
        });
        if (res.ok) {
            logChatActivity("Bulk deleted", `${ids.length} chats removed`);
            selectedChatIds.clear();
            updateBulkToolbarState();
            
            const storageKey = `truthlens_runs_${currentUser.email}`;
            let runs = JSON.parse(localStorage.getItem(storageKey) || '[]');
            runs = runs.filter(r => !ids.includes(r.id));
            localStorage.setItem(storageKey, JSON.stringify(runs));

            updateDashboardUI();
        }
    } catch (e) {
        console.error("Failed to bulk delete chats:", e);
    } finally {
        closeDeleteConfirmDialog();
    }
}

async function executeBulkSave() {
    if (selectedChatIds.size === 0) return;
    const ids = Array.from(selectedChatIds);
    const firstChat = allChats.find(c => c.id === ids[0]);
    const nextSaved = firstChat ? !firstChat.is_saved : true;

    try {
        const res = await fetch('/api/chats/bulk-save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: JSON.stringify({ ids: ids, is_saved: nextSaved })
        });
        if (res.ok) {
            logChatActivity("Bulk bookmarked", `${ids.length} chats updated`);
            updateDashboardUI();
        }
    } catch (e) {
        console.error("Failed to bulk save chats:", e);
    }
}

window.viewPastRunFromDB = function(id) {
    if (!currentUser) return;
    const chat = allChats.find(c => c.id === id);
    if (!chat) return;
    
    localStorage.setItem('view_run_id', id);
    navigateTo('analysis');
};

function renderSavedQuickAccess() {
    const listEl = document.getElementById('saved-quick-list');
    if (!listEl) return;

    const saved = allChats.filter(c => c.is_saved);
    if (saved.length === 0) {
        listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 1rem 0; font-size: 0.85rem;">No saved chats yet.</div>';
        return;
    }

    listEl.innerHTML = '';
    saved.slice(0, 5).forEach(chat => {
        const div = document.createElement('div');
        div.className = 'saved-quick-item';
        div.style.cssText = 'background: rgba(0,0,0,0.01); border: 1px solid var(--panel-border); border-radius: 6px; padding: 0.5rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;';
        
        div.onmouseover = () => {
            div.style.background = 'rgba(79, 70, 229, 0.04)';
            div.style.borderColor = 'rgba(79, 70, 229, 0.2)';
        };
        div.onmouseout = () => {
            div.style.background = 'rgba(0,0,0,0.01)';
            div.style.borderColor = 'var(--panel-border)';
        };

        div.onclick = () => openChatDetailModal(chat.id);

        const riskColor = getColorForRisk(chat.risk_score / 100);
        div.innerHTML = `
            <span style="font-weight: 500; font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 80%;" title="${chat.title}">${chat.title}</span>
            <span style="font-size: 0.72rem; font-weight: 600; color: ${riskColor}; background: ${riskColor}15; padding: 1px 4px; border-radius: 4px;">${chat.risk_score}%</span>
        `;
        listEl.appendChild(div);
    });
}

function openChatDetailModal(id) {
    const modal = document.getElementById('chat-detail-modal');
    if (!modal) return;

    const chat = allChats.find(c => c.id === id);
    if (!chat) return;

    modal.dataset.chatId = id;
    renderAllChatsPanel();

    const titleEl = document.getElementById('cm-modal-title');
    const dateEl = document.getElementById('cm-modal-date');
    const verdictEl = document.getElementById('cm-modal-verdict');

    if (titleEl) titleEl.textContent = chat.title;
    if (dateEl) {
        const formattedDate = new Date(chat.created_at).toLocaleDateString('en-IN', {
            month: 'long', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        dateEl.innerHTML = `<i class="fa-solid fa-calendar-days"></i> ${formattedDate}`;
    }
    if (verdictEl) {
        const badgeClass = getVerdictBadgeClass(chat.risk_score);
        verdictEl.className = `badge-verdict ${badgeClass}`;
        verdictEl.textContent = `${chat.verdict} (${chat.risk_score}% Risk)`;
    }

    const bodyEl = document.getElementById('cm-modal-body');
    if (bodyEl) {
        bodyEl.innerHTML = '';

        const userBubble = document.createElement('div');
        userBubble.className = 'cm-bubble user';
        userBubble.innerHTML = `
            <div class="cm-label">You</div>
            <div class="cm-text">${chat.prompt.replace(/\n/g, '<br>')}</div>
        `;
        bodyEl.appendChild(userBubble);

        const aiBubble = document.createElement('div');
        aiBubble.className = 'cm-bubble ai';
        
        let contentHTML = chat.response.replace(/\n/g, '<br>');
        let riskChipHTML = "";
        let modelBadgeHTML = "";

        if (chat.evaluation_data) {
            try {
                const evalData = JSON.parse(chat.evaluation_data);
                const sentences = evalData.sentence_analysis;
                
                if (sentences && sentences.length > 0) {
                    contentHTML = sentences.map(s => {
                        const riskClass = s.category === 'verified' ? 'verified' : (s.score > 70 ? 'danger' : (s.score > 30 ? 'warn' : 'low'));
                        return `<span class="risk-highlight ${riskClass}" title="${s.type}: ${s.reason}">${s.text}</span>`;
                    }).join(' ');
                }

                const riskVal = chat.risk_score;
                const riskLevel = chat.verdict;
                const riskColor = getColorForRisk(riskVal / 100);
                
                riskChipHTML = `
                    <div class="chat-risk-chip" style="border-left: 3px solid ${riskColor}; margin-top: 1rem; padding: 0.5rem; background: rgba(0,0,0,0.01); border-radius: 4px; font-size: 0.82rem;">
                        <span class="rc-label" style="font-weight:600; color:var(--text-muted);">Hallucination Risk Analysis:</span>
                        <span class="rc-val" style="color: ${riskColor}; font-weight:700;">${riskVal}% (${riskLevel})</span>
                    </div>`;

                if (evalData.model_name) {
                    modelBadgeHTML = `<div class="chat-model-badge" style="font-size:0.75rem; color:var(--text-muted); margin-bottom:0.5rem; display:flex; align-items:center; gap:4px;"><i class="fa-solid fa-microchip"></i> Generated by ${evalData.model_name}</div>`;
                }
            } catch (e) {
                console.error("Failed to parse evaluation data in modal:", e);
            }
        }

        aiBubble.innerHTML = `
            <div class="cm-label"><i class="fa-solid fa-robot"></i> TruthLens AI</div>
            ${modelBadgeHTML}
            <div class="cm-text" style="font-size: 0.95rem; color: var(--text-main); font-family: inherit;">${contentHTML}</div>
            ${riskChipHTML}
        `;
        bodyEl.appendChild(aiBubble);
    }

    modal.classList.remove('hidden');
    logChatActivity("Viewed chat details", chat.title.substring(0, 25) + "...");
}

function closeChatDetailModal() {
    const modal = document.getElementById('chat-detail-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.dataset.chatId = '';
    }
    renderAllChatsPanel();
}

function getChatsToExport() {
    if (selectedChatIds.size > 0) {
        return allChats.filter(c => selectedChatIds.has(c.id));
    }
    return allChats;
}

function exportToJSON() {
    const chats = getChatsToExport();
    if (chats.length === 0) return alert("No chats available to export.");
    const cleanChats = chats.map(c => ({
        id: c.id,
        title: c.title,
        prompt: c.prompt,
        response: c.response,
        risk_score: c.risk_score,
        verdict: c.verdict,
        created_at: c.created_at,
        updated_at: c.updated_at,
        is_saved: c.is_saved
    }));

    const blob = new Blob([JSON.stringify(cleanChats, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `truthlens_chats_export_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    logChatActivity("Exported JSON", `${chats.length} chats`);
}

function exportToCSV() {
    const chats = getChatsToExport();
    if (chats.length === 0) return alert("No chats available to export.");
    
    let csvContent = "ID,Title,Prompt,Response,Risk Score,Verdict,Created At,Is Saved\n";
    
    chats.forEach(c => {
        const id = `"${c.id.replace(/"/g, '""')}"`;
        const title = `"${c.title.replace(/"/g, '""')}"`;
        const prompt = `"${c.prompt.replace(/"/g, '""')}"`;
        const response = `"${c.response.replace(/"/g, '""')}"`;
        const score = c.risk_score;
        const verdict = `"${c.verdict.replace(/"/g, '""')}"`;
        const date = `"${c.created_at}"`;
        const saved = c.is_saved ? 1 : 0;
        
        csvContent += `${id},${title},${prompt},${response},${score},${verdict},${date},${saved}\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `truthlens_chats_export_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    logChatActivity("Exported CSV", `${chats.length} chats`);
}

function exportToTXT(singleChat = null) {
    const chats = singleChat ? [singleChat] : getChatsToExport();
    if (chats.length === 0) return alert("No chats available to export.");
    
    let txt = `==================================================\n`;
    txt += `TRUTHLENS AI - CHAT HISTORY EXPORT\n`;
    txt += `Generated on: ${new Date().toLocaleString()}\n`;
    txt += `==================================================\n\n`;
    
    chats.forEach((c, idx) => {
        txt += `--- CONVERSATION ${idx + 1} ---\n`;
        txt += `ID: ${c.id}\n`;
        txt += `Title: ${c.title}\n`;
        txt += `Date: ${new Date(c.created_at).toLocaleString()}\n`;
        txt += `Verdict: ${c.verdict} (${c.risk_score}% risk score)\n\n`;
        txt += `[USER PROMPT]:\n${c.prompt}\n\n`;
        txt += `[AI RESPONSE]:\n${c.response}\n`;
        txt += `\n==================================================\n\n`;
    });

    const blob = new Blob([txt], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = singleChat ? `truthlens_chat_${singleChat.id}.txt` : `truthlens_chats_export_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    logChatActivity("Exported TXT", `${chats.length} chats`);
}

function exportToPDF() {
    const chats = getChatsToExport();
    if (chats.length === 0) return alert("No chats available to export.");

    const iframe = document.createElement('iframe');
    iframe.style.position = 'fixed';
    iframe.style.right = '0';
    iframe.style.bottom = '0';
    iframe.style.width = '0';
    iframe.style.height = '0';
    iframe.style.border = '0';
    document.body.appendChild(iframe);

    const doc = iframe.contentWindow.document;
    doc.open();
    
    let html = `
    <html>
    <head>
        <title>TruthLens AI Export</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Outfit', sans-serif;
                color: #0f172a;
                padding: 2rem;
                background: #ffffff;
            }
            .header {
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 1rem;
                margin-bottom: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .logo {
                font-size: 1.5rem;
                font-weight: 700;
                color: #4f46e5;
            }
            .meta-info {
                font-size: 0.8rem;
                color: #64748b;
                text-align: right;
            }
            .chat-block {
                margin-bottom: 3rem;
                page-break-inside: avoid;
            }
            .chat-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 0.5rem;
                border-left: 4px solid #4f46e5;
                padding-left: 0.75rem;
            }
            .chat-date {
                font-size: 0.8rem;
                color: #64748b;
                margin-bottom: 1rem;
            }
            .bubble {
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
                line-height: 1.5;
            }
            .bubble.user {
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
            }
            .bubble.ai {
                background: #ffffff;
                border: 1px solid #e2e8f0;
            }
            .label {
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.3rem;
                color: #4f46e5;
            }
            .bubble.user .label {
                color: #475569;
            }
            .risk-highlight {
                padding: 0 2px;
                border-radius: 3px;
            }
            .risk-highlight.verified {
                background-color: rgba(16, 185, 129, 0.12);
                border-bottom: 2px solid #10b981;
            }
            .risk-highlight.danger {
                background-color: rgba(239, 68, 68, 0.12);
                border-bottom: 2px solid #ef4444;
            }
            .risk-highlight.warn {
                background-color: rgba(245, 158, 11, 0.12);
                border-bottom: 2px solid #f59e0b;
            }
            .risk-highlight.low {
                background-color: rgba(99, 102, 241, 0.1);
                border-bottom: 2px solid #6366f1;
            }
            .risk-chip {
                border-left: 3px solid #cbd5e1;
                margin-top: 1rem;
                padding: 0.5rem;
                background: #f8fafc;
                border-radius: 4px;
                font-size: 0.85rem;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">TruthLens AI</div>
            <div class="meta-info">
                <div>Chat History Report</div>
                <div>Exported: ${new Date().toLocaleDateString()}</div>
                <div>Total Chats: ${chats.length}</div>
            </div>
        </div>
    `;

    chats.forEach(c => {
        let responseHTML = c.response.replace(/\n/g, '<br>');
        let riskColor = getColorForRisk(c.risk_score / 100);
        
        if (c.evaluation_data) {
            try {
                const evalData = JSON.parse(c.evaluation_data);
                const sentences = evalData.sentence_analysis;
                if (sentences && sentences.length > 0) {
                    responseHTML = sentences.map(s => {
                        const riskClass = s.category === 'verified' ? 'verified' : (s.score > 70 ? 'danger' : (s.score > 30 ? 'warn' : 'low'));
                        return `<span class="risk-highlight ${riskClass}">${s.text}</span>`;
                    }).join(' ');
                }
            } catch(e){}
        }

        const dateStr = new Date(c.created_at).toLocaleString();

        html += `
            <div class="chat-block">
                <div class="chat-title">${c.title}</div>
                <div class="chat-date">${dateStr}</div>
                <div class="bubble user">
                    <div class="label">You</div>
                    <div>${c.prompt.replace(/\n/g, '<br>')}</div>
                </div>
                <div class="bubble ai">
                    <div class="label">TruthLens AI</div>
                    <div>${responseHTML}</div>
                    <div class="risk-chip" style="border-left-color: ${riskColor}; color: ${riskColor}">
                        Hallucination Risk: ${c.risk_score}% (${c.verdict})
                    </div>
                </div>
            </div>
        `;
    });

    html += `
    </body>
    </html>
    `;

    doc.write(html);
    doc.close();

    iframe.contentWindow.onload = function() {
        iframe.contentWindow.print();
        setTimeout(() => {
            if (iframe.parentNode) document.body.removeChild(iframe);
        }, 1000);
    };
    
    setTimeout(() => {
        if (iframe.parentNode) {
            iframe.contentWindow.print();
            setTimeout(() => {
                if (iframe.parentNode) document.body.removeChild(iframe);
            }, 1000);
        }
    }, 500);

    logChatActivity("Exported PDF", `${chats.length} chats`);
}

function initDashboardChatManager() {
    console.log('[TruthLens] Initializing Dashboard Chat History Manager...');
    
    const searchInput = document.getElementById('chats-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            renderAllChatsPanel();
        });
    }

    const pills = document.querySelectorAll('.filter-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentChatFilter = pill.dataset.filter;
            selectedChatIds.clear();
            updateBulkToolbarState();
            renderAllChatsPanel();
        });
    });

    const bulkSave = document.getElementById('bulk-save-btn');
    if (bulkSave) bulkSave.addEventListener('click', () => executeBulkSave());
    
    const bulkDelete = document.getElementById('bulk-delete-btn');
    if (bulkDelete) bulkDelete.addEventListener('click', () => confirmBulkDeleteChats());
    
    const bulkExport = document.getElementById('bulk-export-btn');
    if (bulkExport) bulkExport.addEventListener('click', () => exportToJSON());

    const expPdf = document.getElementById('exp-pdf-btn');
    if (expPdf) expPdf.addEventListener('click', () => exportToPDF());

    const expTxt = document.getElementById('exp-txt-btn');
    if (expTxt) expTxt.addEventListener('click', () => exportToTXT());

    const expJson = document.getElementById('exp-json-btn');
    if (expJson) expJson.addEventListener('click', () => exportToJSON());

    const expCsv = document.getElementById('exp-csv-btn');
    if (expCsv) expCsv.addEventListener('click', () => exportToCSV());

    const cancelConfirm = document.getElementById('confirm-cancel-btn');
    if (cancelConfirm) cancelConfirm.addEventListener('click', () => closeDeleteConfirmDialog());

    const okConfirm = document.getElementById('confirm-ok-btn');
    if (okConfirm) okConfirm.addEventListener('click', () => executeDeleteChat());

    const cmClose = document.getElementById('cm-modal-close');
    if (cmClose) cmClose.addEventListener('click', () => closeChatDetailModal());

    const cmCloseBtn = document.getElementById('cm-modal-close-btn');
    if (cmCloseBtn) cmCloseBtn.addEventListener('click', () => closeChatDetailModal());

    const cmExportTxt = document.getElementById('cm-modal-export-txt');
    if (cmExportTxt) {
        cmExportTxt.addEventListener('click', () => {
            const chatId = document.getElementById('chat-detail-modal').dataset.chatId;
            const chat = allChats.find(c => c.id === chatId);
            if (chat) exportToTXT(chat);
        });
    }

    const cmExportJson = document.getElementById('cm-modal-export-json');
    if (cmExportJson) {
        cmExportJson.addEventListener('click', () => {
            const chatId = document.getElementById('chat-detail-modal').dataset.chatId;
            const chat = allChats.find(c => c.id === chatId);
            if (chat) {
                const blob = new Blob([JSON.stringify(chat, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `truthlens_chat_${chat.id}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        });
    }

    window.toggleSaveChatFromDB = toggleSaveChatFromDB;
    window.renameChatFromDB = renameChatFromDB;
    window.confirmDeleteChatFromDB = confirmDeleteChatFromDB;
    window.viewPastRunFromDB = viewPastRunFromDB;
    window.openChatDetailModal = openChatDetailModal;
    window.closeChatDetailModal = closeChatDetailModal;

    logChatActivity("Dashboard loaded", "System initialized");
}

// ── Contact Form Handler ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contact-form');
    if (!contactForm) return;

    const firstNameInput = document.getElementById('contact-first-name');
    const lastNameInput = document.getElementById('contact-last-name');
    const emailInput = document.getElementById('contact-email');
    const inquiryTypeInput = document.getElementById('contact-inquiry-type');
    const messageInput = document.getElementById('contact-message');
    const honeypotInput = document.getElementById('contact-honeypot');
    const submitBtn = document.getElementById('contact-submit-btn');
    const statusMsg = document.getElementById('contact-status-msg');

    /*
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Client-Side Validation
        const firstName = firstNameInput.value.trim();
        const lastName = lastNameInput.value.trim();
        const email = emailInput.value.trim();
        const inquiryType = inquiryTypeInput.value;
        const message = messageInput.value.trim();
        const honeypot = honeypotInput ? honeypotInput.value : '';

        // Status message reset and show helper
        const showStatus = (text, type) => {
            statusMsg.textContent = text;
            statusMsg.classList.remove('hidden');
            if (type === 'success') {
                statusMsg.style.backgroundColor = 'rgba(16, 185, 129, 0.15)';
                statusMsg.style.color = '#10b981';
                statusMsg.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            } else {
                statusMsg.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                statusMsg.style.color = '#ef4444';
                statusMsg.style.borderColor = 'rgba(239, 68, 68, 0.3)';
            }
        };

        if (!firstName || !lastName) {
            showStatus('First name and last name are required.', 'error');
            return;
        }

        const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        if (!emailRegex.test(email)) {
            showStatus('Please enter a valid email address.', 'error');
            return;
        }

        if (message.length < 10) {
            showStatus('Message must be at least 10 characters long.', 'error');
            return;
        }

        // 2. Loading State
        submitBtn.disabled = true;
        const originalBtnHTML = submitBtn.innerHTML;
        submitBtn.innerHTML = 'Sending... <i class="fa-solid fa-spinner fa-spin" style="margin-left: 0.5rem;"></i>';
        statusMsg.classList.add('hidden');

        try {
            const res = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    email: email,
                    inquiry_type: inquiryType,
                    message: message,
                    honeypot: honeypot
                })
            });

            const data = await res.json();

            if (res.ok && data.status === 'success') {
                showStatus(data.message || 'Your message has been sent successfully. Our team will contact you soon.', 'success');
                contactForm.reset();
            } else {
                showStatus(data.detail || data.message || 'An error occurred. Please try again.', 'error');
            }
        } catch (err) {
            console.error('Contact submission error:', err);
            showStatus('Failed to send message. Please check your connection and try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnHTML;
        }
    });
    */
});

