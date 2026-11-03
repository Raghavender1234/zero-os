import os
import re
import shutil

root = r"C:\Users\brred\.gemini\antigravity\scratch\zero_os"
parser_path = os.path.join(root, 'app', 'src', 'main', 'java', 'com', 'zeroos', 'launcher', 'core', 'CommandParser.kt')
aosp_parser_path = os.path.join(root, 'aosp', 'packages', 'apps', 'ZeroLauncher', 'src', 'main', 'java', 'com', 'zeroos', 'launcher', 'core', 'CommandParser.kt')
activity_path = os.path.join(root, 'app', 'src', 'main', 'java', 'com', 'zeroos', 'launcher', 'ui', 'ZeroLauncherActivity.kt')
aosp_activity_path = os.path.join(root, 'aosp', 'packages', 'apps', 'ZeroLauncher', 'src', 'main', 'java', 'com', 'zeroos', 'launcher', 'ui', 'ZeroLauncherActivity.kt')
app_py_path = os.path.join(root, 'simulator', 'app.py')

# ==============================================================================
# 1. UPDATE CommandParser.kt for ZeroFlow
# ==============================================================================
with open(parser_path, 'r', encoding='utf-8') as f:
    p_code = f.read()

# Add ZeroCommand data classes
p_code = p_code.replace(
    '    data class SetAlarm(val hour: Int, val minutes: Int, val label: String) : ZeroCommand()',
    '    data class SetAlarm(val hour: Int, val minutes: Int, val label: String) : ZeroCommand()\n    data class CreateRoutine(val name: String, val trigger: String, val actions: List<String>, val raw: String) : ZeroCommand()\n    object ShowAutomations : ZeroCommand()'
)

# Add parsing rules
zeroflow_parsing = """        // ZEROFLOW: AUTOMATIONS & ROUTINES
        if (lower == "routines" || lower == "automations" || lower == "/routines" || lower == "/auto") {
            return ZeroCommand.ShowAutomations
        }
        if (lower.startsWith("auto:") || lower.startsWith("routine:") || lower.startsWith("when ") || lower.startsWith("if ")) {
            val clean = text.replace(Regex("^(auto:|routine:|when|if)\\\\s*", RegexOption.IGNORE_CASE), "").trim()
            val triggerPart: String
            val actionPart: String
            if (clean.contains(" then ", ignoreCase = true)) {
                val parts = clean.split(Regex("\\\\bthen\\\\b", RegexOption.IGNORE_CASE), limit = 2)
                triggerPart = parts[0].trim()
                actionPart = parts[1].trim()
            } else if (clean.contains(" do ", ignoreCase = true)) {
                val parts = clean.split(Regex("\\\\bdo\\\\b", RegexOption.IGNORE_CASE), limit = 2)
                triggerPart = parts[0].trim()
                actionPart = parts[1].trim()
            } else {
                // Heuristic split e.g. "at 11pm grayscale and silent"
                val timeMatch = Regex("^(at\\\\s+\\\\d{1,2}(?::\\\\d{2})?\\\\s*(?:am|pm)?)\\\\s+(.*)$", RegexOption.IGNORE_CASE).find(clean)
                val battMatch = Regex("^(battery\\\\s*(?:<|<=|below)\\\\s*\\\\d+%?)\\\\s+(.*)$", RegexOption.IGNORE_CASE).find(clean)
                val wifiMatch = Regex("^(wifi\\\\s+[a-zA-Z0-9_-]+)\\\\s+(.*)$", RegexOption.IGNORE_CASE).find(clean)
                when {
                    timeMatch != null -> {
                        triggerPart = timeMatch.groupValues[1]
                        actionPart = timeMatch.groupValues[2]
                    }
                    battMatch != null -> {
                        triggerPart = battMatch.groupValues[1]
                        actionPart = battMatch.groupValues[2]
                    }
                    wifiMatch != null -> {
                        triggerPart = wifiMatch.groupValues[1]
                        actionPart = wifiMatch.groupValues[2]
                    }
                    else -> {
                        triggerPart = "Event detected"
                        actionPart = clean
                    }
                }
            }
            val actions = actionPart.split(Regex("[,&]|\\\\band\\\\b", RegexOption.IGNORE_CASE)).map { it.trim() }.filter { it.isNotEmpty() }
            return ZeroCommand.CreateRoutine(name = "Auto: $triggerPart", trigger = triggerPart, actions = actions, raw = text)
        }
"""

