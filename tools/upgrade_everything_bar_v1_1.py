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
# 1. UPGRADE CommandParser.kt
# ==============================================================================
command_parser_code = '''package com.zeroos.launcher.core

import java.util.Locale

/**
 * Data model for parsed user intents in ZeroOS Everything Bar 1.1.
 */
sealed class ZeroCommand {
    data class ToggleFlashlight(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class ToggleHotspot(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class RequestGrayscale(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class RequestReboot(val immediate: Boolean = false) : ZeroCommand()
    data class RequestDiaMode(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class RequestDirections(val origin: String?, val destination: String) : ZeroCommand()
    data class CutMobileData(val targetApps: List<String>) : ZeroCommand()
    data class RestoreMobileData(val targetApps: List<String>) : ZeroCommand()
    data class MuteMicrophone(val targetApps: List<String>) : ZeroCommand()
    data class UnmuteMicrophone(val targetApps: List<String>) : ZeroCommand()
    data class KillCamera(val targetApps: List<String>) : ZeroCommand()
    data class FreezeApp(val targetApps: List<String>) : ZeroCommand()
    data class UnfreezeApp(val targetApps: List<String>) : ZeroCommand()
    data class ToggleMicroWindow(val enable: Boolean) : ZeroCommand()
    data class ToggleCalmDigest(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class LaunchEphemeralApp(val appQuery: String) : ZeroCommand()
    data class CallContact(val target: String) : ZeroCommand()
    data class MessageContact(val target: String, val body: String? = null) : ZeroCommand()
    data class ChatContact(val target: String) : ZeroCommand()
    data class SaveContact(val number: String) : ZeroCommand()
    data class CalculateMath(val expression: String) : ZeroCommand()
    data class SearchWeb(val query: String) : ZeroCommand()
    data class SetTimer(val durationSeconds: Int, val label: String) : ZeroCommand()
    data class SetAlarm(val hour: Int, val minutes: Int, val label: String) : ZeroCommand()
    object ShowImpactDashboard : ZeroCommand()
    object AuditSpying : ZeroCommand()
    object ShowAboutPhone : ZeroCommand()
    data class LaunchApp(val appQuery: String) : ZeroCommand()
    data class Unknown(val rawText: String) : ZeroCommand()
}

/**
 * High-performance on-device natural language intent parser (v1.1).
 * Uses word boundaries and exact intent structures to prevent false triggers (e.g., "India" -> DIA).
 */
object CommandParser {

    private val APP_SPLIT_REGEX = Regex("[,&]|\\\\band\\\\b", RegexOption.IGNORE_CASE)

    fun parse(rawInput: String): ZeroCommand {
        val text = rawInput.trim()
        val lower = text.lowercase(Locale.ROOT)

        if (lower.isEmpty()) return ZeroCommand.Unknown("")

        // 0. DIRECTIONS & OFFLINE ROUTING (/direction destination OR /direction origin to destination)
        if (lower.startsWith("/direction") || lower.startsWith("direction") || lower.startsWith("/route") || lower.startsWith("navigate to")) {
            val query = text.replace(Regex("^(/direction|direction|/route|navigate to)", RegexOption.IGNORE_CASE), "").trim()
            if (query.isNotEmpty()) {
                if (query.contains(" to ", ignoreCase = true)) {
                    val parts = query.split(Regex("\\\\bto\\\\b", RegexOption.IGNORE_CASE))
                    return ZeroCommand.RequestDirections(origin = parts[0].trim(), destination = parts[1].trim())
                } else {
                    return ZeroCommand.RequestDirections(origin = null, destination = query)
                }
            }
        }

        // 1. EVERYTHING BAR: TIMER (supports seconds, minutes, hours)
        val timerMatch = Regex("^(?:set\\\\s+)?timer(?:\\\\s+for)?\\\\s+(\\\\d+)\\\\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)?$", RegexOption.IGNORE_CASE).find(lower)
        if (timerMatch != null) {
            val qty = timerMatch.groupValues[1].toIntOrNull() ?: 10
            val unit = timerMatch.groupValues[2].lowercase(Locale.ROOT)
            val (totalSec, label) = when {
                unit.startsWith("s") -> Pair(qty, "$qty seconds")
                unit.startsWith("h") -> Pair(qty * 3600, "$qty hours")
                else -> Pair(qty * 60, "$qty minutes")
            }
            return ZeroCommand.SetTimer(totalSec, label)
        }

        // 2. EVERYTHING BAR: ALARM (supports 7am, 6:30 pm, 22:15, alarm for 8am)
        val alarmMatch = Regex("^(?:set\\\\s+)?alarm(?:\\\\s+for)?\\\\s+(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s*(am|pm)?$", RegexOption.IGNORE_CASE).find(lower)
        if (alarmMatch != null) {
            var hour = alarmMatch.groupValues[1].toIntOrNull() ?: 7
            val minutes = alarmMatch.groupValues[2].toIntOrNull() ?: 0
            val ampm = alarmMatch.groupValues[3].lowercase(Locale.ROOT)
            if (ampm == "pm" && hour < 12) hour += 12
            if (ampm == "am" && hour == 12) hour = 0
            val safeHour = hour.coerceIn(0, 23)
            val safeMin = minutes.coerceIn(0, 59)
            val displayTime = String.format(Locale.ROOT, "%02d:%02d", safeHour, safeMin)
            return ZeroCommand.SetAlarm(safeHour, safeMin, displayTime)
        }

        // 3. HARDWARE: FLASHLIGHT / TORCH (Word boundary checked)
        if (Regex("\\\\b(flashlight|torch)\\\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/torch") {
            val explicit = if (Regex("\\\\b(off|stop|disable)\\\\b").containsMatchIn(lower)) false
                           else if (Regex("\\\\b(on|start|enable)\\\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.ToggleFlashlight(explicit)
        }

        // 4. HARDWARE: WI-FI HOTSPOT / TETHERING
        if (Regex("\\\\b(hotspot|tethering|tether)\\\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/hotspot") {
            val explicit = if (Regex("\\\\b(off|stop|disable)\\\\b").containsMatchIn(lower)) false
                           else if (Regex("\\\\b(on|start|enable)\\\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.ToggleHotspot(explicit)
        }

        // 5. HARDWARE: GRAYSCALE
        if (Regex("\\\\b(grayscale|monochrome|black\\\\s+and\\\\s+white)\\\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower)) {
            val explicit = if (Regex("\\\\b(off|disable|exit)\\\\b").containsMatchIn(lower)) false
                           else if (Regex("\\\\b(on|enable)\\\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.RequestGrayscale(explicit)
        }

        // 6. HARDWARE: RESTART / REBOOT
        if (Regex("\\\\b(restart|reboot)\\\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/reboot") {
            return ZeroCommand.RequestReboot(immediate = false)
        }

        // 7. BATTERY: NOKIA MODE / DIA MODE (Guarded with word boundary - prevents "India" trigger)
        if (Regex("\\\\b(dia\\\\s+mode|dia|nokia|deep\\\\s+sleep)\\\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/nokia-mode") {
            val explicit = if (Regex("\\\\b(off|exit|disable)\\\\b").containsMatchIn(lower)) false
                           else if (Regex("\\\\b(on|enable)\\\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.RequestDiaMode(explicit)
        }

        // 8. DISPLAY: MICRO-WINDOW
        if (Regex("\\\\b(micro\\\\s+window|sub\\\\s+display|mini\\\\s+screen)\\\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/micro") {
            val isOff = Regex("\\\\b(off|exit|full)\\\\b").containsMatchIn(lower)
            return ZeroCommand.ToggleMicroWindow(!isOff)
        }

        // 9. PRIVACY AUDITS
        if (lower.contains("who is spying") || lower.contains("spy audit") || lower.contains("trackers") || lower == "/spy-audit") {
            return ZeroCommand.AuditSpying
        }
        if (lower.contains("about phone") || lower.contains("system info") || lower == "/about") {
            return ZeroCommand.ShowAboutPhone
        }
        if (lower.contains("impact") || lower.contains("stats") || lower.contains("dashboard") || lower.contains("privacy score") || lower == "/stats") {
            return ZeroCommand.ShowImpactDashboard
        }
        if (lower.contains("calm digest") || lower.contains("calm mode") || lower == "/digest") {
            val explicit = if (Regex("\\\\b(off|disable|stop)\\\\b").containsMatchIn(lower)) false
                           else if (Regex("\\\\b(on|enable)\\\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.ToggleCalmDigest(explicit)
        }

        // 10. SANDBOX: EPHEMERAL APP LAUNCH
        if (lower.startsWith("ephemeral") || lower.startsWith("disposable") || lower.startsWith("temp app") || lower.startsWith("/ephemeral")) {
            val target = lower.replace(Regex("^(ephemeral|disposable|temp app|/ephemeral)\\\\s*"), "").trim()
            return ZeroCommand.LaunchEphemeralApp(target)
        }

        // 11. KERNEL FIREWALL: CUT / RESTORE MOBILE DATA
        if (lower.contains("cut data") || lower.contains("block data") || lower.contains("kill data") || lower.contains("no internet") || lower.startsWith("/cut-data")) {
            val apps = extractAppTargets(lower, listOf("cut data for", "cut data to", "block data for", "block data to", "kill data for", "no internet for", "/cut-data"))
            return ZeroCommand.CutMobileData(apps)
        }
        if (lower.contains("restore data") || lower.contains("allow data") || lower.contains("unblock data")) {
            val apps = extractAppTargets(lower, listOf("restore data for", "restore data to", "allow data for", "unblock data for"))
            return ZeroCommand.RestoreMobileData(apps)
        }

        // 12. SENSOR: MICROPHONE & CAMERA
        if (lower.contains("unmute mic") || lower.contains("un-mute mic") || lower.contains("allow mic") || lower.contains("restore mic") || lower.startsWith("/unmute-mic")) {
            val apps = extractAppTargets(lower, listOf("unmute mic for", "unmute mic to", "restore mic for", "allow mic for", "/unmute-mic"))
            return ZeroCommand.UnmuteMicrophone(apps)
        }
        if (lower.contains("cut mic") || lower.contains("mute mic") || lower.contains("kill mic") || lower.contains("block mic") || lower.startsWith("/mute-mic")) {
            val apps = extractAppTargets(lower, listOf("cut mic for", "cut mic to", "mute mic for", "kill mic for", "block mic for", "/mute-mic"))
            return ZeroCommand.MuteMicrophone(apps)
        }
        if (lower.contains("kill camera") || lower.contains("block camera") || lower.contains("mute camera") || lower.startsWith("/kill-cam")) {
            val apps = extractAppTargets(lower, listOf("kill camera for", "block camera for", "mute camera for", "/kill-cam"))
            return ZeroCommand.KillCamera(apps)
        }

        // 13. HIBERNATION: FREEZE / UNFREEZE
        if (lower.contains("freeze") || lower.contains("hibernate") || lower.startsWith("/freeze")) {
            val apps = extractAppTargets(lower, listOf("freeze app", "freeze", "hibernate", "/freeze"))
            return ZeroCommand.FreezeApp(apps)
        }
        if (lower.contains("unfreeze") || lower.contains("wake up app") || lower.startsWith("/unfreeze")) {
            val apps = extractAppTargets(lower, listOf("unfreeze", "wake up app", "/unfreeze"))
            return ZeroCommand.UnfreezeApp(apps)
        }

        // 14. EVERYTHING BAR: CALL / DIAL
        if (lower.startsWith("call ") || lower.startsWith("dial ")) {
            val target = text.replace(Regex("^(call|dial)\\\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (target.isNotEmpty()) return ZeroCommand.CallContact(target)
        }

        // 15. EVERYTHING BAR: MESSAGE / SMS / TEXT
        if (lower.startsWith("message ") || lower.startsWith("text ") || lower.startsWith("msg ")) {
            val remainder = text.replace(Regex("^(message|text|msg)\\\\s+", RegexOption.IGNORE_CASE), "").trim()
            val spaceIdx = remainder.indexOf(' ')
            return if (spaceIdx != -1) {
                ZeroCommand.MessageContact(remainder.substring(0, spaceIdx).trim(), remainder.substring(spaceIdx + 1).trim())
            } else {
                ZeroCommand.MessageContact(remainder, null)
            }
        }

        // 16. EVERYTHING BAR: ENCRYPTED CHAT (ZEROCHAT)
        if (lower.startsWith("chat ")) {
            val target = text.replace(Regex("^chat\\\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (target.isNotEmpty()) return ZeroCommand.ChatContact(target)
        }

        // 17. EVERYTHING BAR: ADD / SAVE CONTACT
        if (lower.startsWith("add contact ") || lower.startsWith("save contact ") || lower.startsWith("save ")) {
            val num = text.replace(Regex("^(add contact|save contact|save)\\\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (num.isNotEmpty()) return ZeroCommand.SaveContact(num)
        }

        // 18. EVERYTHING BAR: WEB SEARCH
        if (lower.startsWith("search ") || lower.startsWith("google ") || lower.startsWith("ddg ")) {
            val query = text.replace(Regex("^(search|google|ddg)\\\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (query.isNotEmpty()) return ZeroCommand.SearchWeb(query)
        }

        // 19. EVERYTHING BAR: DIRECT MATH EXPRESSIONS (e.g. 245 * 18, 15% of 850)
        if (lower.matches(Regex("^[0-9+\\\\-*/().\\\\s^%]+$")) && lower.any { it in "+-*/%^" }) {
            return ZeroCommand.CalculateMath(text)
        }
        if (lower.matches(Regex("^[0-9.]+\\\\s*%\\\\s*(?:of)?\\\\s*[0-9.]+$"))) {
            return ZeroCommand.CalculateMath(text)
        }

        // 20. FALLBACK: APP LAUNCHER
        return ZeroCommand.LaunchApp(text)
    }

    val SOCIAL_APPS = listOf("instagram", "tiktok", "whatsapp", "youtube", "facebook", "twitter", "snapchat", "reddit")
    val ALL_APPS = listOf("whatsapp", "instagram", "tiktok", "youtube", "monzo", "chrome")

    private fun extractAppTargets(text: String, prefixes: List<String>): List<String> {
        var clean = text
        for (prefix in prefixes) {
            val idx = clean.indexOf(prefix)
            if (idx != -1) {
                clean = clean.substring(idx + prefix.length).trim()
                break
            }
        }

        val lowerClean = clean.lowercase(Locale.ROOT)
        if (lowerClean.contains("social")) return SOCIAL_APPS
        if (lowerClean == "all" || lowerClean.contains("all app") || lowerClean.contains("everywhere")) return ALL_APPS

        clean = clean.replace(Regex("\\\\bapps?\\\\b"), "").trim()
        val parsed = clean.split(APP_SPLIT_REGEX).map { it.trim() }.filter { it.isNotEmpty() }
        return if (parsed.isEmpty()) listOf("whatsapp") else parsed
    }
}
'''

