# ==============================================================================
# ZeroOS Android 14 Emulator Product Definition (x86_64)
# Targets: Android Studio Emulator / Cuttlefish Virtual Device
# Output: Standard bootable virtual system image with ZeroOS Core
# ==============================================================================

$(call inherit-product, $(SRC_TARGET_DIR)/product/sdk_phone_x86_64.mk)

PRODUCT_NAME := zero_emulator_x86_64
PRODUCT_DEVICE := emulator_x86_64
PRODUCT_BRAND := Android
PRODUCT_MANUFACTURER := Google
PRODUCT_MODEL := ZeroOS Virtual Device (x86_64)

# Core ZeroOS System Packages
PRODUCT_PACKAGES += \
    ZeroLauncher \
    privapp-permissions-zeroos.xml

# ZeroOS Core Runtime Properties (Development/Emulator Mode)
PRODUCT_SYSTEM_PROPERTIES += \
    ro.config.zero_os=true \
    ro.zero.version=1.0.0-EMU \
    ro.zero.environment=emulator \
    ro.zero.auto_airgap=enabled \
    ro.zero.single_session_perms=enabled \
    persist.sys.theme=monochrome