p_code = p_code.replace('        // 0. DIRECTIONS & OFFLINE ROUTING', zeroflow_parsing + '\n        // 0. DIRECTIONS & OFFLINE ROUTING')

with open(parser_path, 'w', encoding='utf-8') as f:
    f.write(p_code)
shutil.copyfile(parser_path, aosp_parser_path)
print("Updated CommandParser.kt with ZeroFlow in app and AOSP!")

# ==============================================================================
# 2. UPDATE ZeroLauncherActivity.kt for ZeroFlow
# ==============================================================================
with open(activity_path, 'r', encoding='utf-8') as f:
    act_code = f.read()

act_branches = """            is ZeroCommand.CreateRoutine -> {
                systemLog = "⚡ ZeroFlow Routine SAVED: WHEN ${cmd.trigger} -> DO ${cmd.actions.joinToString()}."
            }
            is ZeroCommand.ShowAutomations -> {
                activeAppView = "settings"
                systemLog = "⚡ ZeroFlow Active Routines opened."
            }
"""

act_code = act_code.replace('            is ZeroCommand.SetAlarm -> {', act_branches + '            is ZeroCommand.SetAlarm -> {')

with open(activity_path, 'w', encoding='utf-8') as f:
    f.write(act_code)
shutil.copyfile(activity_path, aosp_activity_path)
print("Updated ZeroLauncherActivity.kt with ZeroFlow in app and AOSP!")

# ==============================================================================
# 3. UPDATE simulator/app.py WITH ZEROFLOW CORE ENGINE & UI
# ==============================================================================
with open(app_py_path, 'r', encoding='utf-8') as f:
    sim = f.read()