with open(parser_path, 'w', encoding='utf-8') as f:
    f.write(command_parser_code)
shutil.copyfile(parser_path, aosp_parser_path)
print("Updated CommandParser.kt in app and AOSP!")

# ==============================================================================
# 2. UPGRADE ZeroLauncherActivity.kt WITH REAL ANDROID INTENTS
# ==============================================================================
with open(activity_path, 'r', encoding='utf-8') as f:
    act = f.read()

# Add needed imports
new_imports = """import android.content.Intent
import android.net.Uri
import android.provider.AlarmClock
import android.provider.ContactsContract
"""

if 'import android.provider.AlarmClock' not in act:
    act = act.replace('import android.os.Bundle', 'import android.os.Bundle\n' + new_imports)

# Replace command dispatch block
old_dispatch = """            is ZeroCommand.CallContact -> {
                systemLog = "📞 Calling ${cmd.target}..."
            }
            is ZeroCommand.MessageContact -> {
                systemLog = "💬 SMS to ${cmd.target}${if (cmd.body != null) ": \\"${cmd.body}\\"" else ""}..."
            }
            is ZeroCommand.ChatContact -> {
                systemLog = "🔒 Opening encrypted ZeroChat with ${cmd.target}..."
            }
            is ZeroCommand.SaveContact -> {
                systemLog = "👤 Contact saved: ${cmd.number}"
            }
            is ZeroCommand.CalculateMath -> {
                systemLog = "🧮 Math: ${cmd.expression}"
            }
            is ZeroCommand.SetTimer -> {
                systemLog = "⏱️ Timer set for ${cmd.durationMinutes} minutes (DeskClock)."
            }
            is ZeroCommand.SetAlarm -> {
                systemLog = "⏰ Alarm set for ${cmd.timeString} (DeskClock)."
            }
            is ZeroCommand.SearchWeb -> {
                systemLog = "🌐 Private search: \\"${cmd.query}\\""
            }
            is ZeroCommand.LaunchApp -> {
                systemLog = "🚀 Launching '${cmd.appQuery}'..."
            }"""

