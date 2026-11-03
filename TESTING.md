# ZeroOS Testing, Hardware Verification & Status Matrix

This document provides testing procedures and the current empirical verification status for **ZeroOS** across development targets:
1. **ZeroOS UI Simulator** (Web & Local Runtime)
2. **Android 14 Emulator** (`zero_emulator_x86_64`)
3. **ARM64 GSI & Physical Devices** (Samsung Galaxy A15, Motorola)

---

## 1. Status Taxonomy & Verification Legend

To maintain strict scientific and engineering integrity, features are classified under five verifiable stages:

| Status | Meaning |
| :--- | :--- |
| **`Planned`** | Feature specified in architectural blueprint; implementation not yet complete. |
| **`Implemented`** | Code written and integrated; awaiting compilation or hardware execution. |
| **`Simulator-Tested`** | Tested and verified in the ZeroOS interactive simulator runtime. |
| **`Emulator-Tested`** | Verified running on an Android 14 x86_64 emulator virtual device. |
| **`Device-Verified`** | Flashed and verified on physical phone hardware with recorded test logs. |

---

## 2. Feature Verification Status Matrix

| Component | Architecture & Mechanism | Status | Evidence / Test Note |
| :--- | :--- | :--- | :--- |
| **ZeroLauncher** | Compose-based Reachability UI, 0W OLED canvas | **Simulator-Tested** | Runs on `http://127.0.0.1:5077` & GitHub Pages |
| **Quick Chips & /direction** | Command Center autofill and solid state transitions | **Simulator-Tested** | Verified in headless browser test runs |
| **ZeroMaps Engine** | Offline OpenStreetMap vector SVG navigation | **Simulator-Tested** | Turn-by-turn maneuvers active without telemetry |
| **ZeroChat Client** | WhatsApp-style layout, 6-item attachment tray | **Simulator-Tested** | P2P message thread simulated cleanly |
| **ActivityManager Hook** | `ZeroActivityManagerHook` (socket drop on app exit) | **Implemented** | Source complete; patch in `aosp/patches/` |
| **AppOps Sensor Hook** | `ZeroAppOpsHook` (background mic/location restrict) | **Implemented** | Intercepts `checkOperation` & `noteOperation` |
| **Hard-Mute Persistence** | Disk persistence via `/data/system/zero_hard_mutes.txt` | **Implemented** | File I/O structure integrated; needs device test |
| **ZERO_AIRGAP Firewall** | Idempotent iptables custom chain | **Implemented** | Command verification added; kernel test planned |
| **Emulator Target** | `zero_emulator_x86_64-userdebug` | **Implemented** | Configured in `aosp/device/zero/zero_emulator/` |
| **Samsung A15 Target** | MediaTek Helio G99 / Dimensity 6100+ overlay | **Implemented** | Configured in `aosp/device/samsung/a15/` |
| **Battery (11.1 mA)** | Simulated standby power state model | **Simulator-Tested** | Mathematical simulation; physical test planned |
| **Play Integrity / Banking** | Real KeyMint / StrongBox Keystore attestation | **Planned** | No device spoofing; physical verification pending |

---

## 3. Step-by-Step Emulator Verification Procedures

Once the AOSP emulator image is compiled via `aosp/scripts/build_emulator.sh`:

### 3.1 Verify Boot Completion
```bash
adb wait-for-device
adb shell getprop sys.boot_completed
# Expected output: 1
```

### 3.2 Verify ZeroLauncher Installation
```bash
adb shell pm list packages | grep zeroos
# Expected output: package:com.zeroos.launcher
```

### 3.3 Verify Framework Hook Activity
```bash
adb logcat -s ZeroActivityManagerHook ZeroAppOpsHook
# Expected output on app background:
# [ZeroActivityManagerHook] App backgrounded. Severing network sockets via ZERO_AIRGAP chain.
```

### 3.4 Inspect Active AppOps States
```bash
adb shell dumpsys appops
# Confirms whether background packages show MODE_IGNORED for OP_RECORD_AUDIO and OP_COARSE_LOCATION
```

---

## 4. Hardware Attestation & Banking Notice

ZeroOS **does not inject fake Google Pixel identities** (`husky` / `walleye`) to trick Play Integrity. Such spoofing breaks vendor hardware HALs and is routinely blacklisted by Google.

* Devices with **unlocked bootloaders** may report `MEETS_BASIC_INTEGRITY` while failing `MEETS_DEVICE_INTEGRITY`.
* Testing of individual banking and payment apps (Google Pay, PhonePe, Chase, Monzo) will be conducted and reported transparently once physical hardware testing begins.