# Add ZeroFlow routines registry and helper functions
zeroflow_js_engine = """
    // ==============================================================
    // ZEROFLOW ON-DEVICE AUTOMATIONS ENGINE (v1.0)
    // ==============================================================
    let zeroFlowRoutines = [
      {
        id: "rf_bedtime",
        name: "🌙 Bedtime Protocol",
        trigger: "Daily at 11:00 PM",
        actions: ["Grayscale Mode ON", "Sound: Silent", "AirGap Background Telemetry"],
        enabled: true,
        lastRun: "Yesterday, 11:00 PM"
      },
      {
        id: "rf_battery",
        name: "🔋 Extreme Battery Guard",
        trigger: "Battery drops below 15%",
        actions: ["Engage DIA Mode (1Hz OLED)", "Kill Social Sockets"],
        enabled: true,
        lastRun: "2 days ago"
      },
      {
        id: "rf_car",
        name: "🚗 Commute & Navigation",
        trigger: "Bluetooth connected: Sony WH-1000XM5",
        actions: ["Launch ZeroMaps", "Calm Digest: Hold Alerts"],
        enabled: false,
        lastRun: "Never"
      }
    ];

    function toggleRoutine(id) {
      const r = zeroFlowRoutines.find(x => x.id === id);
      if (r) {
        r.enabled = !r.enabled;
        showToast(`⚡ ${r.name} is now ${r.enabled ? 'ACTIVE' : 'PAUSED'}`);
        if (state.active_app === 'settings') {
          launchForegroundApp('settings');
        }
      }
    }

    function deleteRoutine(id) {
      zeroFlowRoutines = zeroFlowRoutines.filter(x => x.id !== id);
      showToast(`🗑️ Routine deleted.`);
      if (state.active_app === 'settings') {
        launchForegroundApp('settings');
      }
    }

    function saveZeroFlowRoutine(name, trigger, actionsStr) {
      const actions = actionsStr.split('|');
      const newRoutine = {
        id: "rf_" + Date.now(),
        name: name,
        trigger: trigger,
        actions: actions,
        enabled: true,
        lastRun: "Just now"
      };
      zeroFlowRoutines.unshift(newRoutine);
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      showToast(`⚡ ZeroFlow SAVED: "${name}" is armed & ready.`);
    }

    function parseZeroFlowInput(raw) {
      const clean = raw.replace(/^(auto:|routine:|when|if)\s*/i, '').trim();
      let trigger = "Event";
      let actions = [];

      if (/then/i.test(clean)) {
        const parts = clean.split(/\bthen\b/i);
        trigger = parts[0].trim();
        actions = parts[1].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
      } else if (/\bat\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?/i.test(clean)) {
        const m = clean.match(/^(at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(.*)$/i);
        if (m) {
          trigger = "Daily " + m[1];
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else if (/battery/i.test(clean)) {
        const m = clean.match(/^(battery\s*(?:<|<=|below)\s*\d+%?)\s+(.*)$/i);
        if (m) {
          trigger = m[1].replace(/</, 'below ');
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else if (/wifi/i.test(clean)) {
        const m = clean.match(/^(wifi\s+[a-zA-Z0-9_-]+)\s+(.*)$/i);
        if (m) {
          trigger = "Connected to " + m[1];
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else {
        trigger = "Smart Context";
        actions = clean.split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
      }

      if (actions.length === 0) actions = ["Execute ZeroOS Action"];
      return { trigger, actions, name: `⚡ Routine: ${trigger}` };
    }
"""

if 'ZEROFLOW ON-DEVICE AUTOMATIONS ENGINE' not in sim:
    sim = sim.replace('function onEverythingBarInput(raw) {', zeroflow_js_engine + '\n    function onEverythingBarInput(raw) {')

# Add ZeroFlow card detection in onEverythingBarInput
zeroflow_card_check = """
      // 0. ZEROFLOW AUTOMATION PARSING (e.g. auto: at 11pm grayscale and silent, auto: battery < 15% dia mode)
      if (lower.startsWith('auto:') || lower.startsWith('routine:') || lower.startsWith('when ') || lower.startsWith('if ') || lower === 'routines' || lower === 'automations') {
        if (lower === 'routines' || lower === 'automations') {
          cardsHtml += `
            <div class="tray-card">
              <div class="tray-card-left" onclick="launchForegroundApp('settings')">
                <span class="tray-icon" style="background:#8b5cf6; color:#fff;">⚡</span>
                <div>
                  <div class="tray-title" style="color:#c084fc; font-size:1.05rem; font-weight:700;">ZeroFlow Automations</div>
                  <div class="tray-sub">${zeroFlowRoutines.filter(r => r.enabled).length} active routines · Tap to manage</div>
                </div>
              </div>
              <div class="tray-actions">
                <button class="tray-btn primary" onclick="launchForegroundApp('settings')">Manage</button>
              </div>
            </div>
          `;
        } else {
          const parsed = parseZeroFlowInput(q);
          const actionsStr = parsed.actions.join(' · ');
          const actionsArg = parsed.actions.join('|');
          cardsHtml += `
            <div class="tray-card" style="border-left: 3px solid #a855f7;">
              <div class="tray-card-left" onclick="saveZeroFlowRoutine('${parsed.name}', '${parsed.trigger}', '${actionsArg}')">
                <span class="tray-icon" style="background:#8b5cf6; color:#fff;">⚡</span>
                <div>
                  <div class="tray-title" style="color:#c084fc; font-size:1.05rem; font-weight:700;">${parsed.name}</div>
                  <div class="tray-sub">WHEN <b>${parsed.trigger}</b> → DO: <b>${actionsStr}</b></div>
                </div>
              </div>
              <div class="tray-actions">
                <button class="tray-btn primary" style="background:#8b5cf6; border-color:#a855f7;" onclick="saveZeroFlowRoutine('${parsed.name}', '${parsed.trigger}', '${actionsArg}')">⚡ Save Routine</button>
              </div>
            </div>
          `;
        }
      }
"""