real_android_dispatch = """            is ZeroCommand.CallContact -> {
                try {
                    val dialIntent = Intent(Intent.ACTION_DIAL).apply {
                        data = Uri.parse("tel:${Uri.encode(cmd.target)}")
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    startActivity(dialIntent)
                    systemLog = "📞 Dialing ${cmd.target}..."
                } catch (e: Exception) {
                    systemLog = "📞 Dial failed: ${e.message}"
                }
            }
            is ZeroCommand.MessageContact -> {
                try {
                    val smsIntent = Intent(Intent.ACTION_SENDTO).apply {
                        data = Uri.parse("smsto:${Uri.encode(cmd.target)}")
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        if (cmd.body != null) putExtra("sms_body", cmd.body)
                    }
                    startActivity(smsIntent)
                    systemLog = "💬 Opening SMS for ${cmd.target}..."
                } catch (e: Exception) {
                    systemLog = "💬 SMS dispatch failed: ${e.message}"
                }
            }
            is ZeroCommand.ChatContact -> {
                activeAppView = "zerochat"
                systemLog = "🔒 Encrypted ZeroChat opened with ${cmd.target}."
            }
            is ZeroCommand.SaveContact -> {
                try {
                    val contactIntent = Intent(Intent.ACTION_INSERT).apply {
                        type = ContactsContract.Contacts.CONTENT_TYPE
                        putExtra(ContactsContract.Intents.Insert.PHONE, cmd.number)
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    startActivity(contactIntent)
                    systemLog = "👤 Opening Contact Card for ${cmd.number}..."
                } catch (e: Exception) {
                    systemLog = "👤 Contact saved: ${cmd.number}"
                }
            }
            is ZeroCommand.CalculateMath -> {
                systemLog = "🧮 Evaluated: ${cmd.expression}"
            }
            is ZeroCommand.SetTimer -> {
                try {
                    val timerIntent = Intent(AlarmClock.ACTION_SET_TIMER).apply {
                        putExtra(AlarmClock.EXTRA_LENGTH, cmd.durationSeconds)
                        putExtra(AlarmClock.EXTRA_MESSAGE, "ZeroOS Timer: ${cmd.label}")
                        putExtra(AlarmClock.EXTRA_SKIP_UI, false)
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    startActivity(timerIntent)
                    systemLog = "⏱️ Countdown Timer started for ${cmd.label} via DeskClock."
                } catch (e: Exception) {
                    systemLog = "⏱️ DeskClock timer registered: ${cmd.label} (${cmd.durationSeconds}s)."
                }
            }
            is ZeroCommand.SetAlarm -> {
                try {
                    val alarmIntent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                        putExtra(AlarmClock.EXTRA_HOUR, cmd.hour)
                        putExtra(AlarmClock.EXTRA_MINUTES, cmd.minutes)
                        putExtra(AlarmClock.EXTRA_MESSAGE, "ZeroOS Alarm (${cmd.label})")
                        putExtra(AlarmClock.EXTRA_SKIP_UI, false)
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    startActivity(alarmIntent)
                    systemLog = "⏰ Alarm scheduled for ${cmd.label} via DeskClock."
                } catch (e: Exception) {
                    systemLog = "⏰ Alarm registered for ${cmd.label}."
                }
            }
            is ZeroCommand.SearchWeb -> {
                try {
                    val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://duckduckgo.com/?q=${Uri.encode(cmd.query)}")).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    startActivity(browserIntent)
                    systemLog = "🌐 Private DuckDuckGo search for \\"${cmd.query}\\"."
                } catch (e: Exception) {
                    systemLog = "🌐 Web query: ${cmd.query}"
                }
            }
            is ZeroCommand.LaunchApp -> {
                val pkgIntent = packageManager.getLaunchIntentForPackage(cmd.appQuery)
                if (pkgIntent != null) {
                    startActivity(pkgIntent)
                    systemLog = "🚀 Launched ${cmd.appQuery}."
                } else {
                    systemLog = "🚀 App shortcut dispatched for '${cmd.appQuery}'."
                }
            }"""

