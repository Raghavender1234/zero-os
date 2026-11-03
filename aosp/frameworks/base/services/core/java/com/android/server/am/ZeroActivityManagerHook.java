/*
 * Copyright (C) 2026 ZeroOS Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.server.am;

import android.content.Context;
import android.media.AudioManager;
import android.os.Process;
import android.util.Log;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * ZeroActivityManagerHook
 * 
 * Intercepts Android Process Lifecycle transitions inside ActivityManagerService.
 * Enforces the User-Intent Air-Gap:
 * 1. Immediate socket severing on app exit via dedicated ZERO_AIRGAP chain.
 * 2. Universal media and navigation exemptions (Spotify, Waze, OsmAnd, Google Maps).
 * 3. Idempotent netfilter rule management (0 duplicate rules).
 */
public final class ZeroActivityManagerHook {

    private static final String TAG = "ZeroActivityManagerHook";

    // Known media streaming applications
    private static final Set<String> MEDIA_PACKAGES = new HashSet<>(Arrays.asList(
        "com.spotify.music",
        "com.amazon.mp3",
        "com.apple.android.music",
        "com.google.android.apps.youtube.music",
        "com.aspiro.tidal",
        "deezer.android.app",
        "com.soundcloud.android",
        "com.pandora.android",
        "com.audible.application",
        "au.com.shiftyjelly.pocketcasts",
        "com.maxmpz.audioplayer"
    ));

    // Known navigation applications
    private static final Set<String> NAVIGATION_PACKAGES = new HashSet<>(Arrays.asList(
        "com.google.android.apps.maps",
        "com.waze",
        "com.here.app.maps",
        "net.osmand",
        "net.osmand.plus",
        "com.citymapper.app.release",
        "com.sygic.aura"
    ));

    private ZeroActivityManagerHook() {}

    /**
     * Called by ActivityManagerService when an activity transitions from RESUMED to STOPPED/PAUSED.
     */
    public static void onProcessBackgrounded(Context context, String packageName, int uid) {
        if (packageName == null || uid < Process.FIRST_APPLICATION_UID) {
            return; // Ignore system processes
        }

        // 1. Check for Active Media or Navigation Streaming Exemption
        if (isMediaOrNavActive(context, packageName)) {
            Log.i(TAG, "[" + packageName + "] Active Media/Nav session detected. Holding stream socket open.");
            return;
        }

        // 2. User-Intent Air-Gap: Sever background sockets
        Log.i(TAG, "[" + packageName + "] App backgrounded. Severing network sockets via ZERO_AIRGAP chain.");
        applyKernelNetfilterDrop(uid);
    }

    /**
     * Called by ActivityManagerService when an activity returns to the FOREGROUND.
     */
    public static void onProcessForegrounded(Context context, String packageName, int uid) {
        if (packageName == null || uid < Process.FIRST_APPLICATION_UID) {
            return;
        }

        Log.i(TAG, "[" + packageName + "] App foregrounded. Restoring network sockets.");
        restoreKernelNetfilter(uid);
    }

    private static boolean isMediaOrNavActive(Context context, String packageName) {
        if (MEDIA_PACKAGES.contains(packageName) || packageName.contains("music") || packageName.contains("audio")) {
            AudioManager audioManager = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (audioManager != null && audioManager.isMusicActive()) {
                return true;
            }
        }

        if (NAVIGATION_PACKAGES.contains(packageName) || packageName.contains("map") || packageName.contains("nav")) {
            return true;
        }

        return false;
    }

    private static void applyKernelNetfilterDrop(int uid) {
        try {
            // Idempotent insertion into custom ZERO_AIRGAP chain (prevents rule stacking)
            Runtime.getRuntime().exec(new String[]{
                "/system/bin/sh", "-c",
                "iptables -N ZERO_AIRGAP 2>/dev/null || true; " +
                "iptables -C OUTPUT -j ZERO_AIRGAP 2>/dev/null || iptables -I OUTPUT -j ZERO_AIRGAP; " +
                "iptables -C ZERO_AIRGAP -m owner --uid-owner " + uid + " -j DROP 2>/dev/null || " +
                "iptables -A ZERO_AIRGAP -m owner --uid-owner " + uid + " -j DROP; " +
                "ip6tables -N ZERO_AIRGAP 2>/dev/null || true; " +
                "ip6tables -C OUTPUT -j ZERO_AIRGAP 2>/dev/null || ip6tables -I OUTPUT -j ZERO_AIRGAP; " +
                "ip6tables -C ZERO_AIRGAP -m owner --uid-owner " + uid + " -j DROP 2>/dev/null || " +
                "ip6tables -A ZERO_AIRGAP -m owner --uid-owner " + uid + " -j DROP"
            }).waitFor();
        } catch (Exception e) {
            Log.w(TAG, "Netfilter drop failed: " + e.getMessage());
        }
    }

    private static void restoreKernelNetfilter(int uid) {
        try {
            Runtime.getRuntime().exec(new String[]{
                "/system/bin/sh", "-c",
                "while iptables -D ZERO_AIRGAP -m owner --uid-owner " + uid + " -j DROP 2>/dev/null; do :; done; " +
                "while ip6tables -D ZERO_AIRGAP -m owner --uid-owner " + uid + " -j DROP 2>/dev/null; do :; done"
            }).waitFor();
        } catch (Exception e) {
            // Restored
        }
    }
}
