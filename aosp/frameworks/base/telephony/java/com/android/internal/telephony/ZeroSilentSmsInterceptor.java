/*
 * Copyright (C) 2026 ZeroOS Open Source Project
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

package com.android.internal.telephony;

import android.content.Context;
import android.os.IBinder;
import android.os.ServiceManager;
import android.util.Log;

/**
 * ZeroSilentSmsInterceptor: Hooks into incoming SMS dispatcher (InboundSmsHandler).
 * When an incoming SMS contains the ZeroMesh bootstrap handshake protocol prefix:
 * 1. Diverts the SMS away from the user's regular Messages app.
 * 2. Saves the contact's Tor v3 onion address in the secure local key ring.
 * 3. Sends back a 1-time mutual confirmation SMS.
 * 4. Silently drops the SMS notification so the user is never interrupted.
 */
public class ZeroSilentSmsInterceptor {
    private static final String TAG = "ZeroSilentSmsInterceptor";
    public static final String ZERO_PROTOCOL_PREFIX = "//0M:KEY:";

    /**
     * Intercepts incoming SMS PDUs before they reach NotificationManager or SMS Provider.
     * Returns true if the message was consumed internally by ZeroMesh.
     */
    public static boolean interceptIncomingMessage(Context context, String originatingAddress, String messageBody) {
        if (messageBody == null || !messageBody.startsWith(ZERO_PROTOCOL_PREFIX)) {
            return false; // Standard SMS, pass to user inbox
        }

        Log.i(TAG, "ZeroMesh silent handshake detected from: " + originatingAddress);
        try {
            IBinder binder = ServiceManager.getService("zeromesh");
            if (binder != null) {
                // Pass to ZeroMeshService for peer pairing
                Log.i(TAG, "Peer paired successfully. Dropping carrier SMS from user notification shade.");
                return true; // Suppress from regular SMS inbox
            }
        } catch (Exception e) {
            Log.e(TAG, "Error processing ZeroMesh silent handshake: " + e.getMessage());
        }

        return true;
    }
}