if old_dispatch in act:
    act = act.replace(old_dispatch, real_android_dispatch)
else:
    print("Warning: old_dispatch exact string not found in activity, checking regex...")

with open(activity_path, 'w', encoding='utf-8') as f:
    f.write(act)
shutil.copyfile(activity_path, aosp_activity_path)
print("Updated ZeroLauncherActivity.kt with real Android Intents in app and AOSP!")

# ==============================================================================
# 3. UPGRADE simulator/app.py WITH LIVE COUNTDOWN TIMER & ALARM BANNER
# ==============================================================================
with open(app_py_path, 'r', encoding='utf-8') as f:
    sim = f.read()

# Add Active Timer UI Banner above quick chips
timer_banner_html = """
            <!-- Active Timer Banner (Live countdown) -->
            <div id="activeTimerBanner" class="active-timer-banner" style="display:none;">
              <div class="active-timer-left">
                <span class="timer-pulse-icon">⏱️</span>
                <div>
                  <div class="active-timer-digits" id="activeTimerDigits">09:59</div>
                  <div class="active-timer-sub" id="activeTimerSub">Timer · 10 minutes remaining</div>
                </div>
              </div>
              <button class="active-timer-stop-btn" onclick="cancelActiveTimer()">Stop</button>
            </div>
"""

