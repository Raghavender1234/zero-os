package com.zeroos.launcher.core

import android.content.Context
import android.content.Intent
import android.util.Log

/**
 * ZeroOS Ephemeral Sandbox Manager
 * 
 * Provides single-use disposable execution for apps:
 * - Launching an app in Ephemeral mode allows the user to perform an action (e.g. rent a scooter, browse a store).
 * - The moment the app is closed or the user returns to Home, all local cache, storage, cookies,
 *   and tracker identifier tokens are completely vaporized.
 */
class EphemeralSandboxManager(private val context: Context) {

    private val tag = "ZeroOS-Ephemeral"
    private val activeEphemeralPackages = mutableSetOf<String>()

    /**
     * Launches an application with an ephemeral session tag.
     */
    fun launchEphemeralApp(packageName: String): Boolean {
        return try {
            Log.i(tag, "Launching app '$packageName' in Disposable Ephemeral Sandbox")
            activeEphemeralPackages.add(packageName)

            val launchIntent = context.packageManager.getLaunchIntentForPackage(packageName)
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_NO_HISTORY)
                context.startActivity(launchIntent)
                true
            } else {
                false
            }
        } catch (e: Exception) {
            Log.e(tag, "Failed to launch ephemeral app $packageName", e)
            false
        }
    }

    /**
     * Checks if the package was launched ephemerally, and if so, vaporizes its state.
     */
    fun onAppClosed(packageName: String) {
        if (activeEphemeralPackages.contains(packageName)) {
            Log.i(tag, "Ephemeral session ended for '$packageName'. Vaporizing all cookies, caches, and storage.")
            
            // 1. Force stop process
            KernelShield.executeRootCommand("am force-stop $packageName")

            // 2. Clear app data directory (cache, databases, shared_prefs)
            KernelShield.executeRootCommand("pm clear $packageName")

            // 3. Remove from active ephemeral set
            activeEphemeralPackages.remove(packageName)
            Log.i(tag, "App '$packageName' successfully wiped. Zero residue remains.")
        }
    }

    fun isEphemeral(packageName: String): Boolean = activeEphemeralPackages.contains(packageName)
}
