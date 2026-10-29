package com.zeroos.launcher.core

import android.content.Context
import android.hardware.camera2.CameraAccessException
import android.hardware.camera2.CameraManager
import android.os.Build
import android.os.PowerManager
import android.provider.Settings
import android.util.Log

/**
 * Direct system and hardware bridge for ZeroOS.
 * Executes camera torch, display color transforms, reboot, and system diagnostics.
 */
class HardwareController(private val context: Context) {

    private val tag = "ZeroOS-Hardware"
    private val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as? CameraManager
    private val powerManager = context.getSystemService(Context.POWER_SERVICE) as? PowerManager

    private var isTorchOn = false
    private var isHotspotOn = false

    /**
     * Toggles personal Wi-Fi hotspot / tethering.
     * Starts HostAPD and assigns DHCP leases on 192.168.43.1/24.
     */
    fun setHotspot(enable: Boolean): Boolean {
        isHotspotOn = enable
        Log.i(tag, "Hotspot state requested: $enable")
        return try {
            // Android 11+ TetheringManager or Root execution
            if (enable) {
                KernelShield.executeRootCommand("cmd connectivity tether start-tethering wifi || svc wifi setHotspot enabled")
            } else {
                KernelShield.executeRootCommand("cmd connectivity tether stop-tethering wifi || svc wifi setHotspot disabled")
            }
            true
        } catch (e: Exception) {
            Log.e(tag, "Failed to toggle hotspot", e)
            false
        }
    }

    fun isHotspotActive(): Boolean = isHotspotOn

    /**
     * Toggles the physical camera flash LED on or off.
     */
    fun setFlashlight(enable: Boolean): Boolean {
        return try {
            val cameraId = cameraManager?.cameraIdList?.firstOrNull() ?: return false
            cameraManager.setTorchMode(cameraId, enable)
            isTorchOn = enable
            Log.d(tag, "Flashlight state set to: $enable")
            true
        } catch (e: CameraAccessException) {
            Log.e(tag, "Failed to toggle flashlight", e)
            false
        }
    }

    fun isFlashlightActive(): Boolean = isTorchOn

    /**
     * Toggles system-wide grayscale (Daltonizer monochrome mode).
     * Physical effect: Converts all UI and app pixels to black and white,
     * drastically cutting visual dopamine triggers and saving OLED subpixel power.
     */
    fun setGrayscale(enable: Boolean): Boolean {
        return try {
            val resolver = context.contentResolver
            if (enable) {
                // Enable color correction daltonizer
                Settings.Secure.putInt(resolver, "accessibility_display_daltonizer_enabled", 1)
                // Mode 0 = Grayscale / Monochrome
                Settings.Secure.putInt(resolver, "accessibility_display_daltonizer", 0)
            } else {
                Settings.Secure.putInt(resolver, "accessibility_display_daltonizer_enabled", 0)
            }
            Log.d(tag, "Display Grayscale set to: $enable")
            true
        } catch (e: Exception) {
            Log.e(tag, "Failed to set grayscale mode. Requires WRITE_SECURE_SETTINGS or Root.", e)
            // Fallback via root shell
            KernelShield.executeRootCommand("settings put secure accessibility_display_daltonizer_enabled ${if (enable) 1 else 0}")
            KernelShield.executeRootCommand("settings put secure accessibility_display_daltonizer 0")
            true
        }
    }

    fun isGrayscaleActive(): Boolean {
        return try {
            Settings.Secure.getInt(context.contentResolver, "accessibility_display_daltonizer_enabled", 0) == 1
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Executes immediate system restart.
     */
    fun rebootSystem(reason: String = "ZeroOS User Command"): Boolean {
        return try {
            Log.i(tag, "Rebooting system: $reason")
            powerManager?.reboot(reason)
            true
        } catch (e: Exception) {
            Log.e(tag, "Framework reboot failed, falling back to kernel root reboot", e)
            KernelShield.executeRootCommand("svc power reboot || reboot")
            true
        }
    }

    /**
     * Retrieves hardware summary for 'About Phone' command.
     */
    fun getHardwareSummary(): Map<String, String> {
        val totalRamMb = Runtime.getRuntime().totalMemory() / (1024 * 1024)
        val freeRamMb = Runtime.getRuntime().freeMemory() / (1024 * 1024)

        return mapOf(
            "Device Model" to "${Build.MANUFACTURER} ${Build.MODEL}",
            "OS Kernel" to System.getProperty("os.version", "Linux 5.x"),
            "ZeroOS Version" to "1.0.0-Nightly (AOSP Base)",
            "Android Security Patch" to Build.VERSION.SECURITY_PATCH,
            "JVM Memory" to "Free: ${freeRamMb}MB / Total: ${totalRamMb}MB",
            "Root Status" to if (KernelShield.isRootAvailable()) "Active (KernelSU/Magisk)" else "Restricted (Shizuku Required)"
        )
    }
}
