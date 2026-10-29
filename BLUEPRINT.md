# 📱 ZeroOS: Master Product & System Specification

> **Vision:** A distraction-free, zero-surveillance mobile operating system with 4-day battery longevity, controlled through natural human language and 1-tap hardware toggles.

---

## 1. Executive Summary & Core Pillars

| Pillar | The Problem It Solves | The ZeroOS Solution |
| :--- | :--- | :--- |
| **1. Universal Command Shell** | Android settings are a labyrinth of 50+ menus; finding basic toggles takes 7 taps. | Long-press power button opens a **Unified Command Terminal**. Type `restart`, `flashlight`, `grayscale` to execute instantly. |
| **2. Kernel Anti-Surveillance** | Apps secretly listen to microphones and send tracking packets in the background. | Natural language firewall (`cut data to instagram`, `mute mic for whatsapp`) enforced at the Linux kernel level. |
| **3. Stealth Notifications** | Users want DMs and alerts without giving apps continuous microphone access. | Decouples push alerts from app sensor access. DMs arrive via Google FCM, but mic hardware stays dead. |
| **4. Physical OLED Battery Saver** | Modern 6,000 mAh batteries die in 18 hours due to lighting 4M pixels at 120Hz. | **Micro-Window Mode:** Shuts off 80% of the OLED screen (0.00 Watts). Refresh drops to 1Hz–10Hz. Battery lasts 3–5 days. |

---

## 2. Complete Feature Specification

### A. The Universal System Command Bar (Power-Button Hold)
* **Access Method:** Long-press the physical power button (or swipe up from the bottom).
* **Input Box:** Single minimalist search line with instant sub-5ms response time.
* **Conversational Confirmation Cards:** For high-impact settings, it doesn't just toggle silently—it renders a clean confirmation dialog explaining the feature:
  * *User types:* `turn on grayscale`
  * *Card pop-up:*
    ```
    ┌────────────────────────────────────────────────────────┐
    │ ⚡ SYSTEM ACTION CONFIRMATION                          │
    │ Enable Grayscale Mode?                                 │
    │ • Converts all display output to monochrome.           │
    │ • Eliminates visual dopamine addiction triggers.       │
    │ • Saves up to 18% OLED battery power.                  │
    │                                                        │
    │       [ ✅ YES, ENABLE ]        [ ❌ CANCEL ]          │
    └────────────────────────────────────────────────────────┘
    ```
* **Direct Hardware Actions:**
  * `turn on flash` / `torch` $\rightarrow$ activates camera flash LED immediately.
  * `restart` / `reboot` $\rightarrow$ triggers system restart.
  * `about phone` $\rightarrow$ displays hardware specs, battery health, and kernel version.
  * `bluetooth off` / `wifi off` $\rightarrow$ severs wireless chips.

---

### B. Natural Anti-Surveillance & Hardware Killswitches
* **Human-First Syntax:**
  * `cut data for instagram, tiktok` $\rightarrow$ drops packets at Linux kernel level (`iptables`).
  * `mute mic for whatsapp` $\rightarrow$ revokes audio recording register via `appops`.
  * `freeze facebook` $\rightarrow$ suspends app execution via `pm suspend` (0 CPU / 0 RAM).
  * `who is spying?` $\rightarrow$ audits background network sockets and prints active tracker IPs.
* **Stealth Notifications:**
  * Push alerts (DMs, mentions, delivery updates) arrive 100% reliably via system-level Google FCM.
  * The actual app remains frozen with microphone and camera hardware registers permanently locked.
* **1-Tap Action Cards:**
  * Searching or swiping any app reveals hardware toggles: `[Data: CUT]` `[Mic: BLOCKED]` `[Cam: BLOCKED]` `[Freeze App]`.
* **Autocomplete Slash Chips:**
  * Typing `/` shows suggested shortcuts: `[/cut-data]` `[/mute-mic]` `[/freeze]` `[/nokia-mode]` `[/spy-audit]`.

---

### C. Physical OLED Display & Battery Architecture
* **Micro-Window Mode (One-Thumb Canvas):**
  * Toggles a compact 2.5-inch active display area at the bottom of the screen.
  * Surrounding 80% of the OLED panel is rendered as `#000000` (physical pixel shutoff = 0 Watts).
* **E-Paper Refresh Throttling:**
  * When screen content is static, drops display refresh rate from 120Hz down to 1Hz–10Hz.
* **Monochrome & Amber Phosphor Themes:**
  * OLED Pure Black + Crisp Off-White.
  * Retro Amber / Cyberpunk Orange (lowest voltage subpixel draw).
* **"Nokia Mode" (Kernel Deep Sleep):**
  * Shuts down all non-essential background processes.
  * Puts the CPU into Linux C-states.
  * Only incoming cellular phone calls and SMS wake the device. Battery lasts 4 to 6 days.

---

### D. Distribution & Installation Strategy
1. **WebUSB 1-Click Browser Installer (`install.zero-os.org`):**
   * Non-technical users connect their phone to PC via USB cable.
   * Google Chrome WebUSB detects the device and flashes the OS image in 3 minutes without terminal commands.
2. **Pre-Installed "ZeroPhone" Hardware:**
   * Commercial refurbished devices (Pixel 6a/7a, Motorola G) shipped pre-flashed in a box, ready to use out of the box with zero Google account setup.

---

## 3. System Architecture & Technical Stack

```
┌────────────────────────────────────────────────────────┐
│  USER INTERACTION LAYER (Jetpack Compose / Kotlin)     │
│  • 120Hz Ultra-fluid Minimalist Home Shell             │
│  • Micro-Window Sub-Display Renderer                   │
│  • Confirmation Action Cards & Slash Chips             │
├────────────────────────────────────────────────────────┤
│  NATURAL LANGUAGE INTENT ENGINE                        │
│  • Sub-millisecond on-device regex & keyword parser    │
│  • Translates human commands to system action payloads │
├────────────────────────────────────────────────────────┤
│  HARDWARE & SYSTEM BUS (Kotlin / Java)                 │
│  • CameraManager (Flashlight)                          │
│  • PowerManager (Reboot, Deep Doze)                    │
│  • Settings.Secure (Daltonizer / Grayscale)            │
├────────────────────────────────────────────────────────┤
│  KERNEL ENFORCEMENT LAYER (Shell / JNI / Root Bridge)  │
│  • `iptables` / `nftables` (Per-UID packet dropping)   │
│  • `cmd appops` (Hardware register sensor denial)      │
│  • `pm suspend` (App hibernation)                      │
└────────────────────────────────────────────────────────┘
```
