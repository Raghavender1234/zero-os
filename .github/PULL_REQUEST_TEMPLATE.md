## 📱 ZeroOS Pull Request

### Summary of Changes
<!-- Describe what this PR does and why it is needed -->

### Architectural Compliance Checklist
- [ ] **Everyday Utility**: Does not break Google Pay, UPI, VoLTE calls, Spotify background audio, or GPS turn-by-turn navigation.
- [ ] **Zero Telemetry**: No background tracking beacons, analytical pings, or telemetry libraries introduced.
- [ ] **Zero Root Dependency**: Operates via documented AOSP privileged APIs or native kernel hooks without needing superuser privileges.
- [ ] **Battery Impact**: Does not introduce persistent CPU wake-locks or violate the 11.1 mA standby baseline.

### Testing & Verification
<!-- Describe on which device(s) or GSI testbed this was tested, following TESTING.md -->
- Device:
- Android Version Base:
- Play Integrity Status:
