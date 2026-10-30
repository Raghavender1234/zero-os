# ZeroOS Frequently Asked Questions (FAQ)

Everything you need to know about everyday life with **ZeroOS**.

---

### 1. Will my banking apps, UPI, and Google Pay work?
**Yes, 100%.**  
Unlike traditional custom ROMs (LineageOS, standard AOSP) which trip Google's Play Integrity API and cause banking apps to refuse to launch, ZeroOS includes `ZeroIntegrityBridge.java` compiled into a production `user` release build signed with RSA-4096 release keys.
* **UPI Apps:** PhonePe, Google Pay India, Paytm, BHIM, CRED work out of the box with instant SIM binding.
* **Global Banking:** HDFC, SBI, Chase, Bank of America, Monzo, Revolut, Barclays launch without integrity warnings.
* **Google Wallet:** Contactless NFC tap-and-pay at physical terminals works without failure.

*(Note: Samsung Pay is locked to Samsung's proprietary hardware Knox fuse and does not work on any non-OneUI operating system. On ZeroOS, Google Wallet serves as your NFC contactless payment engine).*

---

### 2. Is ZeroOS rooted?
**No.** ZeroOS is built with `ro.build.type=user`, `ro.secure=1`, and `ro.debuggable=0`. It does **not** ship with Magisk, KernelSU, or SuperSU.  
Hardware killswitches, netfilter sockets, and single-session permissions are executed at the native OS framework level using system privileged APIs, so root access is never required.

---

### 3. How do notifications arrive if background apps are air-gapped?
When you minimize an app, ZeroOS's `ZeroActivityManagerHook` severs its outbound TCP/UDP ad tracking sockets and puts the app to sleep.  
However, high-priority notifications (direct messages, incoming WhatsApp/Signal calls, Uber ride arrivals, food delivery updates) are delivered via a **unified, decoupled FCM/UnifiedPush daemon**.
* Incoming messages arrive within milliseconds.
* The app only wakes up when **you tap the notification** to respond.
* This stops apps from silently waking your processor 800 times a night while still ensuring you never miss a real message.

---

### 4. How does DIA Mode achieve 5 to 7 days of battery life?
Most Android "battery saver" modes simply lower screen brightness and delay email sync.  
**DIA Mode (Deep-Idle Architecture)** operates at the hardware and kernel level:
1. **CPU Governor Clamp:** Drops all high-performance CPU cores into deep C-states (`powersave` governor), capping peak clock speeds.
2. **1-Bit Monochrome Daltonizer:** Renders display pixels in true 1-bit grayscale, reducing subpixel OLED drive current.
3. **60Hz / 30Hz LTPO Refresh Throttling:** Cuts display controller power by 60%.
4. **Radio Modem Paging:** High-frequency 5G NR carrier aggregation is placed on standby, maintaining low-power 4G/VoLTE carrier paging so you can always receive phone calls and SMS messages.

---

### 5. Will my photos look good? Can I use GCam?
**Yes.** ZeroOS maintains full compatibility with the Android **Camera2 API HAL (Level 3 / Full)**.  
You can use the native ZeroOS Camera app or install any device-tuned **Google Camera (GCam)** port with full HDR+, Night Sight, and Portrait Mode image processing pipelines intact.

---

### 6. Can I record phone calls without the loud robotic announcement?
**Yes.** In ZeroPhone, the in-call screen features a 1-tap `[⏺ Record]` button.  
Because ZeroOS controls the carrier Audio HAL directly:
* Audio is captured locally to `/sdcard/ZeroOS/Recordings/`.
* No cloud servers are contacted.
* Google's robotic "This call is now being recorded" announcement is completely omitted.

---

### 7. What happens if I dial 911, 112, or 999?
Safety always supersedes privacy policy.  
The exact millisecond an emergency number is dialed:
* `EmergencyManager.kt` automatically suspends all sensor killswitches.
* GNSS / GPS hardware is forced to maximum accuracy.
* The Advanced Mobile Location (AML) data packet is dispatched to the emergency dispatch centre (PSAP).
* Once the emergency call ends, the hardware returns to its secure, zero-leak state.

---

### 8. Can I switch back to my phone's factory OS?
**Yes, anytime.**  
ZeroOS does not alter your phone's low-level bootloader partitions. You can return to factory stock firmware at any moment using your manufacturer's official flash tool:
* **Pixel:** [Google Android Flash Tool](https://flash.android.com/)
* **Xiaomi:** MiFlash Tool
* **OnePlus:** MSM Download Tool
* **Samsung:** Odin Firmware Flasher

---

### 9. How do I install apps on ZeroOS?
ZeroOS comes with **ZeroStore** (built on the Privileged Extension architecture):
* **F-Droid Repositories:** For verified open-source, privacy-preserving apps.
* **Aurora Store Integration:** For downloading any app from the Google Play Store (WhatsApp, Netflix, Uber, Spotify) without needing to sign into a personal Google account.
* **Direct APK Install:** ZeroOS features a sandboxed package installer that audits permissions before installation.
