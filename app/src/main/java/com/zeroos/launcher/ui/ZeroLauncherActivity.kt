package com.zeroos.launcher.ui

import android.os.Bundle
import android.view.KeyEvent
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.zeroos.launcher.core.*
import com.zeroos.launcher.ui.components.*
import com.zeroos.launcher.ui.theme.*
import java.text.SimpleDateFormat
import java.util.*

class ZeroLauncherActivity : ComponentActivity() {

    private lateinit var hardwareController: HardwareController

    // System UI State
    private var pendingAction by mutableStateOf<PendingConfirmation?>(null)
    private var isMicroWindowMode by mutableStateOf(false)
    private var isNotificationShadeOpen by mutableStateOf(false)
    private var activeAppView by mutableStateOf<String?>(null) // null = Home, "phone", "messages"
    private var activeCallContact by mutableStateOf<Pair<String, String>?>(null)
    private var commandInput by mutableStateOf("")
    private var systemLog by mutableStateOf<String?>(null)

    // Hardware State
    private var isWifiOn by mutableStateOf(true)
    private var wifiSsid by mutableStateOf("Home-5G")
    private var isBluetoothOn by mutableStateOf(true)
    private var bluetoothDevice by mutableStateOf("WH-1000XM5")
    private var soundMode by mutableStateOf("sound") // "sound", "vibrate", "silent"
    private var brightness by mutableStateOf(0.85f)
    private var volume by mutableStateOf(0.70f)
    private var isHotspotOn by mutableStateOf(false)

