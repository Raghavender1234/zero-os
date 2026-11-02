# ZeroOS on Samsung Galaxy A15: Complete Installation & Testing Guide

This guide covers flashing **ZeroOS** on the **Samsung Galaxy A15** (both 4G and 5G models).

---

## 1. Supported Device Hardware

| Model | SoC / Chipset | Architecture | Treble Target |
| :--- | :--- | :--- | :--- |
| **Galaxy A15 4G** (`SM-A155F`, `SM-A155M`) | MediaTek Helio G99 (`MT6789`) | ARM64-v8a | `arm64_ab` (VNDK 34) |
| **Galaxy A15 5G** (`SM-A156B`, `SM-A156E`, `SM-A156U`) | MediaTek Dimensity 6100+ (`MT6835`) | ARM64-v8a | `arm64_ab` (VNDK 34) |

> **Display:** 6.5" 90Hz Super AMOLED (1080 × 2340)  
> **Battery:** 5000 mAh  
> **Launch OS:** Android 14 (One UI 6.0) — *100% Project Treble Compliant*

---

## 2. Choosing Your Installation Method

We offer two distinct methods depending on your preference:

```
                              Which method should you use?
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
          Method A: DSU Sideloader                    Method B: Fastbootd Flash
         (Zero-Risk / No Data Loss)                  (Permanent ROM Replacement)
                    │                                             │
      • No bootloader unlocking needed              • Requires bootloader unlock
      • Knox warranty NOT tripped (0x0)             • Knox trips to 0x1 permanently
      • Dual-boots alongside stock One UI           • Replaces One UI completely
      • Restart phone anytime to exit               • Full native internal storage
```

---

## Method A: DSU Sideloader (Zero-Risk Dual Boot — Recommended First)

Android 14 supports Google's **Dynamic System Updates (DSU)**. This lets you boot ZeroOS into a virtual partition without wiping your stock Samsung apps or tripping your Knox e-fuse.

### Steps:
1. On your Galaxy A15, enable **Developer Options**:
   * Go to **Settings** > **About phone** > **Software information**.
   * Tap **Build number** 7 times until it says *"You are now a developer!"*.
2. Download and install **[DSU Sideloader](https://github.com/VegaBobo/DSU-Sideloader/releases)** (open-source tool).
3. Connect phone to PC and grant DSU permission via adb (one-time):
   ```bash
   adb shell pm grant com.vega.dsusideloader android.permission.WRITE_SECURE_SETTINGS
   ```
4. Transfer `ZeroOS_GalaxyA15_DSU.img.gz` (or `system.img`) to phone storage.
5. In DSU Sideloader:
   * Tap **Select File** > Choose the ZeroOS image.
   * Tap **Install**.
6. Once installation completes, check your notification shade:
   * A notification from Android System will say: **"Dynamic System Update is ready"**.
   * Tap **Restart**.
7. **Your Galaxy A15 boots into ZeroOS!**
   * Test calls, SMS, mobile data, Wi-Fi, camera, and the unbloated interface.
   * To return to stock One UI, simply reboot your phone normally.

---

## Method B: Native Fastbootd Flashing (Permanent Custom ROM)

*Applies to Global / International models (`SM-A155F`, `SM-A156B/E`). Note: US carrier models (`SM-A156U/U1`) usually have bootloaders locked by carriers.*

### Step 1: Unlock Bootloader
1. In **Developer Options**, toggle **OEM Unlocking** and **USB Debugging** to **ON**.
2. Power off the phone completely.
3. Hold **Volume Up + Volume Down** simultaneously and plug the phone into your PC via USB-C.
4. The phone enters Samsung's Teal Warning Screen:
   * **Long-press Volume Up** (Device Unlock Mode).
   * Press **Volume Up** again to confirm unlock.
   * *Note: The phone will factory reset and boot with an unlocked bootloader.*

### Step 2: Boot into Samsung `fastbootd`
Modern Samsung Android 14 devices have native `fastbootd` in recovery:
1. Power off the phone.
2. Hold **Volume Up + Power** while connected to PC to enter **Android Recovery**.
3. Use the volume keys to highlight **Enter fastboot** and press Power.
4. You are now in `fastbootd`. Verify connection on your PC:
   ```bash
   fastboot devices
   ```

### Step 3: Flash ZeroOS System Image
1. Flash the system partition:
   ```bash
   fastboot flash system system.img
   ```
2. Wipe user data to avoid One UI cache conflicts:
   ```bash
   fastboot -w
   ```
3. Reboot into ZeroOS:
   ```bash
   fastboot reboot
   ```

---

## 3. MediaTek & Samsung A15 Specific Hardware Fixes Bundled

ZeroOS includes pre-configured overrides in `aosp/device/samsung/a15/a15.mk` specifically for the A15:
* **Audio Routing:** Fixes MediaTek Bluetooth A2DP offload routing (`persist.bluetooth.a2dp_offload.disabled=true`).
* **90Hz AMOLED Display:** SurfaceFlinger dynamic refresh rate enabled (`ro.vendor.display.default_fps=90`).
* **Knox / TIMA Daemon Severing:** Shuts down Samsung background security telemetry (`ro.config.knox=v00`, `ro.config.tima=0`).
