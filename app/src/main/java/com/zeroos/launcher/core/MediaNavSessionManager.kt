package com.zeroos.launcher.core

import android.content.Context
import android.media.session.MediaController
import android.media.session.MediaSessionManager
import android.media.session.PlaybackState
import android.util.Log

/**
 * MediaNavSessionManager
 * 
 * Implements the "Intentional User Session" exception engine for ZeroOS.
 * 
 * The Core Problem:
 * Strict air-gapping freezes apps the second you exit to the home screen.
 * However, everyday users EXPECT:
 * 1. Spotify / Podcasts to keep playing music when the screen turns off or while using another app.
 * 2. Google Maps / Waze to keep speaking turn-by-turn directions while driving.
 * 
 * The ZeroOS Solution:
 * 1. Detect active media playback (PlaybackState.STATE_PLAYING) and active navigation sessions.
 * 2. Allow ONLY the audio stream or turn-by-turn GNSS updates to continue.
 * 3. All background advertising networks, analytics trackers, and camera/mic registers
 *    REMAIN COMPLETELY DROPPED by kernel netfilter (iptables) and AppOps.
 * 4. The millisecond the user hits PAUSE or completes the trip, the Air-Gap steel door
 *    slams immediately (0 B/s data, 0% CPU, location wiped).
 */
class MediaNavSessionManager(private val context: Context) {

    private val tag = "MediaNavGuard"

    companion object {
        // Known media streaming applications
        val MEDIA_PACKAGES = setOf(
            "com.spotify.music",
            "com.google.android.apps.youtube.music",
            "com.audible.application",
            "com.apple.android.music",
            "com.soundcloud.android",
            "deezer.android.app"
        )

        // Known navigation applications
        val NAVIGATION_PACKAGES = setOf(
            "com.google.android.apps.maps",
            "com.waze",
            "com.here.app.maps",
            "cz.aponia.bor3"
        )

        private val activeMediaSessions = mutableSetOf<String>()
        private val activeNavSessions = mutableSetOf<String>()

        fun setMediaPlaying(packageName: String, isPlaying: Boolean) {
            if (isPlaying) activeMediaSessions.add(packageName) else activeMediaSessions.remove(packageName)
        }

        fun setNavigating(packageName: String, isNavigating: Boolean) {
            if (isNavigating) activeNavSessions.add(packageName) else activeNavSessions.remove(packageName)
        }

        fun isMediaActive(packageName: String): Boolean = activeMediaSessions.contains(packageName)
        fun isNavigationActive(packageName: String): Boolean = activeNavSessions.contains(packageName)
    }

    /**
     * Determines whether an exiting app qualifies for a temporary media/navigation exemption.
     */
    fun shouldHoldAirGapExemption(packageName: String): Boolean {
        // Check active media playback
        if (isMediaActive(packageName)) {
            Log.i(tag, "[$packageName] Active audio playback session in progress. Holding audio streaming socket.")
            return true
        }

        // Check active turn-by-turn navigation
        if (isNavigationActive(packageName)) {
            Log.i(tag, "[$packageName] Active turn-by-turn navigation in progress. Holding GNSS location stream.")
            return true
        }

        return false
    }

    /**
     * Called when media playback pauses or stops.
     * Instantly slams the Air-Gap steel door.
     */
    fun onMediaStopped(packageName: String, uid: Int) {
        Log.i(tag, "[$packageName] Playback STOPPED/PAUSED. Slashing remaining sockets & freezing background CPU.")
        setMediaPlaying(packageName, false)
        
        // Sever netfilter sockets
        KernelShield.executeRootCommand("iptables -I OUTPUT -m owner --uid-owner $uid -j DROP")
        // Freeze CPU wakelocks
        KernelShield.executeRootCommand("am force-stop $packageName || pm suspend $packageName")
    }

    /**
     * Called when a navigation route ends or is cancelled.
     * Instantly revokes GPS location access and severs sockets.
     */
    fun onNavigationEnded(packageName: String, uid: Int) {
        Log.i(tag, "[$packageName] Navigation trip ended. Revoking GNSS hardware registers.")
        setNavigating(packageName, false)

        SingleSessionPermissionManager(context).onAppClosed(packageName, uid)
        KernelShield.executeRootCommand("iptables -I OUTPUT -m owner --uid-owner $uid -j DROP")
    }
}
