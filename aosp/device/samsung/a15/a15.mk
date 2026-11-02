# ==============================================================================
# ZeroOS Device Configuration: Samsung Galaxy A15 (4G & 5G)
# Models: SM-A155F, SM-A155M (Helio G99), SM-A156B, SM-A156E (Dimensity 6100+)
# Architecture: ARM64-v8a (Treble ARM64 A/B, Android 14)
# ==============================================================================

PRODUCT_NAME := zero_samsung_a15
PRODUCT_DEVICE := a15
PRODUCT_BRAND := samsung
PRODUCT_MANUFACTURER := samsung
PRODUCT_MODEL := Galaxy A15 (ZeroOS)

# Inherit ZeroOS Common ARM64 System Image
$(call inherit-product, device/zero/zero_arm64/zero_arm64.mk)

# MediaTek MT6789 / MT6835 Hardware Adaptation Overrides
PRODUCT_PROPERTY_OVERRIDES += \
    ro.product.device=a15 \
    ro.build.product=a15 \
    ro.sf.lcd_density=450 \
    ro.surface_flinger.has_wide_color_display=true \
    ro.surface_flinger.has_HDR_display=false \
    ro.surface_flinger.max_frame_buffer_acquired_buffers=3 \
    ro.surface_flinger.set_idle_timer_ms=250 \
    ro.surface_flinger.set_touch_timer_ms=1000 \
    persist.sys.sf.native_mode=1 \
    persist.sys.sf.color_mode=0

# Disable Samsung Knox & TIMA Telemetry Sockets
PRODUCT_PROPERTY_OVERRIDES += \
    ro.config.knox=v00 \
    ro.config.tima=0 \
    ro.config.iccc_version=0 \
    ro.config.dmverity=false

# MediaTek Bluetooth A2DP & Audio Offload Fix
PRODUCT_PROPERTY_OVERRIDES += \
    persist.bluetooth.a2dp_offload.disabled=true \
    persist.sys.bt.offload=false \
    ro.audio.flinger_standbytime_ms=1000

# Super AMOLED 90Hz Refresh Rate Profiles
PRODUCT_PROPERTY_OVERRIDES += \
    ro.vendor.display.default_fps=90 \
    ro.vendor.display.dynamic_fps=true
