package com.zeroos.launcher.core

import java.util.Locale

/**
 * Data model for parsed user intents in ZeroOS.
 */
sealed class ZeroCommand {
    data class ToggleFlashlight(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class ToggleHotspot(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class RequestGrayscale(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class RequestReboot(val immediate: Boolean = false) : ZeroCommand()
    data class RequestNokiaMode(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class CutMobileData(val targetApps: List<String>) : ZeroCommand()
    data class RestoreMobileData(val targetApps: List<String>) : ZeroCommand()
    data class MuteMicrophone(val targetApps: List<String>) : ZeroCommand()
    data class KillCamera(val targetApps: List<String>) : ZeroCommand()
    data class FreezeApp(val targetApps: List<String>) : ZeroCommand()
    data class UnfreezeApp(val targetApps: List<String>) : ZeroCommand()
    data class ToggleMicroWindow(val enable: Boolean) : ZeroCommand()
    data class ToggleCalmDigest(val explicitEnable: Boolean? = null) : ZeroCommand()
    data class LaunchEphemeralApp(val appQuery: String) : ZeroCommand()
    object ShowImpactDashboard : ZeroCommand()
    object AuditSpying : ZeroCommand()
    object ShowAboutPhone : ZeroCommand()
    data class LaunchApp(val appQuery: String) : ZeroCommand()
    data class Unknown(val rawText: String) : ZeroCommand()
}

/**
 * High-performance on-device natural language intent parser.
 * Executes in sub-millisecond time with zero external network dependencies.
 */
object CommandParser {

    private val APP_SPLIT_REGEX = Regex("[,&]|\\band\\b", RegexOption.IGNORE_CASE)

    fun parse(rawInput: String): ZeroCommand {
        val text = rawInput.trim()
        val lower = text.lowercase(Locale.ROOT)

        if (lower.isEmpty()) return ZeroCommand.Unknown("")

        // 1. HARDWARE: FLASHLIGHT / TORCH
        if (lower.contains("flashlight") || lower.contains("torch") || lower.contains("flash")) {
            val explicit = if (lower.contains("off") || lower.contains("stop") || lower.contains("disable")) false
                           else if (lower.contains("on") || lower.contains("start") || lower.contains("enable")) true
                           else null
            return ZeroCommand.ToggleFlashlight(explicit)
        }

        // 1b. HARDWARE: WI-FI HOTSPOT / TETHERING
        if (lower.contains("hotspot") || lower.contains("tethering") || lower.contains("tether") || lower == "/hotspot") {
            val explicit = if (lower.contains("off") || lower.contains("stop") || lower.contains("disable")) false
                           else if (lower.contains("on") || lower.contains("start") || lower.contains("enable")) true
                           else null
            return ZeroCommand.ToggleHotspot(explicit)
        }

        // 2. HARDWARE: GRAYSCALE (Triggers Confirmation Dialog)
        if (lower.contains("grayscale") || lower.contains("monochrome") || lower.contains("black and white")) {
            val explicit = if (lower.contains("off") || lower.contains("disable") || lower.contains("exit")) false
                           else if (lower.contains("on") || lower.contains("enable")) true
                           else null
            return ZeroCommand.RequestGrayscale(explicit)
        }

        // 3. HARDWARE: RESTART / REBOOT
        if (lower.contains("restart") || lower.contains("reboot") || lower == "/reboot") {
            return ZeroCommand.RequestReboot(immediate = false)
        }

        // 4. BATTERY: NOKIA MODE / DEEP SLEEP
        if (lower.contains("nokia") || lower.contains("deep sleep") || lower == "/nokia-mode") {
            val explicit = if (lower.contains("off") || lower.contains("exit") || lower.contains("disable")) false
                           else if (lower.contains("on") || lower.contains("enable")) true
                           else null
            return ZeroCommand.RequestNokiaMode(explicit)
        }

        // 5. DISPLAY: MICRO-WINDOW / 0W SUB-DISPLAY
        if (lower.contains("micro window") || lower.contains("sub display") || lower.contains("mini screen") || lower == "/micro") {
            val isOff = lower.contains("off") || lower.contains("exit") || lower.contains("full")
            return ZeroCommand.ToggleMicroWindow(!isOff)
        }

        // 6. PRIVACY: WHO IS SPYING / TRACKER AUDIT
        if (lower.contains("who is spying") || lower.contains("spy audit") || lower.contains("trackers") || lower == "/spy-audit") {
            return ZeroCommand.AuditSpying
        }

        // 7. SYSTEM: ABOUT PHONE
        if (lower.contains("about phone") || lower.contains("system info") || lower == "/about") {
            return ZeroCommand.ShowAboutPhone
        }

        // 7b. PRIVACY & BATTERY: IMPACT DASHBOARD / STATS
        if (lower.contains("impact") || lower.contains("stats") || lower.contains("dashboard") || lower.contains("privacy score") || lower == "/stats") {
            return ZeroCommand.ShowImpactDashboard
        }

        // 7c. ATTENTION: CALM DIGEST
        if (lower.contains("calm digest") || lower.contains("digest") || lower.contains("calm mode") || lower == "/digest") {
            val explicit = if (lower.contains("off") || lower.contains("disable") || lower.contains("stop")) false
                           else if (lower.contains("on") || lower.contains("enable")) true
                           else null
            return ZeroCommand.ToggleCalmDigest(explicit)
        }

        // 7d. SANDBOX: EPHEMERAL APP LAUNCH
        if (lower.startsWith("ephemeral") || lower.startsWith("disposable") || lower.startsWith("temp app") || lower.startsWith("/ephemeral")) {
            val target = lower.replace(Regex("^(ephemeral|disposable|temp app|/ephemeral)\\s*"), "").trim()
            return ZeroCommand.LaunchEphemeralApp(target)
        }

        // 8. KERNEL FIREWALL: CUT / RESTORE MOBILE DATA
        if (lower.contains("cut data") || lower.contains("block data") || lower.contains("kill data") || lower.contains("no internet") || lower.startsWith("/cut-data")) {
            val apps = extractAppTargets(lower, listOf("cut data for", "cut data to", "block data for", "block data to", "kill data for", "no internet for", "/cut-data"))
            return ZeroCommand.CutMobileData(apps)
        }
        if (lower.contains("restore data") || lower.contains("allow data") || lower.contains("unblock data")) {
            val apps = extractAppTargets(lower, listOf("restore data for", "restore data to", "allow data for", "unblock data for"))
            return ZeroCommand.RestoreMobileData(apps)
        }

        // 9. SENSOR: MUTE / CUT MICROPHONE
        if (lower.contains("cut mic") || lower.contains("mute mic") || lower.contains("kill mic") || lower.contains("block mic") || lower.contains("cut audio") || lower.contains("mute audio") || lower.contains("cut microphone") || lower.startsWith("/mute-mic")) {
            val apps = extractAppTargets(lower, listOf("cut mic for", "cut mic to", "mute mic for", "kill mic for", "block mic for", "cut microphone for", "mute audio for", "/mute-mic"))
            return ZeroCommand.MuteMicrophone(apps)
        }

        // 10. SENSOR: KILL CAMERA
        if (lower.contains("kill camera") || lower.contains("block camera") || lower.contains("mute camera") || lower.startsWith("/kill-cam")) {
            val apps = extractAppTargets(lower, listOf("kill camera for", "block camera for", "mute camera for", "/kill-cam"))
            return ZeroCommand.KillCamera(apps)
        }

        // 11. HIBERNATION: FREEZE / UNFREEZE APP
        if (lower.contains("freeze") || lower.contains("hibernate") || lower.startsWith("/freeze")) {
            val apps = extractAppTargets(lower, listOf("freeze app", "freeze", "hibernate", "/freeze"))
            return ZeroCommand.FreezeApp(apps)
        }
        if (lower.contains("unfreeze") || lower.contains("wake up app") || lower.startsWith("/unfreeze")) {
            val apps = extractAppTargets(lower, listOf("unfreeze", "wake up app", "/unfreeze"))
            return ZeroCommand.UnfreezeApp(apps)
        }

        // 12. FALLBACK: APP LAUNCHER
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
        if (lowerClean.contains("social")) {
            return SOCIAL_APPS
        }
        if (lowerClean == "all" || lowerClean.contains("all app") || lowerClean.contains("everywhere") || lowerClean.contains("every app")) {
            return ALL_APPS
        }

        // Clean out words like "apps", "app"
        clean = clean.replace(Regex("\\bapps?\\b"), "").trim()

        val parsed = clean.split(APP_SPLIT_REGEX)
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        return if (parsed.isEmpty()) listOf("whatsapp") else parsed
    }
}
