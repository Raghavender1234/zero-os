# Contributing to ZeroOS

We welcome developers, security researchers, kernel hackers, UI designers, and translators to help build the future of user-first mobile computing.

---

## 1. Code of Conduct & Core Philosophy

Every pull request must adhere to the **ZeroOS Axiom**:
> *"Everything should feel like Android — yet make things work as the user intended, not what the company intended."*

### Non-Negotiable Standards:
1. **Never break everyday user utility:** Changes must not break Google Pay, UPI payments, phone calls, local recording, Spotify background music, or turn-by-turn navigation.
2. **Zero Telemetry:** No analytical pings, phone-home beacons, crash reporters, or tracking identifiers may ever be committed.
3. **No Root Requirement:** Features must be architected via native AOSP privileged APIs or Linux kernel hooks, not by granting su/root privileges to user apps.
4. **Clean Typography & Minimalist UX:** Avoid jargon in UI elements (use "DIA Mode", not verbose acronym descriptions).

---

## 2. Setting Up the Local Development Environment

### Prerequisites
* **Operating System:** Ubuntu 22.04 LTS / 24.04 LTS (or Debian 12 / Arch Linux / Windows WSL2).
* **JDK:** OpenJDK 17.
* **Storage:** 250 GB fast NVMe SSD for full AOSP compilation; 15 GB for ZeroLauncher & SystemUI development.
* **RAM:** Minimum 32 GB RAM (64 GB recommended for parallel `ninja` builds).

### Building the System Shell (ZeroLauncher & SystemUI)
```bash
# Clone the repository
git clone https://github.com/Raghavender1234/zero-os.git
cd zero-os

# Build the Compose APK
./gradlew assembleDebug

# Install on connected device or emulator
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Compiling the Full AOSP GSI Image
```bash
# Generate AVB 2.0 cryptographic keys
bash aosp/tools/generate_keys.sh

# Run automated GSI compiler
bash aosp/scripts/build_gsi.sh
```

---

## 3. Submitting a Pull Request (PR)

1. **Fork the repo** to your GitHub profile.
2. **Create a topic branch:**
   ```bash
   git checkout -b feat/device-support-pixel9
   ```
3. **Commit with conventional commit prefixes:**
   * `feat:` A new feature or device tree port.
   * `fix:` A bug fix in kernel hooks or SystemUI.
   * `docs:` Documentation or translation improvements.
   * `perf:` Battery optimization or latency improvements.
4. **Push and open a PR** against the `main` branch.
5. All PRs must pass the automated GitHub Actions CI validation pipeline.
