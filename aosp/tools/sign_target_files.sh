#!/usr/bin/env bash
# ==============================================================================
# ZeroOS Production Image Signer
# Signs target-files package and GSI images with production RSA-4096 release keys.
# ==============================================================================

set -euo pipefail

KEY_DIR="aosp/keys"
TARGET_FILES="${1:-out/target/product/zero_arm64/obj/PACKAGING/target_files_intermediates/zero_arm64-target_files.zip}"
SIGNED_TARGET_FILES="out/target/product/zero_arm64/signed-target-files.zip"

if [[ ! -d "${KEY_DIR}" || ! -f "${KEY_DIR}/releasekey.pk8" ]]; then
    echo "❌ Error: Production keys not found in ${KEY_DIR}. Run generate_keys.sh first."
    exit 1
fi

echo "🔏 [ZeroOS Signer] Signing target-files with private release keys..."

sign_target_files_apks \
    -o \
    -d "${KEY_DIR}" \
    --avb_vbmeta_key "${KEY_DIR}/avb.key" \
    --avb_vbmeta_algorithm SHA256_RSA4096 \
    --extra_apks AdServicesApk.apk="${KEY_DIR}/releasekey" \
    "${TARGET_FILES}" \
    "${SIGNED_TARGET_FILES}"

echo "🔨 Generating signed fastboot flashable GSI image..."
img_from_target_files "${SIGNED_TARGET_FILES}" out/target/product/zero_arm64/zero-os-arm64-signed.zip

echo "✅ Signed ZeroOS production package generated successfully at out/target/product/zero_arm64/zero-os-arm64-signed.zip"
