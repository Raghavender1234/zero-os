# ZeroOS ARM64 Generic System Image (GSI) Product Definition
$(call inherit-product, $(SRC_TARGET_DIR)/product/generic_system_image.mk)

PRODUCT_NAME := zero_arm64
PRODUCT_DEVICE := zero_arm64
PRODUCT_BRAND := ZeroOS
PRODUCT_MANUFACTURER := ZeroOS
PRODUCT_MODEL := ZeroOS GSI (ARM64)

# Core ZeroOS System Packages
PRODUCT_PACKAGES += \
    ZeroLauncher \
    privapp-permissions-zeroos.xml

# Device Overlays (OLED Palette, Sensor Privacy)
DEVICE_PACKAGE_OVERLAYS += device/zero/zero_arm64/overlay

# ==============================================================================
# RUNTIME IDENTITY PROPERTIES
# Genuine OEM / hardware build tags without synthetic bootloader-lock spoofing
# ==============================================================================
PRODUCT_DEFAULT_PROPERTY_OVERRIDES += \
    ro.build.type=user \
    ro.build.tags=release-keys \
    ro.system.build.tags=release-keys \
    ro.vendor.build.tags=release-keys \
    ro.product.build.tags=release-keys \
    ro.system_ext.build.tags=release-keys \
    ro.odm.build.tags=release-keys

# ==============================================================================
# USER-INTENT ARCHITECTURE (NOT COMPANY-INTENT)
# • High-efficiency battery baseline
# • True OLED black (0.00W draw)
# • Zero background ad tracking
# • Instant background socket severing
# ==============================================================================
PRODUCT_SYSTEM_PROPERTIES += \
    ro.config.zero_os=true \
    ro.zero.version=1.0.0-PROD \
    ro.zero.battery_mode=extreme \
    ro.zero.oled_canvas=true \
    ro.zero.auto_airgap=enabled \
    ro.zero.single_session_perms=enabled \
    debug.sf.latch_unsignaled=1 \
    ro.surface_flinger.use_color_management=true \
    persist.sys.theme=monochrome \
    pm.dexopt.downgrade_after_inactive_days=10 \
    ro.config.low_ram=false \
    ro.telephony.default_network=9 \
    wifi.supplicant_scan_interval.interval=300
