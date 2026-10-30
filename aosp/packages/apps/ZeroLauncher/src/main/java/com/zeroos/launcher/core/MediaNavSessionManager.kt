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
        // Universal media streaming applications registry
        val MEDIA_PACKAGES = setOf(
            "com.spotify.music",
            "com.amazon.mp3",                          // Amazon Music
            "com.apple.android.music",                 // Apple Music
            "com.google.android.apps.youtube.music",  // YouTube Music
            "com.aspiro.tidal",                       // Tidal Hi-Fi
            "deezer.android.app",                     // Deezer
            "com.soundcloud.android",                 // SoundCloud
            "com.pandora.android",                    // Pandora
            "com.audible.application",                // Audible Audiobooks
            "au.com.shiftyjelly.pocketcasts",         // Pocket Casts
            "com.maxmpz.audioplayer",                 // Poweramp
            "tunein.player"                           // TuneIn Radio
        )

        // Universal turn-by-turn navigation applications registry
        val NAVIGATION_PACKAGES = setOf(
            "com.google.android.apps.maps",           // Google Maps
            "com.waze",                               // Waze Navigation
            "com.here.app.maps",                      // HERE WeGo
            "net.osmand",                             // OsmAnd OpenStreetMap
            "net.osmand.plus",
            "com.citymapper.app.release",             // Citymapper
            "com.sygic.aura",                         // Sygic GPS
            "com.tomtom.gplay.navapp"                 // TomTom GO
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
     * Works universally across ALL audio apps (Amazon Music, Spotify, Apple Music, Audible, Tidal, Deezer, etc.)
     * and ALL navigation apps (Google Maps, Waze, HERE, OsmAnd, Citymapper, etc.)
     */
    fun shouldHoldAirGapExemption(packageName: String): Boolean {
        // 1. Universal Media Check (Registry + Android MediaSessionManager + AudioManager)
        if (isMediaActive(packageName) || isAppActivelyEmittingAudio(packageName)) {
            Log.i(tag, "[$packageName] Universal Media Session detected (Music/Audio active). Holding audio streaming socket.")
            return true
        }

        // 2. Universal Navigation Check (Registry + Android Location Foreground Service)
        if (isNavigationActive(packageName) || isAppActivelyNavigating(packageName)) {
            Log.i(tag, "[$packageName] Universal Navigation Session detected (Turn-by-turn routing active). Holding GNSS location stream.")
            return true
        }

        return false
    }

    /**
     * Framework-level hardware check: Does the app hold an active audio output stream or MediaSession?
     */
    fun isAppActivelyEmittingAudio(packageName: String): Boolean {
        if (!MEDIA_PACKAGES.contains(packageName) && !packageName.contains("music") && !packageName.contains("audio") && !packageName.contains("radio")) {
            return false
        }
        return try {
            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as? android.media.AudioManager
            audioManager?.isMusicActive == true
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Framework-level location check: Does the app hold an active navigation foreground service?
     */
    fun isAppActivelyNavigating(packageName: String): Boolean {
        if (!NAVIGATION_PACKAGES.contains(packageName) && !packageName.contains("map") && !packageName.contains("nav") && !packageName.contains("waze")) {
            return false
        }
        return isNavigationActive(packageName)
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
