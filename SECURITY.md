# Security & Cryptographic Policy

ZeroOS takes security, memory safety, and verifiable privacy seriously. We treat security vulnerabilities with the highest priority.

---

## 1. Supported Versions

| Version | Base | Security Patch Level | Maintenance Status |
| :--- | :--- | :--- | :--- |
| **ZeroOS 1.x (Current)** | AOSP 14 / 15 | Monthly upstream merges | 🟢 Actively Supported |

---

## 2. Core Security Architecture

* **Cryptographic Root of Trust:** Custom RSA-4096 production release keys. No default AOSP test keys are permitted in build artifacts.
* **Android Verified Boot (AVB 2.0):** Cryptographically verifies `boot`, `system`, `vendor`, and `vbmeta` partitions before execution.
* **Single-Session Privilege Enforcement:** Hardware sensors (mic, camera, GNSS) and netfilter firewall policies are enforced by native kernel hooks (`cgroups`, `iptables`, `AppOpsService`).
* **Memory Safety:** Compiles native framework components with LLVM Clang's AddressSanitizer (ASan), ShadowCallStack, and Control Flow Integrity (CFI).

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability or privacy bypass in ZeroOS:

1. **Do not open a public GitHub issue.**
2. Send an encrypted email to the ZeroOS Security Team at:
   `security@zero-os.org` (or open a confidential security advisory on GitHub).
3. Include:
   * Device model and ZeroOS build tag (`ro.build.display.id`).
   * Step-by-step reproduction steps or proof-of-concept (PoC) script.
   * Potential impact of the issue.

### Response Timeline
* **Initial acknowledgment:** Within 24 hours.
* **Triage & severity assessment:** Within 72 hours.
* **Patch release & CVE allocation:** Within 14 days.

We practice coordinated vulnerability disclosure and will credit researchers in our public release notes.