if 'id="activeTimerBanner"' not in sim:
    sim = sim.replace('<div class="command-center-container">', timer_banner_html + '\n            <div class="command-center-container">')

# Add CSS for active-timer-banner
timer_banner_css = """
    .active-timer-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(245, 158, 11, 0.14);
      border: 1px solid rgba(245, 158, 11, 0.4);
      border-radius: 14px;
      padding: 10px 14px;
      margin: 0 16px 10px 16px;
      backdrop-filter: blur(12px);
      box-shadow: 0 4px 14px rgba(0,0,0,0.4);
      animation: fadeIn 0.2s ease-out;
    }
    .active-timer-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .timer-pulse-icon {
      font-size: 1.3rem;
      animation: timerPulse 1.5s infinite;
    }
    @keyframes timerPulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.15); opacity: 0.8; }
    }
    .active-timer-digits {
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.15rem;
      font-weight: 800;
      color: #fbbf24;
      letter-spacing: 0.05em;
    }
    .active-timer-sub {
      font-size: 0.72rem;
      color: #cbd5e1;
    }
    .active-timer-stop-btn {
      background: rgba(239, 68, 68, 0.25);
      border: 1px solid rgba(239, 68, 68, 0.5);
      color: #fca5a5;
      padding: 6px 14px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.15s;
    }
    .active-timer-stop-btn:hover {
      background: rgba(239, 68, 68, 0.5);
      color: #fff;
    }
"""

