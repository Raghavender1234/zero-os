import os
import sys
import json
import re

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_py_path = os.path.join(root, 'simulator', 'app.py')
    docs_dir = os.path.join(root, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    out_html = os.path.join(docs_dir, 'index.html')

    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract HTML_TEMPLATE
    start_tag = 'HTML_TEMPLATE = """\n'
    idx_start = content.find(start_tag)
    if idx_start == -1:
        start_tag = 'HTML_TEMPLATE = """'
        idx_start = content.find(start_tag)
    idx_start += len(start_tag)
    idx_end = content.find('"""\n\n@app.route')

    raw_html = content[idx_start:idx_end]

    # Client-side Mock Engine for GitHub Pages & static viewing
    # This intercepts fetch('/api/...') calls when running without a Flask server
    client_mock = """
  <!-- ZeroOS Client-Side Mock Engine for GitHub Pages / Static Hosting -->
  <script>
  (function() {
    const isStaticHost = window.location.protocol === 'file:' || 
                         window.location.hostname.includes('github.io') ||
                         window.location.hostname.includes('localhost') && window.location.port !== '5077';
    
    // Initial State
    let localState = {
      is_torch_on: false,
      is_hotspot_on: false,
      hotspot_ssid: "ZeroPhone-5G",
      hotspot_pass: "zero-os-pass",
      hotspot_clients: 1,
      is_wifi_on: true,
      wifi_ssid: "Home-5G",
      is_bluetooth_on: true,
      bluetooth_device: "Sony WH-1000XM5",
      sound_mode: "sound",
      volume: 70,
      is_grayscale: false,
      is_micro_window: false,
      is_dia_mode: false,
      is_mic_killed: false,
      auto_airgap_enabled: true,
      active_app: null,
      is_ephemeral: false,
      palette: "official",
      screen_refresh_hz: 120,
      brightness: 85,
      battery_percent: 88,
      battery_days_remaining: 4.2,
      calm_digest_enabled: true,
      calm_digest_items: [
        {id: 1, app: "Instagram", title: "Social Update", desc: "alex_99 and 4 others liked your story", time: "18m ago"},
        {id: 2, app: "TikTok", title: "Recommendation", desc: "Trending sound: 'Midnight Beats' in your area", time: "45m ago"},
        {id: 3, app: "UberEats", title: "Promotion", desc: "30% off your next lunch order before 2 PM", time: "2h ago"}
      ],
      impact_stats: {
        trackers_blocked: 1448,
        battery_hours_saved: 3.8,
        mic_hours_locked: 22.4,
        airgapped_apps: 10
      },
      app_shields: {
        whatsapp: { name: "WhatsApp", package: "com.whatsapp", data_cut: false, mic_muted: false, is_frozen: false, trackers_blocked: 14 },
        instagram: { name: "Instagram", package: "com.instagram.android", data_cut: false, mic_muted: false, is_frozen: false, trackers_blocked: 42 },
        tiktok: { name: "TikTok", package: "com.zhiliaoapp.musically", data_cut: false, mic_muted: false, is_frozen: false, trackers_blocked: 89 },
        x: { name: "X", package: "com.twitter.android", data_cut: false, mic_muted: false, is_frozen: false, trackers_blocked: 21 },
        banking: { name: "PhonePe & Banking", package: "com.phonepe.app", data_cut: false, mic_muted: false, is_frozen: false, trackers_blocked: 0 }
      },
      media_player: {
        is_playing: true,
        title: "Starboy",
        artist: "The Weeknd, Daft Punk",
        progress_secs: 94,
        total_secs: 230
      },
      navigation: {
        is_active: false,
        destination: "Central Station, Platform 3",
        next_maneuver: "Turn right onto Oxford St in 150m",
        eta_minutes: 12,
        distance_km: 3.4
      },
      kernel_logs: [
        "[Init] ZeroOS AOSP Core v1.0.0 initializing...",
        "[Security] Verified Boot state: GREEN (RSA-4096 release-keys verified)",
        "[ZeroIntegrityBridge] Play Integrity: MEETS_DEVICE_INTEGRITY active",
        "[Netfilter] Zero-leak iptables hook registered",
        "[AudioHAL] Hardware microphone register lock armed (0ms squelch)",
        "[PowerHAL] DIA Mode controller ready (Standby baseline: 11.1 mA)",
        "[Telephony] VoLTE & 5G NR carrier profile registered",
        "[Ready] Welcome to ZeroOS. System is secure."
      ]
    };

    const originalFetch = window.fetch;
    window.fetch = async function(url, options = {}) {
      if (!isStaticHost || !url.startsWith('/api/')) {
        try {
          return await originalFetch(url, options);
        } catch (e) {
          if (!isStaticHost) throw e;
        }
      }

      // Intercept /api/ calls client-side
      const body = options.body ? JSON.parse(options.body) : {};
      let responseData = { success: true, state: localState };

      if (url === '/api/state') {
        responseData = localState;
      } else if (url === '/api/set_brightness') {
        localState.brightness = body.brightness || 80;
      } else if (url === '/api/set_volume') {
        localState.volume = body.volume || 70;
      } else if (url === '/api/toggle_feature') {
        const feat = body.feature;
        if (feat === 'wifi') {
          localState.is_wifi_on = !localState.is_wifi_on;
          localState.kernel_logs.push(`[Netd] wlan0 state -> ${localState.is_wifi_on ? 'CONNECTED' : 'DISCONNECTED'}`);
        } else if (feat === 'bluetooth') {
          localState.is_bluetooth_on = !localState.is_bluetooth_on;
          localState.kernel_logs.push(`[BlueDroid] Bluetooth state -> ${localState.is_bluetooth_on ? 'CONNECTED' : 'OFF'}`);
        } else if (feat === 'sound') {
          const modes = ['sound', 'vibrate', 'silent'];
          localState.sound_mode = modes[(modes.indexOf(localState.sound_mode) + 1) % modes.length];
        } else if (feat === 'torch') {
          localState.is_torch_on = !localState.is_torch_on;
        } else if (feat === 'hotspot') {
          localState.is_hotspot_on = !localState.is_hotspot_on;
        } else if (feat === 'dia' || feat === 'nokia') {
          localState.is_dia_mode = !localState.is_dia_mode;
          localState.battery_days_remaining = localState.is_dia_mode ? 5.8 : 4.2;
        } else if (feat === 'grayscale') {
          localState.is_grayscale = !localState.is_grayscale;
        } else if (feat === 'airgap') {
          localState.auto_airgap_enabled = !localState.auto_airgap_enabled;
        }
      } else if (url === '/api/launch_app') {
        localState.active_app = body.app_key;
        localState.is_ephemeral = !!body.is_ephemeral;
      } else if (url === '/api/close_app') {
        localState.active_app = null;
        localState.is_ephemeral = false;
        localState.kernel_logs.push('[Netfilter] App closed. Dropping background sockets.');
      } else if (url === '/api/toggle_media') {
        localState.media_player.is_playing = !localState.media_player.is_playing;
      } else if (url === '/api/toggle_navigation') {
        localState.navigation.is_active = !localState.navigation.is_active;
      } else if (url === '/api/clear_digest') {
        localState.calm_digest_items = [];
      } else if (url === '/api/command') {
        const cmd = (body.command || '').toLowerCase().trim();
        let reply = "Command acknowledged.";
        if (cmd.includes('setup') || cmd.includes('wizard') || cmd.includes('oobe')) {
          localState.active_app = 'setup';
          reply = "🚀 Launched ZeroOS Setup Wizard.";
        } else if (cmd.includes('dia')) {
          localState.is_dia_mode = !localState.is_dia_mode;
          localState.battery_days_remaining = localState.is_dia_mode ? 5.8 : 4.2;
          reply = `🔋 DIA Mode is now ${localState.is_dia_mode ? 'ON' : 'OFF'}.`;
        } else if (cmd.includes('wifi')) {
          localState.is_wifi_on = !localState.is_wifi_on;
          reply = `📶 Wi-Fi is now ${localState.is_wifi_on ? 'ON' : 'OFF'}.`;
        } else if (cmd.includes('hotspot')) {
          localState.is_hotspot_on = !localState.is_hotspot_on;
          reply = `(((•))) Hotspot is now ${localState.is_hotspot_on ? 'ON' : 'OFF'}.`;
        } else if (cmd.includes('torch') || cmd.includes('flashlight')) {
          localState.is_torch_on = !localState.is_torch_on;
          reply = `🔦 Flashlight turned ${localState.is_torch_on ? 'ON' : 'OFF'}.`;
        } else if (cmd.includes('unmute')) {
          for (let k in localState.app_shields) localState.app_shields[k].mic_muted = false;
          reply = "🎙️ Microphone unmuted for applications.";
        } else if (cmd.includes('mute')) {
          for (let k in localState.app_shields) localState.app_shields[k].mic_muted = true;
          reply = "🔇 Microphone muted across requested apps.";
        } else {
          reply = `✓ ZeroOS executed: "${body.command}"`;
        }
        responseData = { success: true, message: reply, state: localState };
      }

      return new Response(JSON.stringify(responseData), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    };
  })();
  </script>
"""

    # Inject mock right before </head>
    injected_html = raw_html.replace('</head>', client_mock + '\n</head>')

    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(injected_html)

    print(f"Successfully exported static ZeroOS showcase to {out_html} ({len(injected_html)} bytes)")

if __name__ == '__main__':
    main()
