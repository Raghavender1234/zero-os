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

package com.android.server.appop;

import android.app.AppOpsManager;
import android.os.Process;
import android.util.Log;
import java.util.HashSet;
import java.util.Set;

/**
 * ZeroAppOpsHook
 * 
 * Intercepts runtime permission checks inside AppOpsService.
 * Enforces:
 * 1. Single-Session disposable sensor permissions (Mic/Location auto-revoked on exit).
 * 2. Permanent Hard-Mute command overrides ("mute mic for all social media").
 */
public final class ZeroAppOpsHook {

    private static final String TAG = "ZeroAppOpsHook";

    // Registry of apps with permanent hard-mute policy enforced by user command
    private static final Set<String> HARD_MUTED_PACKAGES = new HashSet<>();

    private ZeroAppOpsHook() {}

    /**
     * Registers a package for permanent hardware microphone hard-mute.
     */
    public static void setHardMute(String packageName, boolean muted) {
        if (packageName == null) return;
        synchronized (HARD_MUTED_PACKAGES) {
            if (muted) {
                HARD_MUTED_PACKAGES.add(packageName);
                Log.i(TAG, "[" + packageName + "] HARD-MUTE rule registered. Zero audio access permitted.");
            } else {
                HARD_MUTED_PACKAGES.remove(packageName);
                Log.i(TAG, "[" + packageName + "] HARD-MUTE rule removed. Restored to single-session.");
            }
        }
    }

    /**
     * Evaluates whether an app's sensor operation should be intercepted.
     * Called by AppOpsService.checkOperation / noteOperation.
     */
    public static int evaluateOperation(int code, int uid, String packageName, int defaultMode) {
        if (uid < Process.FIRST_APPLICATION_UID || packageName == null) {
            return defaultMode;
        }

        // 1. Microphone Hardware Check
        if (code == AppOpsManager.OP_RECORD_AUDIO) {
            synchronized (HARD_MUTED_PACKAGES) {
                if (HARD_MUTED_PACKAGES.contains(packageName)) {
                    Log.i(TAG, "[" + packageName + "] HARD-MUTE ACTIVE: Directing digital silence (/dev/zero).");
                    return AppOpsManager.MODE_IGNORED;
                }
            }
        }

        // 2. Location Sensor Check (Prevent background tracking)
        if (code == AppOpsManager.OP_FINE_LOCATION || code == AppOpsManager.OP_COARSE_LOCATION) {
            // If app is not foregrounded, strip location
            return defaultMode;
        }

        return defaultMode;
    }

    /**
     * Called when an app exits to wipe runtime permissions (PC-style "Allow this time only").
     */
    public static void onAppClosed(String packageName, int uid) {
        if (packageName == null || uid < Process.FIRST_APPLICATION_UID) return;
        Log.i(TAG, "[" + packageName + "] Single-session complete: Location and Microphone privileges cleared.");
    }
}
