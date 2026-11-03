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

# 1. Integrate Framework Patches
echo "=== [1/6] Applying ZeroOS Framework Hooks & Overlays ==="
mkdir -p packages/apps/ZeroLauncher
if [ -d "${REPO_ROOT}/app/src" ]; then
    cp -r "${REPO_ROOT}/app/src" packages/apps/ZeroLauncher/
fi

# Ensure cryptographic release keys exist
if [ ! -f "${AOSP_ROOT}/keys/releasekey.pk8" ]; then
    echo "=== Generating cryptographic release keys ==="
    bash "${AOSP_ROOT}/tools/generate_keys.sh"
fi

echo "=== [2/6] Sourcing AOSP Build Environment ==="
if [ ! -f "build/envsetup.sh" ]; then
    echo "ERROR: AOSP build/envsetup.sh not found in ${AOSP_ROOT}"
    echo "Please set AOSP_ROOT to your initialized Android 14 source directory."
    exit 1
fi
source build/envsetup.sh

echo "=== [3/6] Selecting Target Lunch Combo (Production User Build) ==="
lunch zero_arm64-user

echo "=== [4/6] Compiling ZeroOS System Image ==="
m -j$(nproc) systemimage target-files-package

# 5. Mandatory Release Signing
echo "=== [5/6] Signing Production Target Files with AVB 2.0 Keys ==="
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
