package com.zeroos.launcher.ui.components

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.zeroos.launcher.ui.theme.*

/**
 * 1-Tap Hardware Privacy Shield Card for any installed app.
 * Provides instant kernel-level killswitches without typing commands.
 */
@Composable
fun PrivacyActionCard(
    appName: String,
    packageName: String,
    isDataCut: Boolean,
    isMicMuted: Boolean,
    isCamKilled: Boolean,
    isFrozen: Boolean,
    blockedTrackersCount: Int = 18,
    onToggleData: () -> Unit,
    onToggleMic: () -> Unit,
    onToggleCam: () -> Unit,
    onToggleFreeze: () -> Unit,
    onLaunch: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .border(1.dp, BorderSubtle, RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = SurfaceCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Header: App Name & Launch
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = appName,
                        color = TextPrimary,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = packageName,
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }

                Button(
                    onClick = onLaunch,
                    colors = ButtonDefaults.buttonColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(6.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text("Launch", color = AmberAccent, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }
            }

            Divider(color = BorderSubtle, thickness = 0.5.dp)

            // 1-Tap Shield Toggles
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                // 1. Mobile & Wi-Fi Data
                ShieldToggleRow(
                    label = "📶 Internet (iptables)",
                    isBlocked = isDataCut,
                    activeText = "ONLINE",
                    blockedText = "SEVERED (0 B/s)",
                    onToggle = onToggleData
                )

                // 2. Microphone Hardware
                ShieldToggleRow(
                    label = "🎙️ Microphone (AppOps)",
                    isBlocked = isMicMuted,
                    activeText = "LISTENING",
                    blockedText = "MUTED (Dead Audio)",
                    onToggle = onToggleMic
                )

                // 3. Camera Sensor
                ShieldToggleRow(
                    label = "📷 Camera Hardware",
                    isBlocked = isCamKilled,
                    activeText = "ACCESSIBLE",
                    blockedText = "LOCKED",
                    onToggle = onToggleCam
                )

                // 4. Background Hibernation
                ShieldToggleRow(
                    label = "🧊 Hibernation (pm suspend)",
                    isBlocked = isFrozen,
                    activeText = "ACTIVE",
                    blockedText = "DEEP COMA (0% CPU)",
                    onToggle = onToggleFreeze
                )
            }

            // Footer Tracker Summary
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "🛡️ $blockedTrackersCount telemetry beacons blocked today",
                    color = AmberMuted,
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace
                )
            }
        }
    }
}

@Composable
private fun ShieldToggleRow(
    label: String,
    isBlocked: Boolean,
    activeText: String,
    blockedText: String,
    onToggle: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = label, color = TextPrimary, fontSize = 12.sp)

        Button(
            onClick = onToggle,
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isBlocked) RedSevered.copy(alpha = 0.2f) else SurfaceDark
            ),
            border = ButtonDefaults.outlinedButtonBorder.copy(
                brush = androidx.compose.ui.graphics.SolidColor(if (isBlocked) RedSevered else BorderSubtle)
            ),
            shape = RoundedCornerShape(6.dp),
            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp)
        ) {
            Text(
                text = if (isBlocked) blockedText else activeText,
                color = if (isBlocked) RedSevered else GreenActive,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace
            )
        }
    }
}
