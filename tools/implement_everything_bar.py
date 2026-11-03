import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_py = os.path.join(root, 'simulator', 'app.py')

with open(app_py, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. ADD CSS FOR EVERYTHING TRAY
tray_css = """
    /* ZEROOS EVERYTHING BAR - OMNIBAR ACTION TRAY */
    .command-center-container {
      position: relative;
    }
    .everything-tray {
      position: absolute;
      bottom: calc(100% + 6px);
      left: 0;
      right: 0;
      background: #141b24;
      border: 1px solid #283548;
      border-radius: 16px;
      padding: 8px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.85);
      z-index: 120;
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-height: 280px;
      overflow-y: auto;
      scrollbar-width: none;
      backdrop-filter: blur(24px);
    }
    .everything-tray::-webkit-scrollbar { display: none; }
    
    .tray-card {
      background: #1a222d;
      border: 1px solid #253142;
      border-radius: 12px;
      padding: 8px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      cursor: pointer;
      transition: background 0.12s ease;
    }
    .tray-card:hover {
      background: #232e3d;
      border-color: #3b82f6;
    }
    .tray-card-left {
      display: flex;
      align-items: center;
      gap: 10px;
      overflow: hidden;
    }
    .tray-icon {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      flex-shrink: 0;
    }
    .tray-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #00a884;
      color: #000;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.95rem;
      flex-shrink: 0;
    }
    .tray-title {
      font-size: 0.82rem;
      font-weight: 600;
      color: #f1f5f9;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .tray-sub {
      font-size: 0.68rem;
      color: #94a3b8;
      white-space: nowrap;
    }
    .tray-actions {
      display: flex;
      gap: 6px;
      flex-shrink: 0;
    }
    .tray-btn {
      background: #253142;
      border: 1px solid #37475d;
      color: #e2e8f0;
      border-radius: 8px;
      padding: 5px 10px;
      font-size: 0.7rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: background 0.1s;
    }
    .tray-btn:hover { background: #37475d; }
    .tray-btn.call { background: #15803d; border-color: #16a34a; color: #fff; }
    .tray-btn.call:hover { background: #16a34a; }
    .tray-btn.sms { background: #2563eb; border-color: #3b82f6; color: #fff; }
    .tray-btn.sms:hover { background: #3b82f6; }
    .tray-btn.zerochat { background: #005c4b; border-color: #00a884; color: #fff; }
    .tray-btn.zerochat:hover { background: #00a884; color: #000; }
    .tray-btn.primary { background: #00a884; border-color: #00a884; color: #000; }
"""

if '/* ZEROOS EVERYTHING BAR' not in text:
    text = text.replace('.search-command-bar {', tray_css + '\n    .search-command-bar {')

# 2. UPDATE SEARCH BAR HTML TO INCLUDE oninput AND TRAY CONTAINER
old_search_bar = re.search(r'<div class="search-command-bar">[\s\S]*?</div>\s*</div>\s*<!-- Standard Clean App Grid', text)
if not old_search_bar:
    old_search_bar = re.search(r'<div class="search-command-bar">[\s\S]*?</div>\s*</div>', text)

new_search_bar = """<div class="search-command-bar">
                <span class="command-symbol">⌘</span>
                <input type="text" id="androidSearchInput" class="search-input" placeholder="Search, calculate, call, message, or command..." oninput="onEverythingBarInput(this.value)" onkeydown="if(event.key==='Enter') executeSearchCommand()" />
                <button class="btn-execute-cmd" onclick="executeSearchCommand()" title="Execute Command">↵</button>
              </div>

              <!-- Floating Everything Bar Action & Suggestion Tray -->
              <div id="everythingResultsTray" class="everything-tray" style="display:none;"></div>
            </div>
            <!-- Standard Clean App Grid"""

if old_search_bar:
    text = text[:old_search_bar.start()] + new_search_bar + text[old_search_bar.end():]

# 3. ADD JAVASCRIPT EVERYTHING BAR ENGINE
everything_js = """
    // ==============================================================
    // ZEROOS EVERYTHING BAR (UNIVERSAL OMNIBAR ENGINE)
    // ==============================================================
    const CONTACTS_DIRECTORY = [
      { id: "c1", name: "Alex Rivera", number: "+1 555-0192", avatar: "A", handle: "@alex.0" },
      { id: "c2", name: "Dr. Maya Chen", number: "+44 7700-900821", avatar: "M", handle: "@maya.0" },
      { id: "c3", name: "David Kumar", number: "+91 98765-43210", avatar: "D", handle: "@david.0" },
      { id: "c4", name: "Sarah Jenkins", number: "+1 555-0144", avatar: "S", handle: "@sarah.0" },
      { id: "c5", name: "Mom", number: "+1 555-0100", avatar: "M", handle: "@mom.0" },
      { id: "c6", name: "Office Desk", number: "+1 555-0800", avatar: "O", handle: "@office.0" }
    ];

    const APPS_DIRECTORY = [
      { key: "phone", name: "Phone", sub: "Dialer & Call History", icon: "📞" },
      { key: "messages", name: "Messages", sub: "Standard Carrier SMS", icon: "💬" },
      { key: "zerochat", name: "ZeroChat", sub: "Encrypted P2P Messenger", icon: "🔒" },
      { key: "maps", name: "ZeroMaps", sub: "100% Offline Vector Navigation", icon: "🗺️" },
      { key: "camera", name: "Camera", sub: "Private Viewfinder", icon: "📷" },
      { key: "settings", name: "Settings", sub: "ZeroOS System Controls", icon: "⚙️" },
      { key: "spotify", name: "Spotify", sub: "Music Streaming", icon: "🎵" },
      { key: "monzo", name: "Monzo Bank", sub: "Cards & NFC Tap-to-Pay", icon: "💳" },
      { key: "chrome", name: "Chrome", sub: "Web Browser", icon: "🌐" },
      { key: "youtube", name: "YouTube", sub: "Video Player", icon: "▶️" },
      { key: "instagram", name: "Instagram", sub: "Social Media", icon: "📸" },
      { key: "tiktok", name: "TikTok", sub: "Short Videos", icon: "🎵" }
    ];

    function onEverythingBarInput(raw) {
      const q = (raw || '').trim();
      const tray = document.getElementById('everythingResultsTray');
      if (!tray) return;

      if (!q) {
        tray.style.display = 'none';
        tray.innerHTML = '';
        return;
      }

      let cardsHtml = '';
      const lower = q.toLowerCase();

      // 1. MATH CALCULATION ENGINE (e.g. 245 * 18, 15% of 850, 120 / 4 + 50)
      const mathClean = q.replace(/x/gi, '*').replace(/÷/g, '/');
      const isPercentOf = lower.match(/^([0-9.]+)\s*%\s*(?:of)?\s*([0-9.]+)$/);
      let mathResult = null;

      if (isPercentOf) {
        const pct = parseFloat(isPercentOf[1]);
        const base = parseFloat(isPercentOf[2]);
        if (!isNaN(pct) && !isNaN(base)) {
          mathResult = (pct / 100) * base;
        }
      } else if (/^[0-9+\-*/().\s^%]+$/.test(mathClean) && /[+\-*/%]/.test(mathClean)) {
        try {
          // Safe arithmetic evaluation
          const res = Function('"use strict"; return (' + mathClean + ')')();
          if (typeof res === 'number' && !isNaN(res) && isFinite(res)) {
            mathResult = Math.round(res * 10000) / 10000;
          }
        } catch (e) {}
      }

      if (mathResult !== null) {
        const formattedRes = Number(mathResult).toLocaleString();
        cardsHtml += `
          <div class="tray-card">
            <div class="tray-card-left" onclick="copyEverythingResult('${formattedRes}')">
              <span class="tray-icon" style="background:#2563eb; color:#fff;">🧮</span>
              <div>
                <div class="tray-title" style="color:#38bdf8; font-size:1.05rem; font-weight:700;">= ${formattedRes}</div>
                <div class="tray-sub">${q} · Tap to copy result</div>
              </div>
            </div>
            <div class="tray-actions">
              <button class="tray-btn" onclick="copyEverythingResult('${formattedRes}')">📋 Copy</button>
              <button class="tray-btn primary" onclick="showToast('🧮 Calculator opened: ${formattedRes}')">Open Calc</button>
            </div>
          </div>
        `;
      }

      // 2. PHONE NUMBER DETECTION (e.g. +1 555-0192 or 9876543210 or digits 5+)
      const cleanDigits = q.replace(/[^0-9+]/g, '');
      const isPhoneNumber = cleanDigits.length >= 5 && (/^[+]?[0-9\s\-()]{5,18}$/.test(q) || cleanDigits.length >= 7);
      if (isPhoneNumber && !mathResult) {
        cardsHtml += `
          <div class="tray-card">
            <div class="tray-card-left">
              <span class="tray-icon" style="background:#15803d; color:#fff;">📞</span>
              <div>
                <div class="tray-title">${q}</div>
                <div class="tray-sub">Unsaved Number · Tap to call or add contact</div>
              </div>
            </div>
            <div class="tray-actions">
              <button class="tray-btn call" onclick="makeEverythingCall('${q}', '${q}')">📞 Call</button>
              <button class="tray-btn sms" onclick="openEverythingMessage('${q}', '${q}')">💬 Text</button>
              <button class="tray-btn" onclick="saveEverythingContact('${q}')">👤 Add</button>
            </div>
          </div>
        `;
      }

      // 3. CONTACT SEARCH & ACTIONS (e.g. "Alex", "call Sarah", "message Mom")
      let contactQuery = lower.replace(/^(call|dial|text|message|msg|chat)\s+/i, '').trim();
      const matchedContacts = CONTACTS_DIRECTORY.filter(c => 
        c.name.toLowerCase().includes(contactQuery) || 
        c.number.includes(contactQuery) ||
        c.handle.toLowerCase().includes(contactQuery)
      );

      matchedContacts.slice(0, 3).forEach(c => {
        cardsHtml += `
          <div class="tray-card">
            <div class="tray-card-left" onclick="makeEverythingCall('${c.name}', '${c.number}')">
              <div class="tray-avatar">${c.avatar}</div>
              <div>
                <div class="tray-title">${c.name}</div>
                <div class="tray-sub">${c.number} · ${c.handle}</div>
              </div>
            </div>
            <div class="tray-actions">
              <button class="tray-btn call" onclick="makeEverythingCall('${c.name}', '${c.number}')">📞 Call</button>
              <button class="tray-btn sms" onclick="openEverythingMessage('${c.name}', '${c.number}')">💬 Text</button>
              <button class="tray-btn zerochat" onclick="openEverythingZeroChat('${c.name}')">🔒 Chat</button>
            </div>
          </div>
        `;
      });

      // 4. APP MATCHING & LAUNCH (e.g. "cam", "spotify", "maps")
      let appQuery = lower.replace(/^(open|launch)\s+/i, '').trim();
      const matchedApps = APPS_DIRECTORY.filter(a => 
        a.name.toLowerCase().includes(appQuery) || 
        a.key.includes(appQuery)
      );

      matchedApps.slice(0, 2).forEach(a => {
        cardsHtml += `
          <div class="tray-card" onclick="launchForegroundApp('${a.key}')">
            <div class="tray-card-left">
              <span class="tray-icon" style="background:#1f2937; border:1px solid #374151;">${a.icon}</span>
              <div>
                <div class="tray-title">${a.name}</div>
                <div class="tray-sub">${a.sub}</div>
              </div>
            </div>
            <div class="tray-actions">
              <button class="tray-btn primary" onclick="launchForegroundApp('${a.key}')">Open App</button>
            </div>
          </div>
        `;
      });

      // 5. UNIT & CURRENCY CONVERSIONS
      const unitConversions = [
        { regex: /([0-9.]+)\s*(km|kilometers?)\s*(?:to|in)\s*(miles?|mi)/i, fn: (m) => `${(parseFloat(m[1]) * 0.621371).toFixed(2)} miles` },
        { regex: /([0-9.]+)\s*(miles?|mi)\s*(?:to|in)\s*(km|kilometers?)/i, fn: (m) => `${(parseFloat(m[1]) * 1.60934).toFixed(2)} km` },
        { regex: /([0-9.]+)\s*(kg|kilos?)\s*(?:to|in)\s*(lbs?|pounds?)/i, fn: (m) => `${(parseFloat(m[1]) * 2.20462).toFixed(2)} lbs` },
        { regex: /([0-9.]+)\s*(lbs?|pounds?)\s*(?:to|in)\s*(kg|kilos?)/i, fn: (m) => `${(parseFloat(m[1]) * 0.453592).toFixed(2)} kg` },
        { regex: /([0-9.]+)\s*(c|celsius)\s*(?:to|in)\s*(f|fahrenheit)/i, fn: (m) => `${((parseFloat(m[1]) * 9/5) + 32).toFixed(1)}°F` },
        { regex: /([0-9.]+)\s*(f|fahrenheit)\s*(?:to|in)\s*(c|celsius)/i, fn: (m) => `${(((parseFloat(m[1]) - 32) * 5/9)).toFixed(1)}°C` },
        { regex: /([0-9.]+)\s*(usd|\$)\s*(?:to|in)\s*(eur|€)/i, fn: (m) => `€${(parseFloat(m[1]) * 0.92).toFixed(2)} EUR` },
        { regex: /([0-9.]+)\s*(eur|€)\s*(?:to|in)\s*(usd|\$)/i, fn: (m) => `$${(parseFloat(m[1]) * 1.09).toFixed(2)} USD` },
        { regex: /([0-9.]+)\s*(gbp|£)\s*(?:to|in)\s*(usd|\$)/i, fn: (m) => `$${(parseFloat(m[1]) * 1.30).toFixed(2)} USD` }
      ];

      for (let uc of unitConversions) {
        const m = lower.match(uc.regex);
        if (m) {
          const res = uc.fn(m);
          cardsHtml += `
            <div class="tray-card">
              <div class="tray-card-left" onclick="copyEverythingResult('${res}')">
                <span class="tray-icon" style="background:#0d9488; color:#fff;">📐</span>
                <div>
                  <div class="tray-title" style="color:#2dd4bf; font-weight:700;">= ${res}</div>
                  <div class="tray-sub">${q} · Unit Conversion</div>
                </div>
              </div>
              <div class="tray-actions">
                <button class="tray-btn" onclick="copyEverythingResult('${res}')">📋 Copy</button>
              </div>
            </div>
          `;
          break;
        }
      }

      // 6. PRIVATE WEB SEARCH FALLBACK
      cardsHtml += `
        <div class="tray-card" onclick="searchEverythingWeb('${q}')">
          <div class="tray-card-left">
            <span class="tray-icon" style="background:#4f46e5; color:#fff;">🔍</span>
            <div>
              <div class="tray-title">Search DuckDuckGo</div>
              <div class="tray-sub">"${q}" · Telemetry-free private search</div>
            </div>
          </div>
          <div class="tray-actions">
            <button class="tray-btn primary" onclick="searchEverythingWeb('${q}')">Search</button>
          </div>
        </div>
      `;

      tray.innerHTML = cardsHtml;
      tray.style.display = 'flex';
    }

    function makeEverythingCall(name, number) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      initiateCall(name, number);
    }

    function openEverythingMessage(name, number) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      launchForegroundApp('messages');
      showToast(`💬 Messaging thread opened for ${name} (${number})`);
    }

    function openEverythingZeroChat(name) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      launchForegroundApp('zerochat');
      showToast(`🔒 Encrypted ZeroChat opened with ${name}`);
    }

    function saveEverythingContact(number) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      showToast(`👤 Contact saved: ${number}`);
    }

    function copyEverythingResult(val) {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(val);
      }
      showToast(`📋 Copied to clipboard: ${val}`);
    }

    function searchEverythingWeb(query) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      showToast(`🌐 Opening private search for "${query}" (Ad trackers blocked)`);
      launchForegroundApp('chrome');
    }
"""

if 'function onEverythingBarInput' not in text:
    text = text.replace('function executeSearchCommand() {', everything_js + '\n    function executeSearchCommand() {')

# 4. ENHANCE executeSearchCommand() to handle direct conversational syntax
enhanced_exec_search = """function executeSearchCommand() {
      const input = document.getElementById('androidSearchInput');
      const val = input.value.trim();
      const tray = document.getElementById('everythingResultsTray');
      if (tray) tray.style.display = 'none';
      if (!val) return;
      input.value = '';

      const lower = val.toLowerCase();

      // Check direct "call <contact>"
      if (lower.startsWith('call ') || lower.startsWith('dial ')) {
        const target = val.replace(/^(call|dial)\s+/i, '').trim();
        const found = CONTACTS_DIRECTORY.find(c => c.name.toLowerCase().includes(target.toLowerCase()));
        if (found) {
          initiateCall(found.name, found.number);
          return;
        } else {
          initiateCall(target, target);
          return;
        }
      }

      // Check direct "message <contact>" or "text <contact>"
      if (lower.startsWith('message ') || lower.startsWith('msg ') || lower.startsWith('text ')) {
        const parts = val.replace(/^(message|msg|text)\s+/i, '').split(' ');
        const target = parts[0];
        const found = CONTACTS_DIRECTORY.find(c => c.name.toLowerCase().includes(target.toLowerCase()));
        launchForegroundApp('messages');
        showToast(`💬 SMS opened for ${found ? found.name : target}`);
        return;
      }

      // Check direct "chat <contact>"
      if (lower.startsWith('chat ')) {
        const target = val.replace(/^chat\s+/i, '').trim();
        launchForegroundApp('zerochat');
        showToast(`🔒 ZeroChat opened with ${target}`);
        return;
      }

      sendCommand(val);
    }"""

text = re.sub(r'function executeSearchCommand\(\)\s*\{[\s\S]*?sendCommand\(val\);\s*\}', lambda m: enhanced_exec_search, text)

with open(app_py, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated simulator/app.py with full Everything Bar!")
