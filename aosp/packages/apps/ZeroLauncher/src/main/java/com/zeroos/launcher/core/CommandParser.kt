package com.zeroos.launcher.core

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

    private val APP_SPLIT_REGEX = Regex("[,&]|\\band\\b", RegexOption.IGNORE_CASE)

    fun parse(rawInput: String): ZeroCommand {
        val text = rawInput.trim()
        val lower = text.lowercase(Locale.ROOT)

        if (lower.isEmpty()) return ZeroCommand.Unknown("")

        // 0. DIRECTIONS & OFFLINE ROUTING (/direction destination OR /direction origin to destination)
        if (lower.startsWith("/direction") || lower.startsWith("direction") || lower.startsWith("/route") || lower.startsWith("navigate to")) {
            val query = text.replace(Regex("^(/direction|direction|/route|navigate to)", RegexOption.IGNORE_CASE), "").trim()
            if (query.isNotEmpty()) {
                if (query.contains(" to ", ignoreCase = true)) {
                    val parts = query.split(Regex("\\bto\\b", RegexOption.IGNORE_CASE))
                    return ZeroCommand.RequestDirections(origin = parts[0].trim(), destination = parts[1].trim())
                } else {
                    return ZeroCommand.RequestDirections(origin = null, destination = query)
                }
            }
        }

        // 1. EVERYTHING BAR: TIMER (supports seconds, minutes, hours)
        val timerMatch = Regex("^(?:set\\s+)?timer(?:\\s+for)?\\s+(\\d+)\\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|h|hr|hrs|hour|hours)?$", RegexOption.IGNORE_CASE).find(lower)
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
        val alarmMatch = Regex("^(?:set\\s+)?alarm(?:\\s+for)?\\s+(\\d{1,2})(?::(\\d{2}))?\\s*(am|pm)?$", RegexOption.IGNORE_CASE).find(lower)
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
        if (Regex("\\b(flashlight|torch)\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/torch") {
            val explicit = if (Regex("\\b(off|stop|disable)\\b").containsMatchIn(lower)) false
                           else if (Regex("\\b(on|start|enable)\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.ToggleFlashlight(explicit)
        }

        // 4. HARDWARE: WI-FI HOTSPOT / TETHERING
        if (Regex("\\b(hotspot|tethering|tether)\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/hotspot") {
            val explicit = if (Regex("\\b(off|stop|disable)\\b").containsMatchIn(lower)) false
                           else if (Regex("\\b(on|start|enable)\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.ToggleHotspot(explicit)
        }

        // 5. HARDWARE: GRAYSCALE
        if (Regex("\\b(grayscale|monochrome|black\\s+and\\s+white)\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower)) {
            val explicit = if (Regex("\\b(off|disable|exit)\\b").containsMatchIn(lower)) false
                           else if (Regex("\\b(on|enable)\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.RequestGrayscale(explicit)
        }

        // 6. HARDWARE: RESTART / REBOOT
        if (Regex("\\b(restart|reboot)\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/reboot") {
            return ZeroCommand.RequestReboot(immediate = false)
        }

        // 7. BATTERY: NOKIA MODE / DIA MODE (Guarded with word boundary - prevents "India" trigger)
        if (Regex("\\b(dia\\s+mode|dia|nokia|deep\\s+sleep)\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/nokia-mode") {
            val explicit = if (Regex("\\b(off|exit|disable)\\b").containsMatchIn(lower)) false
                           else if (Regex("\\b(on|enable)\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.RequestDiaMode(explicit)
        }

        // 8. DISPLAY: MICRO-WINDOW
        if (Regex("\\b(micro\\s+window|sub\\s+display|mini\\s+screen)\\b", RegexOption.IGNORE_CASE).containsMatchIn(lower) || lower == "/micro") {
            val isOff = Regex("\\b(off|exit|full)\\b").containsMatchIn(lower)
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
            val explicit = if (Regex("\\b(off|disable|stop)\\b").containsMatchIn(lower)) false
                           else if (Regex("\\b(on|enable)\\b").containsMatchIn(lower)) true
                           else null
            return ZeroCommand.ToggleCalmDigest(explicit)
        }

        // 10. SANDBOX: EPHEMERAL APP LAUNCH
        if (lower.startsWith("ephemeral") || lower.startsWith("disposable") || lower.startsWith("temp app") || lower.startsWith("/ephemeral")) {
            val target = lower.replace(Regex("^(ephemeral|disposable|temp app|/ephemeral)\\s*"), "").trim()
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
            val target = text.replace(Regex("^(call|dial)\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (target.isNotEmpty()) return ZeroCommand.CallContact(target)
        }

        // 15. EVERYTHING BAR: MESSAGE / SMS / TEXT
        if (lower.startsWith("message ") || lower.startsWith("text ") || lower.startsWith("msg ")) {
            val remainder = text.replace(Regex("^(message|text|msg)\\s+", RegexOption.IGNORE_CASE), "").trim()
            val spaceIdx = remainder.indexOf(' ')
            return if (spaceIdx != -1) {
                ZeroCommand.MessageContact(remainder.substring(0, spaceIdx).trim(), remainder.substring(spaceIdx + 1).trim())
            } else {
                ZeroCommand.MessageContact(remainder, null)
            }
        }

        // 16. EVERYTHING BAR: ENCRYPTED CHAT (ZEROCHAT)
        if (lower.startsWith("chat ")) {
            val target = text.replace(Regex("^chat\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (target.isNotEmpty()) return ZeroCommand.ChatContact(target)
        }

        // 17. EVERYTHING BAR: ADD / SAVE CONTACT
        if (lower.startsWith("add contact ") || lower.startsWith("save contact ") || lower.startsWith("save ")) {
            val num = text.replace(Regex("^(add contact|save contact|save)\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (num.isNotEmpty()) return ZeroCommand.SaveContact(num)
        }

        // 18. EVERYTHING BAR: WEB SEARCH
        if (lower.startsWith("search ") || lower.startsWith("google ") || lower.startsWith("ddg ")) {
            val query = text.replace(Regex("^(search|google|ddg)\\s+", RegexOption.IGNORE_CASE), "").trim()
            if (query.isNotEmpty()) return ZeroCommand.SearchWeb(query)
        }

        // 19. EVERYTHING BAR: DIRECT MATH EXPRESSIONS (e.g. 245 * 18, 15% of 850)
        if (lower.matches(Regex("^[0-9+\\-*/().\\s^%]+$")) && lower.any { it in "+-*/%^" }) {
            return ZeroCommand.CalculateMath(text)
        }
        if (lower.matches(Regex("^[0-9.]+\\s*%\\s*(?:of)?\\s*[0-9.]+$"))) {
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

        clean = clean.replace(Regex("\\bapps?\\b"), "").trim()
        val parsed = clean.split(APP_SPLIT_REGEX).map { it.trim() }.filter { it.isNotEmpty() }
        return if (parsed.isEmpty()) listOf("whatsapp") else parsed
    }
}
