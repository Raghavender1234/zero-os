# ZeroOS Device Compatibility & Hardware Support Matrix

ZeroOS is engineered on top of Google's **Project Treble Generic System Image (GSI)** architecture (ARM64-v8a / ARM64-v9a). Any Android device launched with **Android 9 (Pie) or higher** and a compliant vendor partition (`vendor.img`) can run ZeroOS.

---

## 1. Official Tier 1: Verified Daily Drivers (Gold Standard)

These devices have undergone end-to-end testing with all ZeroOS features verified: **11.1 mA standby**, **AVB 2.0 Green boot**, **VoLTE/5G calls**, **1-tap call recording**, and **UPI / Google Pay**.

| Manufacturer | Model | Codename | SoC | Android Base | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google** | Pixel 8 / 8 Pro | `shiba` / `husky` | Google Tensor G3 | AOSP 14 / 15 | ✅ Fully Verified | Full AVB custom key re-locking supported |
| **Google** | Pixel 7 / 7a / 7 Pro | `panther` / `lynx` / `cheetah` | Google Tensor G2 | AOSP 14 | ✅ Fully Verified | Recommended entry device |
| **Google** | Pixel 6 / 6a / 6 Pro | `oriole` / `bluejay` / `raven` | Google Tensor G1 | AOSP 14 | ✅ Fully Verified | Exceptional 5-day DIA Mode battery |
| **Nothing** | Phone (2) | `pong` | Snapdragon 8+ Gen 1 | AOSP 14 | ✅ Fully Verified | Glyph interface mapped to notification events |
| **Nothing** | Phone (2a) | `pacman` | Dimensity 7200 Pro | AOSP 14 | ✅ Fully Verified | VoLTE and 5G Dual SIM verified |
| **OnePlus** | OnePlus 11 / 12 | `salami` / `waffle` | Snapdragon 8 Gen 2/3 | AOSP 14 | ✅ Fully Verified | Alert slider maps to Sound/Vibrate/Silent |
| **Motorola** | Edge 40 / 50 Pro | `rtwo` / `tetris` | Dimensity / Snapdragon | AOSP 14 | ✅ Fully Verified | Clean near-stock vendor layer |
| **Xiaomi** | POCO F5 / F6 | `marble` / `peridot` | Snapdragon 7+ Gen 2 / 8s Gen 3 | AOSP 14 | ✅ Fully Verified | Requires 7-day Mi Unlock waiting period |

---

## 2. Official Tier 2: Community Certified Devices

Tested by community contributors with functional core telephony, data, and hardware sensors.

| Manufacturer | Model | SoC | Treble Flavour | Status | Known Quirk / Fix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Samsung** | Galaxy S23 / S24 | Snapdragon 8 Gen 2/3 | `arm64_bgN` | ✅ Community Verified | Google Pay works; Samsung Pay permanently disabled due to Knox fuse |
| **Samsung** | Galaxy A54 / A55 | Exynos 1380 / 1480 | `arm64_bgN` | ✅ Community Verified | Audio in-call fix enabled via overlay |
| **Xiaomi** | Redmi Note 12 / 13 | Snapdragon 685 / Dimensity | `arm64_bvN` | ✅ Community Verified | Brightness curve patched in overlay |
| **Sony** | Xperia 1 V / 5 V | Snapdragon 8 Gen 2 | `arm64_bgN` | ✅ Community Verified | Dedicated shutter button supported |
| **Fairphone** | Fairphone 4 / 5 | Snapdragon 750G / QCM6490 | `arm64_bvN` | ✅ Community Verified | 100% open-source driver stack |
| **Asus** | Zenfone 9 / 10 | Snapdragon 8+ Gen 1 / 8 Gen 2 | `arm64_bgN` | ✅ Community Verified | Smart key power-button mapping |

---

## 3. Generic Hardware Requirements

If your specific phone is not listed above, it will still boot and run ZeroOS if it meets these criteria:

* **CPU Architecture:** 64-bit ARM (`arm64-v8a` or `arm64-v9a`).
* **Treble Compliance:** Launched with Android 10+ (Check with *Treble Check* app from F-Droid).
* **Partition Layout:** Dynamic Partitions (`super.img` with `system`, `vendor`, `product`).
* **RAM & Storage:** Minimum 4GB RAM and 64GB UFS storage.
* **Bootloader:** User-unlockable via standard OEM fastboot commands (`fastboot flashing unlock` or `fastboot oem unlock`).

---

## 4. Bootloader Relocking Support with AVB 2.0 Custom Keys

| OEM Brand | Custom Root of Trust Supported? | Can Re-lock Bootloader with ZeroOS? |
| :--- | :--- | :--- |
| **Google Pixel** | **YES** (`fastboot flashing set-active-key avb_pkmd.bin`) | ✅ **YES** (Full Green Verified Boot) |
| **Fairphone** | **YES** | ✅ **YES** |
| **Nothing** | **YES** (Experimental) | ⚠️ Test via fastboot first |
| **OnePlus** | **NO** (Only OEM keys allowed for re-lock) | ⚠️ Must stay unlocked (Yellow Boot) |
| **Xiaomi** | **NO** (Re-locking brick protection) | ⚠️ Must stay unlocked (Yellow Boot) |
| **Samsung** | **NO** (Knox efuse blown on unlock) | ⚠️ Must stay unlocked (Yellow Boot) |

> [!IMPORTANT]
> Never attempt to re-lock the bootloader on Xiaomi or Samsung devices running a custom GSI. Keep the bootloader unlocked; ZeroOS's `ZeroIntegrityBridge.java` still satisfies `MEETS_DEVICE_INTEGRITY` even with an unlocked bootloader!
