package com.zeroos.launcher.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Pure OLED Black Palette - Physically powers off OLED subpixels (0.00 Watts)
val OledBlack = Color(0xFF000000)
val SurfaceDark = Color(0xFF0A0A0A)
val SurfaceCard = Color(0xFF141414)
val BorderSubtle = Color(0xFF262626)

val TextPrimary = Color(0xFFE5E5E5)
val TextMuted = Color(0xFF888888)

// Cyberpunk Amber / Phosphor Palette (Lowest voltage draw, zero night eye-fatigue)
val AmberAccent = Color(0xFFFFB000)
val AmberMuted = Color(0xFF996A00)
val GreenActive = Color(0xFF34D399)
val RedSevered = Color(0xFFEF4444)

private val DarkColorScheme = darkColorScheme(
    primary = AmberAccent,
    background = OledBlack,
    surface = SurfaceDark,
    onPrimary = OledBlack,
    onBackground = TextPrimary,
    onSurface = TextPrimary
)

@Composable
fun ZeroTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content
    )
}
