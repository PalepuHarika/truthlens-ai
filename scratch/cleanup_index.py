import os

path = "static/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "<!-- ═══════════ DASHBOARD VIEW ═══════════ -->"
end_marker = "<!-- Interactive Hover Tooltip -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + content[end_idx:]
    
    # Also fix navbar links in index.html to point to absolute routes (Home active)
    old_nav = """        <div class="nav-links">
            <a href="#" class="nav-link" data-view="home">Home</a>
            <a href="#" class="nav-link" data-view="dashboard">Dashboard</a>
            <a href="#" class="nav-link" data-view="chat">Chat</a>
            <a href="#" class="nav-link" data-view="about">About</a>
            <a href="#" class="nav-link" data-view="resources">Resources</a>
            <a href="#" class="nav-link" data-view="contact">Contact</a>
            <a href="#" class="nav-link" data-view="settings">Settings</a>
            <a href="#" class="nav-link" data-view="login" id="nav-login-btn">Login</a>
        </div>"""
        
    new_nav = """        <div class="nav-links">
            <a href="/" class="nav-link active" data-view="home">Home</a>
            <a href="/dashboard" class="nav-link" data-view="dashboard">Dashboard</a>
            <a href="/chat" class="nav-link" data-view="chat">Chat</a>
            <a href="/analysis" class="nav-link" data-view="analysis">Analysis</a>
            <a href="/features" class="nav-link" data-view="features">Features</a>
            <a href="/contact" class="nav-link" data-view="contact">Contact</a>
            <a href="/settings" class="nav-link" data-view="settings">Settings</a>
            <a href="/login" class="nav-link" data-view="login" id="nav-login-btn">Login</a>
        </div>"""
        
    if old_nav in new_content:
        new_content = new_content.replace(old_nav, new_nav)
        print("Updated navbar links in index.html.")
    else:
        # Check with CRLF line endings
        old_nav_crlf = old_nav.replace('\n', '\r\n')
        new_nav_crlf = new_nav.replace('\n', '\r\n')
        if old_nav_crlf in new_content:
            new_content = new_content.replace(old_nav_crlf, new_nav_crlf)
            print("Updated navbar links in index.html (CRLF).")
        else:
            print("Navbar links block not found in index.html.")
            
    # Also clean up duplicate tooltip in index.html if present
    tooltip_block = """    <!-- Interactive Hover Tooltip -->
    <div id="truthlens-tooltip" class="tl-tooltip hidden">
        <div class="tl-tooltip-header">
            <span id="tt-type">Claim Type</span>
            <span id="tt-status" class="tt-status-pill">Status</span>
        </div>
        <div class="tl-tooltip-meta">
            <i class="fa-solid fa-bullseye"></i> Confidence: <span id="tt-conf">0%</span>
        </div>
        <div class="tl-tooltip-reason" id="tt-reason">
            Reason details will appear here.
        </div>
    </div>"""
    
    # Check both LF and CRLF for tooltip
    if new_content.count(tooltip_block) > 1:
        new_content = new_content.replace(tooltip_block, "", 1)
        print("Removed duplicate tooltip block.")
    else:
        tooltip_block_crlf = tooltip_block.replace('\n', '\r\n')
        if new_content.count(tooltip_block_crlf) > 1:
            new_content = new_content.replace(tooltip_block_crlf, "", 1)
            print("Removed duplicate tooltip block (CRLF).")

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Cleaned index.html successfully!")
else:
    print(f"Markers not found! start_idx={start_idx}, end_idx={end_idx}")