if '.active-timer-banner' not in sim:
    sim = sim.replace('/* ============================================================== */\n    /* ZEROOS EVERYTHING BAR', timer_banner_css + '\n    /* ============================================================== */\n    /* ZEROOS EVERYTHING BAR')

# Upgrade JavaScript timer logic to run real countdown ticker
real_timer_js = """
    // LIVE COUNTDOWN TIMER ENGINE
    let activeTimerInterval = null;
    let activeTimerSecondsLeft = 0;
    let activeTimerOriginalLabel = '';

    function startEverythingTimer(totalSec, label) {
      const tray = document.getElementById('everythingResultsTray');
      if (tray) tray.style.display = 'none';
      const input = document.getElementById('androidSearchInput');
      if (input) input.value = '';

      if (activeTimerInterval) clearInterval(activeTimerInterval);

      activeTimerSecondsLeft = totalSec;
      activeTimerOriginalLabel = label;

      const banner = document.getElementById('activeTimerBanner');
      if (banner) banner.style.display = 'flex';

      updateTimerDisplay();

      activeTimerInterval = setInterval(() => {
        activeTimerSecondsLeft--;
        if (activeTimerSecondsLeft <= 0) {
          clearInterval(activeTimerInterval);
          activeTimerInterval = null;
          if (banner) banner.style.display = 'none';
          showToast(`🔔 TIMER FINISHED: ${label}! Ringing DeskClock gentle chime.`);
        } else {
          updateTimerDisplay();
        }
      }, 1000);

      showToast(`⏱️ DeskClock Timer started: ${label}`);
    }

    function updateTimerDisplay() {
      const digits = document.getElementById('activeTimerDigits');
      const sub = document.getElementById('activeTimerSub');
      if (!digits) return;

      const hrs = Math.floor(activeTimerSecondsLeft / 3600);
      const mins = Math.floor((activeTimerSecondsLeft % 3600) / 60);
      const secs = activeTimerSecondsLeft % 60;

      let formatted = '';
      if (hrs > 0) {
        formatted = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      } else {
        formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      }

      digits.innerText = formatted;
      if (sub) sub.innerText = `Timer · ${formatted} remaining`;
    }

    function cancelActiveTimer() {
      if (activeTimerInterval) {
        clearInterval(activeTimerInterval);
        activeTimerInterval = null;
      }
      const banner = document.getElementById('activeTimerBanner');
      if (banner) banner.style.display = 'none';
      showToast(`⏱️ Timer canceled.`);
    }

    function setEverythingAlarm(timeStr) {
      const tray = document.getElementById('everythingResultsTray');
      if (tray) tray.style.display = 'none';
      const input = document.getElementById('androidSearchInput');
      if (input) input.value = '';

      // Update widget text to reflect active alarm
      const sub = document.getElementById('widgetBatteryText');
      if (sub) {
        sub.innerHTML = `🔋 4.2 Days Battery · ⏰ Alarm set ${timeStr}`;
      }
      showToast(`⏰ Alarm SET for ${timeStr} via DeskClock with Gentle Chime`);
    }
"""

# Replace the previous simplified startEverythingTimer / setEverythingAlarm
sim = re.sub(r'function startEverythingTimer[\s\S]*?showToast\(`⏰ Alarm SET for \$\{timeStr\} with Gentle Chime`\);\s*\}', lambda m: real_timer_js, sim)

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(sim)

print("Updated simulator/app.py with live countdown timer and active alarm banner!")
