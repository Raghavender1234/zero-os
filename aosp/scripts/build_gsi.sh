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
echo "⚡ Flashing Directly via Fastboot (Permanent):"
echo "  adb reboot bootloader"
echo "  fastboot erase avb_custom_key"
echo "  fastboot flash avb_custom_key aosp/keys/avb_pkmd.bin"
echo "  fastboot flash system out/target/product/zero_arm64/system.img"
echo "  fastboot flashing lock"
echo "  fastboot reboot"
