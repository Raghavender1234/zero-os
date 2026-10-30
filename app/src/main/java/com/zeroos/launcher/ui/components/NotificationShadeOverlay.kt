package com.zeroos.launcher.ui.components

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.zeroos.launcher.ui.theme.*

/**
 * ZeroOS Notification Shade & Quick Settings Overlay
 * 
 * Replaces standard cluttered Android quick settings with:
 * • One UI one-thumb reachability zone
 * • Dual micro-sliders for Brightness & Volume
 * • 4 Everyday Hero Quick Capsules (Wi-Fi, Bluetooth, Sound cycling, Torch)
 * • 4 Secondary Utility Squircles (Hotspot, 0W Mono, Auto Air-Gap, Nokia Mode)
 */
@Composable
fun NotificationShadeOverlay(
    isOpen: Boolean,
    currentTime: String,
    batteryPercent: Int,
    batteryDaysRemaining: Float,
    isWifiOn: Boolean,
    wifiSsid: String,
    isBluetoothOn: Boolean,
    bluetoothDevice: String,
    soundMode: String, // "sound", "vibrate", "silent"
    isTorchOn: Boolean,
    isHotspotOn: Boolean,
    isGrayscaleOn: Boolean,
    isAirGapActive: Boolean,
    isNokiaModeOn: Boolean,
    brightness: Float,
    volume: Float,
    onBrightnessChange: (Float) -> Unit,
    onVolumeChange: (Float) -> Unit,
    onToggleWifi: () -> Unit,
    onToggleBluetooth: () -> Unit,
    onCycleSoundMode: () -> Unit,
    onToggleTorch: () -> Unit,
    onToggleHotspot: () -> Unit,
    onToggleGrayscale: () -> Unit,
    onToggleAirGap: () -> Unit,
    onToggleNokiaMode: () -> Unit,
    onCloseShade: () -> Unit
) {
    AnimatedVisibility(
        visible = isOpen,
        enter = slideInVertically(initialOffsetY = { -it }) + fadeIn(),
        exit = slideOutVertically(targetOffsetY = { -it }) + fadeOut()
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.96f))
                .clickable { onCloseShade() }
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 24.dp)
                    .clickable(enabled = false) {} // Prevent click-through to close
            ) {
                // 1. One UI Reachability Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = currentTime,
                            fontSize = 44.sp,
                            fontWeight = FontWeight.Light,
                            color = Color.White,
                            fontFamily = FontFamily.SansSerif
                        )
                        Text(
                            text = "Wednesday, October 29 · 🔋 $batteryPercent% (${batteryDaysRemaining}d)",
                            fontSize = 12.sp,
                            color = Color(0xFF8E8E93)
                        )
                    }
                    IconButton(
                        onClick = onCloseShade,
                        modifier = Modifier
                            .size(36.dp)
                            .background(Color(0xFF171717), CircleShape)
                            .border(1.dp, Color(0xFF27272A), CircleShape)
                    ) {
                        Text("✕", color = Color.White, fontSize = 14.sp)
                    }
                }

                Spacer(modifier = Modifier.height(18.dp))

                // 2. Dual Precision Sliders: Brightness & Volume
                Card(
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF121212)),
                    border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF27272A))),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        // Brightness Slider
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("☀️", fontSize = 14.sp, modifier = Modifier.width(26.dp))
                            Slider(
                                value = brightness,
                                onValueChange = onBrightnessChange,
                                modifier = Modifier.weight(1f),
                                colors = SliderDefaults.colors(
                                    thumbColor = Color.White,
                                    activeTrackColor = Color.White,
                                    inactiveTrackColor = Color(0xFF27272A)
                                )
                            )
                            Text(
                                text = "${(brightness * 100).toInt()}%",
                                fontSize = 11.sp,
                                color = Color(0xFF8E8E93),
                                fontFamily = FontFamily.Monospace,
                                modifier = Modifier.width(36.dp)
                            )
                        }

                        Spacer(modifier = Modifier.height(4.dp))

                        // Volume Slider
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🔊", fontSize = 14.sp, modifier = Modifier.width(26.dp))
                            Slider(
                                value = volume,
                                onValueChange = onVolumeChange,
                                modifier = Modifier.weight(1f),
                                colors = SliderDefaults.colors(
                                    thumbColor = Color.White,
                                    activeTrackColor = Color.White,
                                    inactiveTrackColor = Color(0xFF27272A)
                                )
                            )
                            Text(
                                text = "${(volume * 100).toInt()}%",
                                fontSize = 11.sp,
                                color = Color(0xFF8E8E93),
                                fontFamily = FontFamily.Monospace,
                                modifier = Modifier.width(36.dp)
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(14.dp))

                // 3. 4 Everyday Hero Quick Capsules
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    // Wi-Fi Capsule
                    HeroTileCapsule(
                        modifier = Modifier.weight(1f),
                        icon = "📶",
                        title = "Wi-Fi",
                        sub = if (isWifiOn) wifiSsid else "Off",
                        isActive = isWifiOn,
                        onClick = onToggleWifi
                    )
                    // Bluetooth Capsule
                    HeroTileCapsule(
                        modifier = Modifier.weight(1f),
                        icon = "ᛒ",
                        title = "Bluetooth",
                        sub = if (isBluetoothOn) bluetoothDevice else "Off",
                        isActive = isBluetoothOn,
                        onClick = onToggleBluetooth
                    )
                }

                Spacer(modifier = Modifier.height(10.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    // Sound Mode Capsule
                    val soundIcon = when (soundMode) {
                        "vibrate" -> "📳"
                        "silent" -> "🔕"
                        else -> "🔔"
                    }
                    HeroTileCapsule(
                        modifier = Modifier.weight(1f),
                        icon = soundIcon,
                        title = "Sound",
                        sub = soundMode.replaceFirstChar { it.uppercase() },
                        isActive = soundMode != "silent",
                        onClick = onCycleSoundMode
                    )
                    // Flashlight Capsule
                    HeroTileCapsule(
                        modifier = Modifier.weight(1f),
                        icon = "🔦",
                        title = "Torch",
                        sub = if (isTorchOn) "On" else "Off",
                        isActive = isTorchOn,
                        onClick = onToggleTorch
                    )
                }

                Spacer(modifier = Modifier.height(14.dp))

                // 4. Secondary Utility Squircles (Hotspot, 0W Mono, Air-Gap, Nokia Mode)
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    SquircleTile(
                        modifier = Modifier.weight(1f),
                        icon = "(((•)))",
                        label = "Hotspot",
                        isActive = isHotspotOn,
                        onClick = onToggleHotspot
                    )
                    SquircleTile(
                        modifier = Modifier.weight(1f),
                        icon = "🌓",
                        label = "0W Mono",
                        isActive = isGrayscaleOn,
                        onClick = onToggleGrayscale
                    )
                    SquircleTile(
                        modifier = Modifier.weight(1f),
                        icon = "🛡️",
                        label = "Air-Gap",
                        isActive = isAirGapActive,
                        onClick = onToggleAirGap
                    )
                    SquircleTile(
                        modifier = Modifier.weight(1f),
                        icon = "🔋",
                        label = "Ultra Save",
                        isActive = isNokiaModeOn,
                        onClick = onToggleNokiaMode
                    )
                }

                Spacer(modifier = Modifier.weight(1f))

                // 5. Drag Handle to close
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Box(
                        modifier = Modifier
                            .width(42.dp)
                            .height(4.dp)
                            .background(Color(0xFF3F3F46), RoundedCornerShape(2.dp))
                    )
                }
            }
        }
    }
}