if '// 0. ZEROFLOW AUTOMATION PARSING' not in sim:
    sim = sim.replace('// 0a. TIMER DETECTION', zeroflow_card_check + '\n      // 0a. TIMER DETECTION')

# Add execution on Enter in executeSearchCommand()
zeroflow_enter = """
      // Check direct "auto:" or "routine:"
      if (lower.startsWith('auto:') || lower.startsWith('routine:') || lower.startsWith('when ') || lower.startsWith('if ')) {
        const parsed = parseZeroFlowInput(val);
        saveZeroFlowRoutine(parsed.name, parsed.trigger, parsed.actions.join('|'));
        return;
      }
      if (lower === 'routines' || lower === 'automations') {
        launchForegroundApp('settings');
        return;
      }
"""

if 'Check direct "auto:" or "routine:"' not in sim:
    sim = sim.replace('// Check direct "timer <duration>"', zeroflow_enter + '\n      // Check direct "timer <duration>"')

# Add ZeroFlow Section to Settings App view
settings_zeroflow_section = """
            <!-- ZeroFlow Automations Section in Settings -->
            <div style="margin: 8px 0 4px 0; display:flex; align-items:center; justify-content:space-between;">
              <span style="font-size:0.8rem; font-weight:700; color:#c084fc; text-transform:uppercase; letter-spacing:0.05em;">⚡ ZeroFlow Automations</span>
              <span style="font-size:0.7rem; color:#94a3b8;">${zeroFlowRoutines.filter(r=>r.enabled).length} active</span>
            </div>
            
            <div style="display:flex; flex-direction:column; gap:6px;">
              ${zeroFlowRoutines.map(r => `
                <div style="background:rgba(139, 92, 246, 0.1); border:1px solid rgba(139, 92, 246, 0.3); border-radius:12px; padding:10px 12px; display:flex; align-items:center; justify-content:space-between;">
                  <div style="display:flex; flex-direction:column; gap:2px; max-width:75%;">
                    <div style="font-size:0.88rem; font-weight:700; color:#fff;">${r.name}</div>
                    <div style="font-size:0.74rem; color:#c084fc;">WHEN <b>${r.trigger}</b></div>
                    <div style="font-size:0.7rem; color:#94a3b8;">DO: ${r.actions.join(' · ')}</div>
                  </div>
                  <div style="display:flex; align-items:center; gap:8px;">
                    <button onclick="toggleRoutine('${r.id}')" style="background:${r.enabled ? '#8b5cf6' : '#334155'}; border:none; color:#fff; font-size:0.7rem; font-weight:700; padding:5px 10px; border-radius:6px; cursor:pointer;">
                      ${r.enabled ? 'ACTIVE' : 'PAUSED'}
                    </button>
                    <button onclick="deleteRoutine('${r.id}')" style="background:transparent; border:none; color:#ef4444; font-size:0.85rem; cursor:pointer; padding:2px 4px;">✕</button>
                  </div>
                </div>
              `).join('')}
            </div>
"""

# Insert inside settings body before Battery & Longevity card
if 'ZeroFlow Automations Section in Settings' not in sim:
    sim = sim.replace('<div class="settings-card" onclick="toggleFeature(\'nokia\')">', settings_zeroflow_section + '\n            <div class="settings-card" onclick="toggleFeature(\'nokia\')">')

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(sim)

print("Updated simulator/app.py with ZeroFlow Core Engine & Settings view!")
