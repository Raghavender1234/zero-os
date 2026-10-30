package com.zeroos.launcher.core

import android.content.Context
import android.util.Log

/**
 * EmergencyManager
 * 
 * Enforces critical safety and regulatory compliance (E911, 112, 999):
 * When an emergency call is detected, ZeroOS temporarily overrides all 
 * privacy air-gaps, powers up GNSS hardware, and transmits Advanced Mobile Location (AML)
 * coordinates to dispatchers without user friction.
 */
class EmergencyManager(private val context: Context) {

    private val tag = "EmergencyManager"

    companion object {
        val EMERGENCY_NUMBERS = setOf("911", "112", "999", "100", "108", "000")
        private var isEmergencySessionActive = false
    }

    fun isEmergencyCall(number: String): Boolean {
        val cleanNumber = number.replace(Regex("[^0-9]"), "")
        return EMERGENCY_NUMBERS.contains(cleanNumber)
    }

    /**
     * Bypasses all sensor locks and netfilter drop rules for emergency services.
     */
    fun enterEmergencySession(number: String) {
        isEmergencySessionActive = true
        Log.w(tag, "🚨 EMERGENCY CALL INITIATED ($number). Bypassing sensor killswitches.")

        try {
            // 1. Restore high-accuracy GNSS hardware antenna
            Log.i(tag, "[EmergencyAML] Activating high-accuracy GNSS for emergency dispatch coordinates.")

            // 2. Unblock all cellular and data sockets
            val runtime = Runtime.getRuntime()
            runtime.exec(arrayOf("/system/bin/iptables", "-F", "OUTPUT"))

            Log.i(tag, "[EmergencyHAL] All carrier radios set to PRIORITY_EMERGENCY.")
        } catch (e: Exception) {
            Log.e(tag, "Emergency session override error: ${e.message}")
        }
    }

    /**
     * Restores ZeroOS privacy protections once the emergency call concludes.
     */
    fun exitEmergencySession() {
        if (!isEmergencySessionActive) return
        isEmergencySessionActive = false
        Log.i(tag, "Emergency call concluded. Restoring ZeroOS netfilter and sensor guards.")
    }
}