    // Installed demo apps with privacy shield tracking
    private val appShields = mutableStateMapOf(
        "Instagram" to AppState("Instagram", "com.instagram.android", isDataCut = false, isMicMuted = false, isCamKilled = false, isFrozen = false, trackersBlocked = 42),
        "TikTok" to AppState("TikTok", "com.zhiliaoapp.musically", isDataCut = false, isMicMuted = false, isCamKilled = false, isFrozen = false, trackersBlocked = 68),
        "WhatsApp" to AppState("WhatsApp", "com.whatsapp", isDataCut = false, isMicMuted = false, isCamKilled = false, isFrozen = false, trackersBlocked = 14),
        "YouTube" to AppState("YouTube", "com.google.android.youtube", isDataCut = false, isMicMuted = false, isCamKilled = false, isFrozen = false, trackersBlocked = 31),
        "Monzo Banking" to AppState("Monzo Banking", "co.uk.getmondo", isDataCut = false, isMicMuted = false, isCamKilled = false, isFrozen = false, trackersBlocked = 0)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        hardwareController = HardwareController(this)

        setContent {
            ZeroTheme {
                val timeString = remember { SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date()) }

                Box(modifier = Modifier.fillMaxSize()) {
                    if (isMicroWindowMode) {
                        MicroDisplayOverlay(
                            currentTime = timeString,
                            batteryPercent = 88,
                            isGrayscale = hardwareController.isGrayscaleActive(),
                            onExpandFullDisplay = { isMicroWindowMode = false }
                        ) {
                            TerminalInputRow(
                                input = commandInput,
                                onValueChange = { commandInput = it },
                                onExecute = { executeCommand(commandInput) }
                            )
                        }
                    } else if (activeCallContact != null) {
                        InCallScreen(
                            contactName = activeCallContact!!.first,
                            contactNumber = activeCallContact!!.second,
                            onEndCall = { activeCallContact = null },
                            onToast = { showToast(it) }
                        )
                    } else if (activeAppView == "messages") {
                        ZeroMessagesView(onToast = { showToast(it) })
                    } else {
                        MainLauncherScreen(
                            currentTime = timeString,
                            commandInput = commandInput,
                            onInputChange = { commandInput = it },
                            onExecuteCommand = { executeCommand(it) },
                            appShields = appShields.values.toList(),
                            pendingAction = pendingAction,
                            systemLog = systemLog,
                            onOpenShade = { isNotificationShadeOpen = true },
                            onConfirmAction = {
                                pendingAction?.action?.invoke()
                                pendingAction = null
                            },
                            onDismissAction = { pendingAction = null },
                            onToggleData = { app -> toggleDataShield(app) },
                            onToggleMic = { app -> toggleMicShield(app) },
                            onToggleCam = { app -> toggleCamShield(app) },
                            onToggleFreeze = { app -> toggleFreezeShield(app) }
                        )
                    }

                    // Pull-Down Notification Shade & Quick Settings Overlay
                    NotificationShadeOverlay(
                        isOpen = isNotificationShadeOpen,
                        currentTime = timeString,
                        batteryPercent = 88,
                        batteryDaysRemaining = 4.2f,
                        isWifiOn = isWifiOn,
                        wifiSsid = wifiSsid,
                        isBluetoothOn = isBluetoothOn,
                        bluetoothDevice = bluetoothDevice,
                        soundMode = soundMode,
                        isTorchOn = hardwareController.isFlashlightOn,
                        isHotspotOn = isHotspotOn,
                        isGrayscaleOn = hardwareController.isGrayscaleActive(),
                        isAirGapActive = true,
                        isDiaModeOn = false,
                        brightness = brightness,
                        volume = volume,
                        onBrightnessChange = { brightness = it },
                        onVolumeChange = { volume = it },
                        onToggleWifi = {
                            isWifiOn = !isWifiOn
                            showToast(if (isWifiOn) "📶 Wi-Fi connected to $wifiSsid" else "📶 Wi-Fi disconnected")
                        },
                        onToggleBluetooth = {
                            isBluetoothOn = !isBluetoothOn
                            showToast(if (isBluetoothOn) "ᛒ Bluetooth connected to $bluetoothDevice" else "ᛒ Bluetooth OFF")
                        },
                        onCycleSoundMode = {
                            soundMode = when (soundMode) {
                                "sound" -> "vibrate"
                                "vibrate" -> "silent"
                                else -> "sound"
                            }
                            showToast("🔔 Sound mode: ${soundMode.replaceFirstChar { it.uppercase() }}")
                        },
                        onToggleTorch = {
                            hardwareController.setFlashlight(!hardwareController.isFlashlightOn)
                        },
                        onToggleHotspot = {
                            isHotspotOn = !isHotspotOn
                            showToast(if (isHotspotOn) "(((•))) Hotspot ACTIVE: Broadcasting ZeroPhone-5G" else "(((•))) Hotspot OFF")
                        },
                        onToggleGrayscale = {
                            hardwareController.toggleGrayscale()
                        },
                        onToggleAirGap = {
                            showToast("🛡️ Auto Air-Gap policy is ACTIVE (Zero background data leakage)")
                        },
                        onToggleDiaMode = {
                            showToast("🔋 DIA Mode toggled (Deep-Idle Architecture · 5.8 Days)")
                        },
                        onCloseShade = { isNotificationShadeOpen = false }
                    )
                }
            }
        }
    }

    /**
     * Intercepts hardware power button long-press or assistant key
     * to open the Zero Terminal instantly from anywhere.
     */
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_VOICE_ASSIST || keyCode == KeyEvent.KEYCODE_ASSIST) {
            commandInput = "/"
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    private fun showToast(msg: String) {
        android.widget.Toast.makeText(this, msg, android.widget.Toast.LENGTH_SHORT).show()
    }

    private fun executeCommand(input: String) {
        val cmd = CommandParser.parse(input)
        commandInput = ""

        when (cmd) {
            is ZeroCommand.ToggleFlashlight -> {
                val success = hardwareController.setFlashlight(cmd.enable)
                systemLog = if (cmd.enable) "🔦 Flashlight turned ON." else "🔦 Flashlight turned OFF."
            }
            is ZeroCommand.ToggleHotspot -> {
                val success = hardwareController.setHotspot(cmd.enable)
                systemLog = if (cmd.enable) "(((•))) Hotspot ACTIVE: Broadcasting 'ZeroPhone-5G'." else "(((•))) Hotspot turned OFF."
            }
            is ZeroCommand.RequestGrayscale -> {
                pendingAction = PendingConfirmation(
                    title = if (cmd.enable) "Enable Grayscale Mode?" else "Disable Grayscale Mode?",
                    bullets = listOf(
                        "Converts all screen pixels to monochrome black & white.",
                        "Eliminates visual dopamine triggers & digital addiction.",
                        "Saves up to 18% OLED battery power."
                    ),
                    action = {
                        hardwareController.setGrayscale(cmd.enable)
                        systemLog = "⚡ Grayscale display mode updated."
                    }
                )
            }
            is ZeroCommand.RequestReboot -> {
                pendingAction = PendingConfirmation(
                    title = "Reboot Device Now?",
                    bullets = listOf(
                        "Restarts the Linux kernel and ZeroOS framework.",
                        "Clears all volatile RAM buffers.",
                        "Device will be back online in ~25 seconds."
                    ),
                    action = { hardwareController.rebootSystem("ZeroOS User Request") }
                )
            }
            is ZeroCommand.RequestDiaMode -> {
                pendingAction = PendingConfirmation(
                    title = "Activate Nokia 4-Day Battery Mode?",
                    bullets = listOf(
                        "Puts phone CPU into deep Linux C-states (extreme sleep).",
                        "Kills all background social media sync & ad telemetry.",
                        "Incoming cellular voice calls and SMS still work 100%.",
                        "Battery longevity extends to 4–6 days."
                    ),
                    action = {
                        hardwareController.setGrayscale(true)
                        isMicroWindowMode = true
                        systemLog = "🔋 Nokia Deep Sleep Mode ACTIVE. Screen throttled to 1Hz."
                    }
                )
            }
            is ZeroCommand.ToggleMicroWindow -> {
                isMicroWindowMode = cmd.enable
                systemLog = if (cmd.enable) "⚡ OLED Micro-Window Mode: 80% screen powered off." else "OLED Full Display Restored."
            }
            is ZeroCommand.CutMobileData -> {
                val targets = cmd.targetApps.ifEmpty { listOf("all") }
                targets.forEach { target ->
                    val app = appShields.values.firstOrNull { it.name.lowercase().contains(target) }
                    if (app != null) {
                        appShields[app.name] = app.copy(isDataCut = true)
                    }
                }
                systemLog = "⚡ Network packets dropped via iptables for: ${targets.joinToString()}"
            }
            is ZeroCommand.RestoreMobileData -> {
                cmd.targetApps.forEach { target ->
                    val app = appShields.values.firstOrNull { it.name.lowercase().contains(target) }
                    if (app != null) {
                        appShields[app.name] = app.copy(isDataCut = false)
                    }
                }
                systemLog = "📶 Mobile & Wi-Fi restored for: ${cmd.targetApps.joinToString()}"
            }
            is ZeroCommand.UnmuteMicrophone -> {
                cmd.targetApps.forEach { appName ->
                    appShields[appName]?.let { app ->
                        app.isMicMuted = false
                        SingleSessionPermissionManager.setMicHardMuted(app.packageName, false)
                    }
                }
                systemLog = "🎙️ Microphone UNMUTED: Restored to automatic single-session for: ${cmd.targetApps.joinToString()}."
            }
            is ZeroCommand.MuteMicrophone -> {
                cmd.targetApps.forEach { target ->
                    val app = appShields.values.firstOrNull { it.name.lowercase().contains(target) }
                    if (app != null) {
                        appShields[app.name] = app.copy(isMicMuted = true)
                    }
                }
                systemLog = "🎙️ Microphone hardware register LOCKED for: ${cmd.targetApps.joinToString()}. Audio feeds dead silence."
            }
            is ZeroCommand.KillCamera -> {
                cmd.targetApps.forEach { target ->
                    val app = appShields.values.firstOrNull { it.name.lowercase().contains(target) }
                    if (app != null) {
                        appShields[app.name] = app.copy(isCamKilled = true)
                    }
                }
                systemLog = "📷 Camera hardware register LOCKED for: ${cmd.targetApps.joinToString()}."
            }
            is ZeroCommand.FreezeApp -> {
                cmd.targetApps.forEach { target ->
                    val app = appShields.values.firstOrNull { it.name.lowercase().contains(target) }
                    if (app != null) {
                        appShields[app.name] = app.copy(isFrozen = true)
                    }
                }
                systemLog = "🧊 ${cmd.targetApps.joinToString()} placed into system hibernation (0% CPU)."
            }
            is ZeroCommand.AuditSpying -> {
                systemLog = "🛡️ Audit: 42 Meta background sockets blocked. Mic hardware register: SECURED. 0 active leaks."
            }
            is ZeroCommand.ShowAboutPhone -> {
                val info = hardwareController.getHardwareSummary()
                systemLog = info.entries.joinToString("\n") { "• ${it.key}: ${it.value}" }
            }
            is ZeroCommand.LaunchApp -> {
                systemLog = "🚀 Launching '${cmd.appQuery}'..."
            }
            is ZeroCommand.Unknown -> {
                systemLog = "Command not recognized. Type '/' for quick shortcuts."
            }
        }
    }

    private fun toggleDataShield(app: AppState) {
        val updated = !app.isDataCut
        appShields[app.name] = app.copy(isDataCut = updated)
        systemLog = if (updated) "⚡ Mobile data SEVERED for ${app.name} via iptables." else "📶 Mobile data RESTORED for ${app.name}."
    }

    private fun toggleMicShield(app: AppState) {
        val updated = !app.isMicMuted
        appShields[app.name] = app.copy(isMicMuted = updated)
        systemLog = if (updated) "🎙️ Microphone LOCKED for ${app.name}." else "🎙️ Microphone unmuted for ${app.name}."
    }

    private fun toggleCamShield(app: AppState) {
        val updated = !app.isCamKilled
        appShields[app.name] = app.copy(isCamKilled = updated)
        systemLog = if (updated) "📷 Camera LOCKED for ${app.name}." else "📷 Camera unlocked for ${app.name}."
    }

    private fun toggleFreezeShield(app: AppState) {
        val updated = !app.isFrozen
        appShields[app.name] = app.copy(isFrozen = updated)
        systemLog = if (updated) "🧊 ${app.name} suspended (0% CPU)." else "⚡ ${app.name} unsuspended."
    }
}

