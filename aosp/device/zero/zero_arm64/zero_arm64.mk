# ZeroOS ARM64 Generic System Image (GSI) Product Definition
$(call inherit-product, $(SRC_TARGET_DIR)/product/generic_system_image.mk)

PRODUCT_NAME := zero_arm64
PRODUCT_DEVICE := zero_arm64
PRODUCT_BRAND := ZeroOS
PRODUCT_MANUFACTURER := ZeroOS
PRODUCT_MODEL := ZeroPhone GSI (ARM64)

# Overrides default system launcher with ZeroOS Shell
PRODUCT_PACKAGES += \
    ZeroLauncher \
    privapp-permissions-zeroos.xml \
    audio_killswitch

# Default System Properties for Maximum Battery Longevity
PRODUCT_SYSTEM_PROPERTIES += \
    ro.config.zero_os=true \
    ro.zero.battery_mode=extreme \
    ro.zero.oled_canvas=true \
    debug.sf.latch_unsignaled=1 \
    ro.surface_flinger.use_color_management=true \
    persist.sys.theme=monochrome
