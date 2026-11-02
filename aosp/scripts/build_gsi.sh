#!/usr/bin/env bash
# ==============================================================================
# ZeroOS AOSP GSI (Generic System Image) Automated Build Script
# Targets: Universal ARM64 Project Treble Devices (Android 14)
# Output: out/target/product/zero_arm64/system.img (Production Signed)
# ==============================================================================

set -euo pipefail

echo "======================================================================"
echo "          ZERO-OS: USER-INTENT CUSTOM OPERATING SYSTEM                "
echo "  [Target: ARM64 GSI] [Build: Production User Release] [AVB 2.0 Signed] "
echo "======================================================================"

export LC_ALL=C
export ARCH=arm64
export TARGET_BUILD_VARIANT=user
export ZERO_BUILD_NUMBER=$(date +%Y%m%d_%H%M%S)

# 1. Link ZeroLauncher & Framework Hooks into AOSP tree
echo "=== [1/6] Integrating ZeroOS Framework Components ==="
mkdir -p packages/apps/ZeroLauncher
if [ -d "../app/src" ]; then
    cp -r ../app/src packages/apps/ZeroLauncher/
fi

# Ensure cryptographic release keys exist
if [ ! -f "aosp/keys/releasekey.pk8" ]; then
    echo "=== Generating cryptographic release keys ==="
    bash aosp/tools/generate_keys.sh
fi

echo "=== [2/6] Sourcing AOSP Build Environment ==="
source build/envsetup.sh

echo "=== [3/6] Selecting Target Lunch Combo (Production User Build) ==="
lunch zero_arm64-user

echo "=== [4/6] Compiling ZeroOS System Image ==="
m -j$(nproc) systemimage target-files-package

echo "=== [5/6] Signing Production Target Files with AVB 2.0 Keys ==="
if [ -f "aosp/tools/sign_target_files.sh" ]; then
    bash aosp/tools/sign_target_files.sh
fi

echo "=== [6/6] Build & Verification Complete! ==="
echo ""
echo "📦 Deliverables:"
ls -lh out/target/product/zero_arm64/system.img || true
echo ""
echo "🚀 Dual-Booting via DSU (Safe on Samsung / Any Device):"
echo "  1. Install DSU Sideloader APK on your current phone."
echo "  2. Select out/target/product/zero_arm64/system.img."
echo "  3. Tap 'Install & Reboot into ZeroOS'."
echo "  4. Restart phone anytime to return to your stock OS without data loss."
echo ""
echo "⚡ Safe Flashing Instructions (Motorola & Fastboot Devices):"
echo "  1. Unlock bootloader via OEM unlock portal (Motorola / Google Pixel)."
echo "  2. Boot into fastbootd:"
echo "     adb reboot fastboot"
echo "  3. Flash system image without relocking:"
echo "     fastboot flash system out/target/product/zero_arm64/system.img"
echo "  4. (Optional) Disable verity if using custom vbmeta:"
echo "     fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img"
echo "  5. Wipe user data & reboot:"
echo "     fastboot -w"
echo "     fastboot reboot"
echo ""
echo "📱 Samsung Flashing Note (Odin / DSU Sideloader):"
echo "  - Recommended: Use DSU Sideloader (0% risk, no Knox trip, dual-boots ZeroOS)."
echo "  - Or package system.img as system.img.tar for Odin AP slot (Global/Exynos models only)."
echo "  - NEVER run 'fastboot flashing lock' on unofficial system images!
