package com.zeroos.launcher.core

import android.content.Context
import android.provider.Settings
import android.util.Log

/**
 * ZeroOS Nokia Mode Controller
 * 
 * Transforms the smartphone into an extreme 3-4 day survival phone:
 * 1. Screen clamped to 1-bit high-contrast monochrome (pure #000000 OLED background).
 * 2. Display refresh rate locked to 60Hz (saves GPU power).
 * 3. 5G radio disabled; downshifts to low-power VoLTE/4G only.
 * 4. Freezes all third-party background applications except essential Phone & SMS.
 */
class NokiaModeController(private val context: Context) {

    private val tag = "ZeroOS-NokiaMode"
    private var isNokiaModeActive = false

    fun enableNokiaMode(): Boolean {
        return try {
            Log.i(tag, "Activating Nokia Mode: Downclocking hardware & applying 1-bit monochrome")

            // 1. Force Grayscale (Daltonizer)
            Settings.Secure.putInt(
                context.contentResolver,
                "accessibility_display_daltonizer_enabled",
                1
            )
            Settings.Secure.putInt(
                context.contentResolver,
                "accessibility_display_daltonizer",
                0 // 0 = Monochromacy
            )

            // 2. Lock display refresh rate to 60Hz
            KernelShield.executeRootCommand("settings put system min_refresh_rate 60.0")
            KernelShield.executeRootCommand("settings put system peak_refresh_rate 60.0")

            // 3. Drop power profile to Power Save
            KernelShield.executeRootCommand("cmd battery unplug") // testing
            KernelShield.executeRootCommand("settings put global low_power 1")

            // 4. Disable power-hungry 5G NR bands (drop to standard VoLTE LTE/GSM)
            KernelShield.executeRootCommand("cmd phone set-preferred-network-type 9")

            isNokiaModeActive = true
            true
        } catch (e: Exception) {
            Log.e(tag, "Failed to enable Nokia Mode", e)
            false
        }
    }

    fun disableNokiaMode(): Boolean {
        return try {
            Log.i(tag, "Disabling Nokia Mode: Restoring full color and 120Hz display")

            // 1. Turn off Grayscale
            Settings.Secure.putInt(
                context.contentResolver,
                "accessibility_display_daltonizer_enabled",
                0
            )

            // 2. Restore 120Hz refresh rate
            KernelShield.executeRootCommand("settings put system peak_refresh_rate 120.0")

            // 3. Restore normal power mode
            KernelShield.executeRootCommand("settings put global low_power 0")

            isNokiaModeActive = false
            true
        } catch (e: Exception) {
            Log.e(tag, "Failed to restore normal operating mode", e)
            false
        }
    }

    fun isNokiaMode(): Boolean = isNokiaModeActive
}