@Composable
fun HeroTileCapsule(
    modifier: Modifier = Modifier,
    icon: String,
    title: String,
    sub: String,
    isActive: Boolean,
    onClick: () -> Unit
) {
    val bgColor = if (isActive) Color.White else Color(0xFF171717)
    val contentColor = if (isActive) Color.Black else Color.White
    val subColor = if (isActive) Color(0xFF27272A) else Color(0xFF8E8E93)

    Card(
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor),
        border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF27272A))),
        modifier = modifier.clickable { onClick() }
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 13.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(34.dp)
                    .background(if (isActive) Color.Black.copy(alpha = 0.1f) else Color(0xFF27272A), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(icon, fontSize = 16.sp)
            }
            Spacer(modifier = Modifier.width(10.dp))
            Column {
                Text(title, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = contentColor)
                Text(sub, fontSize = 10.sp, color = subColor, maxLines = 1)
            }
        }
    }
}

@Composable
fun SquircleTile(
    modifier: Modifier = Modifier,
    icon: String,
    label: String,
    isActive: Boolean,
    onClick: () -> Unit
) {
    val bgColor = if (isActive) Color.White else Color(0xFF121212)
    val contentColor = if (isActive) Color.Black else Color.White

    Card(
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor),
        border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF27272A))),
        modifier = modifier.clickable { onClick() }
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(icon, fontSize = 16.sp)
            Spacer(modifier = Modifier.height(4.dp))
            Text(label, fontSize = 10.sp, fontWeight = FontWeight.Medium, color = contentColor)
        }
    }
}
