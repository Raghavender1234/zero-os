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
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * ZeroAppOpsHook
 * 
 * Intercepts runtime sensor operations inside AppOpsService (Android Framework).
 * Enforces:
 * 1. Single-Session disposable sensor permissions (Mic/Location restricted in background).
 * 2. Permanent Hard-Mute overrides with disk persistence across reboots.
 */
public final class ZeroAppOpsHook {

    private static final String TAG = "ZeroAppOpsHook";
    private static final String PERSISTENCE_FILE = "/data/system/zero_hard_mutes.txt";

    // Synchronized registry with reboot persistence
    private static final Set<String> HARD_MUTED_PACKAGES = Collections.synchronizedSet(new HashSet<>());
    private static volatile boolean sLoaded = false;

    private ZeroAppOpsHook() {}

    private static void ensureLoaded() {
        if (!sLoaded) {
            synchronized (HARD_MUTED_PACKAGES) {
                if (!sLoaded) {
                    loadFromDisk();
                    sLoaded = true;
                }
            }
        }
    }

    private static void loadFromDisk() {
        File f = new File(PERSISTENCE_FILE);
        if (!f.exists()) return;
        try (BufferedReader br = new BufferedReader(new FileReader(f))) {
            String line;
            while ((line = br.readLine()) != null) {
                String pkg = line.trim();
                if (!pkg.isEmpty()) HARD_MUTED_PACKAGES.add(pkg);
            }
            Log.i(TAG, "Loaded " + HARD_MUTED_PACKAGES.size() + " hard-muted packages from disk.");
        } catch (Exception e) {
            Log.e(TAG, "Failed to load hard-mutes from " + PERSISTENCE_FILE, e);
        }
    }

    private static void saveToDisk() {
        try {
            File f = new File(PERSISTENCE_FILE);
            File parent = f.getParentFile();
            if (parent != null && !parent.exists()) parent.mkdirs();
            try (FileWriter fw = new FileWriter(f, false)) {
                for (String pkg : HARD_MUTED_PACKAGES) {
                    fw.write(pkg + "\n");
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Failed to persist hard-mutes to disk", e);
        }
    }

    /**
     * Registers a package for permanent microphone/camera hard-mute with reboot persistence.
     */
    public static void setHardMute(String packageName, boolean muted) {
        if (packageName == null) return;
        ensureLoaded();
        if (muted) {
            HARD_MUTED_PACKAGES.add(packageName);
            Log.i(TAG, "[" + packageName + "] HARD-MUTE registered. Zero audio access permitted.");
        } else {
            HARD_MUTED_PACKAGES.remove(packageName);
            Log.i(TAG, "[" + packageName + "] HARD-MUTE removed.");
        }
        saveToDisk();
    }

    /**
     * Evaluates whether an app's sensor operation should be intercepted.
     * Called directly by AppOpsService.checkOperation / noteOperation.
     */
    public static int evaluateOperation(int code, int uid, String packageName, int uidState, int defaultMode) {
        if (uid < Process.FIRST_APPLICATION_UID || packageName == null) {
            return defaultMode;
        }

        ensureLoaded();

        // 1. Permanent Hard-Mute Override (Always Deny/Ignore audio & camera)
        if (code == AppOpsManager.OP_RECORD_AUDIO || code == AppOpsManager.OP_CAMERA) {
            if (HARD_MUTED_PACKAGES.contains(packageName)) {
                Log.i(TAG, "[" + packageName + "] HARD-MUTE ACTIVE: Silencing sensor operation.");
                return AppOpsManager.MODE_IGNORED;
            }
        }

        // 2. Background Sensor Restrictions (Single-Session Enforcement)
        // If app is not in the foreground (uidState > 200 / not PROCESS_STATE_TOP),
        // reject silent background microphone and location access.
        boolean isBackground = (uidState > 200); // 200 = ActivityManager.PROCESS_STATE_TOP
        if (isBackground) {
            if (code == AppOpsManager.OP_RECORD_AUDIO) {
                Log.w(TAG, "[" + packageName + "] Background microphone access blocked.");
                return AppOpsManager.MODE_IGNORED;
            }
            if (code == AppOpsManager.OP_FINE_LOCATION || code == AppOpsManager.OP_COARSE_LOCATION) {
                Log.w(TAG, "[" + packageName + "] Background location polling blocked.");
                return AppOpsManager.MODE_IGNORED;
            }
        }

        return defaultMode;
    }
}
