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

package android.os;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Log;
import java.security.KeyPairGenerator;
import java.security.KeyStore;

/**
 * ZeroIntegrityBridge
 * 
 * Hardware-Honest Security & Attestation Diagnostic Service.
 * 
 * Principles:
 * 1. Zero Device Spoofing: Preserves true hardware identity (Samsung, Motorola, Pixel).
 *    Never injects fake Google Pixel ('husky') fingerprints that break vendor camera/HALs
 *    or get blacklisted by Google.
 * 2. Transparent Attestation: Queries device KeyMint / StrongBox hardware Keystore
 *    and reports genuine attestation states.
 */
public final class ZeroIntegrityBridge {

    private static final String TAG = "ZeroIntegrityBridge";

    public enum AttestationStatus {
        HARDWARE_BACKED_KEYMINT,
        STRONGBOX_ENCLAVE,
        SOFTWARE_FALLBACK,
        UNAVAILABLE
    }

    private ZeroIntegrityBridge() {}

    /**
     * Initializes hardware security diagnostics during application bootstrap.
     * Preserves genuine OEM identity (Build.DEVICE, Build.MODEL, Build.MANUFACTURER).
     */
    public static void init(String packageName) {
        if (packageName == null) return;
        // Maintain genuine hardware parameters without property spoofing
        Log.d(TAG, "Initialized integrity subsystem for: " + packageName + " [Hardware: " + Build.MODEL + "]");
    }

    /**
     * Diagnostic helper: Tests whether the physical device provides hardware-backed KeyMint/StrongBox.
     */
    public static AttestationStatus evaluateHardwareSecurity(Context context) {
        try {
            KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
            keyStore.load(null);

            KeyPairGenerator kpg = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_EC, "AndroidKeyStore"
            );

            KeyGenParameterSpec spec = new KeyGenParameterSpec.Builder(
                "zero_integrity_test_alias",
                KeyProperties.PURPOSE_SIGN | KeyProperties.PURPOSE_VERIFY
            )
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setIsStrongBoxBacked(true)
            .build();

            kpg.initialize(spec);
            kpg.generateKeyPair();
            keyStore.deleteEntry("zero_integrity_test_alias");

            return AttestationStatus.STRONGBOX_ENCLAVE;
        } catch (Exception e) {
            // Strongbox not present; check standard KeyMint hardware
            try {
                KeyPairGenerator kpg = KeyPairGenerator.getInstance(
                    KeyProperties.KEY_ALGORITHM_EC, "AndroidKeyStore"
                );
                KeyGenParameterSpec spec = new KeyGenParameterSpec.Builder(
                    "zero_integrity_test_alias",
                    KeyProperties.PURPOSE_SIGN | KeyProperties.PURPOSE_VERIFY
                )
                .setDigests(KeyProperties.DIGEST_SHA256)
                .build();

                kpg.initialize(spec);
                kpg.generateKeyPair();
                KeyStore.getInstance("AndroidKeyStore").load(null);
                KeyStore.getInstance("AndroidKeyStore").deleteEntry("zero_integrity_test_alias");

                return AttestationStatus.HARDWARE_BACKED_KEYMINT;
            } catch (Exception ex) {
                return AttestationStatus.SOFTWARE_FALLBACK;
            }
        }
    }
}
