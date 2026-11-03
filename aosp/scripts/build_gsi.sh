#!/usr/bin/env bash
# ==============================================================================
# ZeroOS AOSP GSI (Generic System Image) Automated Build Script
# Targets: Universal ARM64 Project Treble Devices (Android 14)
# Output: out/target/product/zero_arm64/system.img (Production Signed)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AOSP_ROOT="${AOSP_ROOT:-${REPO_ROOT}/aosp}"

echo "======================================================================"
echo "          ZERO-OS: USER-INTENT CUSTOM OPERATING SYSTEM                "
echo "  [Target: ARM64 GSI] [Build: Production User Release] [AVB 2.0 Signed] "
echo "  Repo Root: ${REPO_ROOT}"
echo "  AOSP Root: ${AOSP_ROOT}"
echo "======================================================================"

export LC_ALL=C
export ARCH=arm64
export TARGET_BUILD_VARIANT=user
export ZERO_BUILD_NUMBER=$(date +%Y%m%d_%H%M%S)

cd "${AOSP_ROOT}"

# 1. Copy ZeroOS Framework Sources into AOSP frameworks/base
echo "=== [1/6] Integrating ZeroOS Framework Files into AOSP ==="
mkdir -p "${AOSP_ROOT}/frameworks/base/core/java/android/os"
mkdir -p "${AOSP_ROOT}/frameworks/base/services/core/java/com/android/server/am"
mkdir -p "${AOSP_ROOT}/frameworks/base/services/core/java/com/android/server/appop"
mkdir -p "${AOSP_ROOT}/packages/apps/ZeroLauncher"

if [ -d "${REPO_ROOT}/aosp/frameworks/base/core/java/android/os" ]; then
    cp -rf "${REPO_ROOT}/aosp/frameworks/base/core/java/android/os/"*.java "${AOSP_ROOT}/frameworks/base/core/java/android/os/" 2>/dev/null || true
fi
if [ -d "${REPO_ROOT}/aosp/frameworks/base/services/core/java/com/android/server/am" ]; then
    cp -rf "${REPO_ROOT}/aosp/frameworks/base/services/core/java/com/android/server/am/"*.java "${AOSP_ROOT}/frameworks/base/services/core/java/com/android/server/am/" 2>/dev/null || true
fi
if [ -d "${REPO_ROOT}/aosp/frameworks/base/services/core/java/com/android/server/appop" ]; then
    cp -rf "${REPO_ROOT}/aosp/frameworks/base/services/core/java/com/android/server/appop/"*.java "${AOSP_ROOT}/frameworks/base/services/core/java/com/android/server/appop/" 2>/dev/null || true
fi

if [ -d "${REPO_ROOT}/app/src" ]; then
    cp -rf "${REPO_ROOT}/app/src" "${AOSP_ROOT}/packages/apps/ZeroLauncher/"
fi

# 2. Apply Framework Patches to frameworks/base
echo "=== [2/6] Applying Framework Patches to frameworks/base ==="
PATCH_DIR="${REPO_ROOT}/aosp/patches/frameworks_base"
if [ -d "${AOSP_ROOT}/frameworks/base/.git" ] && [ -d "${PATCH_DIR}" ]; then
    for patch in "${PATCH_DIR}"/*.patch; do
        if [ -f "$patch" ]; then
            patch_name=$(basename "$patch")
            echo "Checking patch: ${patch_name}"
            if git -C "${AOSP_ROOT}/frameworks/base" apply --check "$patch" 2>/dev/null; then
                echo "Applying patch: ${patch_name}"
                git -C "${AOSP_ROOT}/frameworks/base" apply "$patch"
            else
                if git -C "${AOSP_ROOT}/frameworks/base" apply --reverse --check "$patch" 2>/dev/null; then
                    echo "Patch ${patch_name} is already applied."
                else
                    echo "ERROR: Failed to apply framework patch: ${patch_name}"
                    exit 1
                fi
            fi
        fi
    done
fi

# Ensure cryptographic release keys exist
if [ ! -f "${AOSP_ROOT}/keys/releasekey.pk8" ]; then
    echo "=== Generating cryptographic release keys ==="
    bash "${AOSP_ROOT}/tools/generate_keys.sh"
fi

echo "=== [3/6] Sourcing AOSP Build Environment ==="
if [ ! -f "build/envsetup.sh" ]; then
    echo "ERROR: AOSP build/envsetup.sh not found in ${AOSP_ROOT}"
    echo "Please set AOSP_ROOT to your initialized Android 14 source directory."
    exit 1
fi
source build/envsetup.sh

echo "=== [4/6] Selecting Target Lunch Combo (Production User Build) ==="
lunch zero_arm64-user

echo "=== [5/6] Compiling ZeroOS System Image ==="
m -j$(nproc) systemimage target-files-package

# 6. Mandatory Release Signing
echo "=== Signing Production Target Files with AVB 2.0 Keys ==="
if [ ! -f "${AOSP_ROOT}/tools/sign_target_files.sh" ]; then
    echo "ERROR: Release signing script missing at ${AOSP_ROOT}/tools/sign_target_files.sh"
    exit 1
fi
bash "${AOSP_ROOT}/tools/sign_target_files.sh"

OUTPUT_IMG="out/target/product/zero_arm64/system.img"
if [ ! -f "${OUTPUT_IMG}" ]; then
    echo "ERROR: Build failed - ${OUTPUT_IMG} was not generated."
    exit 1
fi

echo "=== [6/6] Build & Verification Complete! ==="
echo ""
echo "📦 Output Deliverables:"
ls -lh "${OUTPUT_IMG}"
echo ""
echo "⚡ Safe Flashing Instructions (Motorola & Fastboot Devices):"
echo "  1. Unlock bootloader via OEM unlock portal (Motorola / Google Pixel)."
echo "  2. Boot into fastbootd:"
echo "     adb reboot fastboot"
echo "  3. Flash system image without relocking:"
echo "     fastboot flash system ${OUTPUT_IMG}"
echo "  4. (Optional) Disable verity if using custom vbmeta:"
echo "     fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img"
echo "  5. Wipe user data & reboot:"
echo "     fastboot -w"
echo "     fastboot reboot"
echo ""
echo "📱 Samsung Flashing Note (Galaxy A15 / One UI):"
echo "  - Recommended: Use DSU Sideloader (0% risk, no Knox trip, dual-boots ZeroOS)."
echo "  - Or package system.img as system.img.tar for Odin AP slot (Global/Exynos models only)."
echo "  - NEVER run 'fastboot flashing lock' on unofficial system images!"
