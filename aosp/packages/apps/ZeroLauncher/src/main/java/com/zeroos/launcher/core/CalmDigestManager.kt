package com.zeroos.launcher.core

import android.app.Notification
import android.content.Context
import android.service.notification.StatusBarNotification
import android.util.Log

/**
 * ZeroOS Calm Notification Digest Manager
 * 
 * Separates critical 1-on-1 human communication (calls, direct messages, 2FA codes)
 * from algorithmic attention-traps (social media likes, marketing, promotional pushes).
 * Bundles low-priority noise into 2 daily calm digests.
 */
class CalmDigestManager(private val context: Context) {

    private val tag = "ZeroOS-CalmDigest"
    private var isDigestEnabled = true

    // Whitelisted priority categories that ring immediately
    private val priorityCategories = setOf(
        Notification.CATEGORY_CALL,
        Notification.CATEGORY_MESSAGE,
        Notification.CATEGORY_ALARM,
        Notification.CATEGORY_EVENT,
        Notification.CATEGORY_REMINDER
    )

    private val heldDigestList = mutableListOf<DigestItem>()

    data class DigestItem(
        val id: String,
        val packageName: String,
        val title: String,
        val text: String,
        val timestamp: Long = System.currentTimeMillis()
    )

    fun setDigestEnabled(enabled: Boolean) {
        isDigestEnabled = enabled
        Log.i(tag, "Calm Digest status updated: enabled=$enabled")
    }

    fun isDigestActive(): Boolean = isDigestEnabled

    /**
     * Determines whether an incoming notification should alert immediately or be held for Calm Digest.
     */
    fun shouldAlertImmediately(sbn: StatusBarNotification): Boolean {
        if (!isDigestEnabled) return true

        val notification = sbn.notification ?: return true
        val category = notification.category

        // 1. Direct Calls, SMS, Alarms always ring through
        if (priorityCategories.contains(category)) {
            return true
        }

        // 2. High-priority conversation flags (Android 11+ MessagingStyle)
        val isConversation = notification.extras.getBoolean("android.isConversation", false)
        if (isConversation) {
            return true
        }

        // 3. Check for 2FA verification codes / banking security
        val title = notification.extras.getCharSequence(Notification.EXTRA_TITLE)?.toString().orEmpty()
        val text = notification.extras.getCharSequence(Notification.EXTRA_TEXT)?.toString().orEmpty()
        val combined = "$title $text".lowercase()
        if (combined.contains("code") || combined.contains("otp") || combined.contains("verification") || combined.contains("security alert")) {
            return true
        }

        // All other algorithmic alerts (likes, recommendations, promos) are held for the digest
        holdForDigest(sbn.packageName, title, text)
        return false
    }

    private fun holdForDigest(packageName: String, title: String, text: String) {
        val item = DigestItem(
            id = "${packageName}_${System.currentTimeMillis()}",
            packageName = packageName,
            title = title,
            text = text
        )
        heldDigestList.add(item)
        Log.i(tag, "Bundled background notification from $packageName into Calm Digest. Total held: ${heldDigestList.size}")
    }

    fun getHeldDigestItems(): List<DigestItem> = heldDigestList.toList()

    fun clearDigest() {
        heldDigestList.clear()
    }
}
