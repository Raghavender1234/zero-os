#!/usr/bin/env bash
# ==============================================================================
# ZeroOS Android 14 Emulator Automated Build Script (x86_64)
# Targets: Virtual Device (Android Studio Emulator / Cuttlefish)
# Output: out/target/product/emulator_x86_64/system.img
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AOSP_ROOT="${AOSP_ROOT:-${REPO_ROOT}/aosp}"

echo "======================================================================"
echo "          ZERO-OS: EMULATOR BUILD & VALIDATION ENGINE                 "
echo "  [Target: x86_64 Emulator] [Build: userdebug] [ZeroOS Core Active]     "
echo "  Repo Root: ${REPO_ROOT}"
echo "  AOSP Root: ${AOSP_ROOT}"
echo "======================================================================"

export LC_ALL=C
export ARCH=x86_64
export TARGET_BUILD_VARIANT=userdebug

cd "${AOSP_ROOT}"

# 1. Integrate Framework Files
echo "=== [1/5] Integrating ZeroOS Framework Files ==="
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
echo "=== [2/5] Applying Framework Patches to frameworks/base ==="
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

echo "=== [3/5] Sourcing AOSP Environment ==="
if [ ! -f "build/envsetup.sh" ]; then
    echo "ERROR: AOSP build/envsetup.sh not found in ${AOSP_ROOT}"
    echo "Please set AOSP_ROOT to your initialized Android 14 source directory."
    exit 1
fi
source build/envsetup.sh

echo "=== [4/5] Selecting Target Lunch Combo (zero_emulator_x86_64-userdebug) ==="
lunch zero_emulator_x86_64-userdebug

echo "=== [5/5] Compiling Emulator Target Images ==="
m -j$(nproc)

echo ""
echo "======================================================================"
echo "✅ ZeroOS Emulator Build Succeeded!"
echo "To boot the emulator and verify ZeroOS:"
echo "  emulator -no-snapshot -wipe-data -verbose"
echo ""
echo "To verify boot completion and privacy logs:"
echo "  adb wait-for-device"
echo "  adb shell getprop sys.boot_completed"
echo "  adb logcat -s ZeroActivityManagerHook ZeroAppOpsHook"
echo "======================================================================"
