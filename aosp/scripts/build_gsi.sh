#!/usr/bin/env bash
# ==============================================================================
# ZeroOS AOSP GSI (Generic System Image) Automated Build Script
# Targets: Universal ARM64 Project Treble Devices
# Output: out/target/product/zero_arm64/system.img
# ==============================================================================

set -e

echo "=== [1/5] Initializing AOSP Environment ==="
export LC_ALL=C
export ARCH=arm64
export ZERO_BUILD_NUMBER=$(date +%Y%m%d_%H%M%S)

# Link ZeroLauncher into AOSP tree
if [ ! -d "packages/apps/ZeroLauncher/src" ]; then
    echo "=== Linking ZeroLauncher into packages/apps/ZeroLauncher ==="
    mkdir -p packages/apps/ZeroLauncher
    cp -r ../app/src packages/apps/ZeroLauncher/
fi

echo "=== [2/5] Sourcing Build Environment ==="
source build/envsetup.sh

echo "=== [3/5] Selecting Target Lunch Combo ==="
lunch zero_arm64-userdebug

echo "=== [4/5] Compiling ZeroOS System Image ==="
m -j$(nproc) systemimage

echo "=== [5/5] Build Complete! ==="
echo "Flashable system image created at:"
ls -lh out/target/product/zero_arm64/system.img
echo ""
echo "To flash to an unlocked Android phone via Fastboot:"
echo "  adb reboot bootloader"
echo "  fastboot flash system out/target/product/zero_arm64/system.img"
echo "  fastboot reboot"