data class AppState(
    val name: String,
    val packageName: String,
    val isDataCut: Boolean,
    val isMicMuted: Boolean,
    val isCamKilled: Boolean,
    val isFrozen: Boolean,
    val trackersBlocked: Int
)

data class PendingConfirmation(
    val title: String,
    val bullets: List<String>,
    val action: () -> Unit
)

@Composable
fun MainLauncherScreen(
    currentTime: String,
    commandInput: String,
    onInputChange: (String) -> Unit,
    onExecuteCommand: (String) -> Unit,
    appShields: List<AppState>,
    pendingAction: PendingConfirmation?,
    systemLog: String?,
    onOpenShade: () -> Unit,
    onConfirmAction: () -> Unit,
    onDismissAction: () -> Unit,
    onToggleData: (AppState) -> Unit,
    onToggleMic: (AppState) -> Unit,
    onToggleCam: (AppState) -> Unit,
    onToggleFreeze: (AppState) -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(OledBlack)
            .padding(horizontal = 20.dp, vertical = 24.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // TOP STATUS & MINIMALIST CLOCK
            Column {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onOpenShade() },
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "ZERO·OS",
                        color = AmberAccent,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 2.sp
                    )
                    Text(
                        text = "🔋 88% · 4 DAYS REMAINING",
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }

                Spacer(modifier = Modifier.height(18.dp))

                Text(
                    text = currentTime,
                    color = TextPrimary,
                    fontSize = 54.sp,
                    fontWeight = FontWeight.Light,
                    letterSpacing = (-2).sp
                )
                Text(
                    text = "Thursday, 29 October · Silent Shield Active",
                    color = TextMuted,
                    fontSize = 13.sp
                )
            }

            // MIDDLE SCROLLABLE FEED: LOGS, CONFIRMATION DIALOG, OR PRIVACY SHIELDS
            Box(modifier = Modifier.weight(1f).padding(vertical = 12.dp)) {
                if (pendingAction != null) {
                    ConfirmationCard(
                        title = pendingAction.title,
                        bulletPoints = pendingAction.bullets,
                        onConfirm = onConfirmAction,
                        onDismiss = onDismissAction
                    )
                } else {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        if (systemLog != null) {
                            item {
                                Surface(
                                    color = SurfaceCard,
                                    shape = RoundedCornerShape(8.dp),
                                    modifier = Modifier.fillMaxWidth().border(1.dp, AmberMuted, RoundedCornerShape(8.dp))
                                ) {
                                    Text(
                                        text = systemLog,
                                        color = AmberAccent,
                                        fontSize = 12.sp,
                                        fontFamily = FontFamily.Monospace,
                                        modifier = Modifier.padding(12.dp)
                                    )
                                }
                            }
                        }

                        // App Privacy Cards
                        items(appShields) { app ->
                            PrivacyActionCard(
                                appName = app.name,
                                packageName = app.packageName,
                                isDataCut = app.isDataCut,
                                isMicMuted = app.isMicMuted,
                                isCamKilled = app.isCamKilled,
                                isFrozen = app.isFrozen,
                                blockedTrackersCount = app.trackersBlocked,
                                onToggleData = { onToggleData(app) },
                                onToggleMic = { onToggleMic(app) },
                                onToggleCam = { onToggleCam(app) },
                                onToggleFreeze = { onToggleFreeze(app) },
                                onLaunch = { onExecuteCommand(app.name) }
                            )
                        }
                    }
                }
            }

            // BOTTOM UNIVERSAL TERMINAL & CHIPS
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                // Autocomplete Shortcut Chips
                LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    val chips = listOf(
                        "⚡ /cut-data instagram" to "cut data for instagram",
                        "🎙️ /mute-mic" to "mute mic for whatsapp, instagram",
                        "🧊 /freeze tiktok" to "freeze tiktok",
                        "🔦 Flashlight" to "turn on flash",
                        "🌓 Grayscale" to "turn on grayscale",
                        "🔋 DIA Mode" to "dia mode",
                        "👁️ /spy-audit" to "who is spying?",
                        "📱 About Phone" to "about phone",
                        "🔄 Restart" to "restart"
                    )
                    items(chips) { (label, cmd) ->
                        Surface(
                            color = SurfaceDark,
                            shape = RoundedCornerShape(20.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, BorderSubtle),
                            modifier = Modifier.clickable { onExecuteCommand(cmd) }
                        ) {
                            Text(
                                text = label,
                                color = TextMuted,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace,
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                            )
                        }
                    }
                }

                // Main Command Input Bar
                TerminalInputRow(
                    input = commandInput,
                    onValueChange = onInputChange,
                    onExecute = { onExecuteCommand(commandInput) }
                )
            }
        }
    }
}

@Composable
fun TerminalInputRow(
    input: String,
    onValueChange: (String) -> Unit,
    onExecute: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(SurfaceDark, RoundedCornerShape(12.dp))
            .border(1.dp, AmberMuted, RoundedCornerShape(12.dp))
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "> ",
            color = AmberAccent,
            fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Monospace,
            fontSize = 16.sp
        )
        BasicTextField(
            value = input,
            onValueChange = onValueChange,
            textStyle = TextStyle(
                color = TextPrimary,
                fontSize = 14.sp,
                fontFamily = FontFamily.Monospace
            ),
            singleLine = true,
            cursorBrush = SolidColor(AmberAccent),
            modifier = Modifier.weight(1f),
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
            keyboardActions = KeyboardActions(onSend = { onExecute() }),
            decorationBox = { innerTextField ->
                if (input.isEmpty()) {
                    Text(
                        text = "Type command (e.g. 'cut data for instagram', 'turn on flash', 'grayscale')...",
                        color = TextMuted.copy(alpha = 0.5f),
                        fontSize = 13.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }
                innerTextField()
            }
        )
    }
}
