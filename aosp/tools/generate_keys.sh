#!/usr/bin/env bash
# ==============================================================================
# ZeroOS AVB 2.0 (Android Verified Boot) Release Key Generator
# Creates cryptographic RSA-4096 keys to sign production ROM builds.
# Enables bootloader relocking in the secure 'green' state for:
# • Google Play Integrity (MEETS_DEVICE_INTEGRITY)
# • UPI (PhonePe, Paytm, Google Pay)
# • Global Mobile Banking Apps
# ==============================================================================

set -euo pipefail

KEY_DIR="aosp/keys"
mkdir -p "${KEY_DIR}"

SUBJECT="/C=US/ST=California/L=SanFrancisco/O=ZeroOS/OU=ReleaseEngineering/CN=ZeroOSProduction/emailAddress=security@zero-os.org"

echo "🔐 [ZeroOS Security] Generating RSA-4096 cryptographic release keys..."

for KEY in releasekey platform shared media networkstack avb; do
    if [[ ! -f "${KEY_DIR}/${KEY}.pk8" ]]; then
        echo "--> Generating key: ${KEY}"
        # 1. Generate RSA-4096 private key
        openssl genrsa -out "${KEY_DIR}/${KEY}.key" 4096
        
        # 2. Generate X.509 certificate
        openssl req -new -x509 -key "${KEY_DIR}/${KEY}.key" \
            -out "${KEY_DIR}/${KEY}.x509.pem" \
            -days 10000 \
            -subj "${SUBJECT}"
        
        # 3. Convert to PKCS#8 DER format for Android build tools
        openssl pkcs8 -topk8 -inform PEM -outform DER \
            -in "${KEY_DIR}/${KEY}.key" \
            -out "${KEY_DIR}/${KEY}.pk8" \
            -nocrypt
    else
        echo "--> Key ${KEY} already exists. Skipping."
    fi
done

# Extract AVB 2.0 public key for fastboot bootloader enrollment
echo "--> Generating avb_pkmd.bin for bootloader relocking..."
if command -v avbtool >/dev/null 2>&1; then
    avbtool extract_public_key --key "${KEY_DIR}/avb.key" --output "${KEY_DIR}/avb_pkmd.bin"
    echo "✅ avb_pkmd.bin successfully created! (Flash with: fastboot erase avb_custom_key && fastboot flash avb_custom_key avb_pkmd.bin)"
else
    echo "⚠️ avbtool not found on host. Will be extracted during AOSP container build."
fi

echo "🎉 All cryptographic keys generated successfully in ${KEY_DIR}!"
