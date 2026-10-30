package com.zeroos.launcher.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.zeroos.launcher.ui.theme.*

/**
 * Micro-Window OLED Controller:
 * Physically restricts rendering to a 2.5-inch thumb-box at the bottom of the screen.
 * The surrounding 80% of the display is pitch black (#000000), drawing 0.00 Watts on OLED panels.
 */
@Composable
fun MicroDisplayOverlay(
    currentTime: String,
    batteryPercent: Int,
    isGrayscale: Boolean,
    onExpandFullDisplay: () -> Unit,
    content: @Composable () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(OledBlack) // 100% physically unpowered pixels
    ) {
        // Upper 75% Screen: Pitch Black (Off) with subtle double-tap restore hint
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .fillMaxHeight(0.70f)
                .clickable { onExpandFullDisplay() },
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "⚡ 0.00W OLED SHUTDOWN (Tap anywhere for Full Screen)",
                color = TextMuted.copy(alpha = 0.25f),
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace
            )
        }

        // Lower 30% Screen: The Active 2.5-inch Thumb Window
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .padding(12.dp)
                .background(SurfaceDark, RoundedCornerShape(16.dp))
                .border(1.dp, BorderSubtle, RoundedCornerShape(16.dp))
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // Mini Status Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "$currentTime · $batteryPercent% BATTERY",
                    color = AmberAccent,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
                Text(
                    text = if (isGrayscale) "MONO 1Hz" else "COLOR",
                    color = TextMuted,
                    fontSize = 10.sp,
                    fontFamily = FontFamily.Monospace
                )
            }

            // Embedded Micro Content / Command Shell
            content()
        }
    }
}
