import os
import sys
import json
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Simulated ZeroOS System & Kernel State
STATE = {
    "is_torch_on": False,
    "is_hotspot_on": False,
    "hotspot_ssid": "ZeroPhone-5G",
    "hotspot_pass": "zero-os-pass",
    "hotspot_clients": 1,
    "is_grayscale": False,
    "is_micro_window": False,
    "is_nokia_mode": False,
    "palette": "official",  # official, monochrome, amber, emerald, cyan
    "screen_refresh_hz": 120,
    "battery_percent": 88,
    "battery_days_remaining": 4.2,
    "app_shields": {
        "whatsapp": {
            "name": "WhatsApp",
            "package": "com.whatsapp",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 14
        },
        "instagram": {
            "name": "Instagram",
            "package": "com.instagram.android",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 42
        },
        "tiktok": {
            "name": "TikTok",
            "package": "com.zhiliaoapp.musically",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 68
        },
        "youtube": {
            "name": "YouTube",
            "package": "com.google.android.youtube",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 31
        },
        "monzo": {
            "name": "Monzo",
            "package": "co.uk.getmondo",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 0
        }
    },
    "kernel_logs": [
        "[0.000000] Linux version 5.10.198-android12-9-g8971 (android-build@google)",
        "[0.042100] Android Runtime (ART) initialized. Dalvik VM ready",
        "[0.120500] Netfilter iptables ready. Stealth FCM Push Bridge: ACTIVE",
        "[1.020000] SystemUI / Launcher booted. Material 3 Shell online (120Hz)"
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ZeroOS - Pure Android OS with Official Brand Icons</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --android-bg: #0c0f14;
      --android-surface: #1a1e26;
      --android-card: #202632;
      --android-primary: #a8c7fa;
      --android-accent: #669df6;
      --android-text: #e2e8f0;
      --android-text-muted: #94a3b8;
      --android-amber: #f59e0b;
      --android-green: #34d399;
      --android-red: #f87171;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #06090e;
      color: var(--android-text);
      font-family: 'Roboto', -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px;
    }

    .top-header {
      text-align: center;
      margin-bottom: 20px;
    }
    .top-header h1 {
      font-size: 1.6rem;
      font-weight: 500;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }
    .top-header p {
      font-size: 0.85rem;
      color: var(--android-text-muted);
      margin-top: 4px;
    }

    .main-layout {
      display: flex;
      gap: 36px;
      align-items: flex-start;
      justify-content: center;
      max-width: 1200px;
      width: 100%;
      flex-wrap: wrap;
    }

    /* REALISTIC ANDROID PHONE HARDWARE */
    .phone-container {
      position: relative;
    }
    .phone-body {
      width: 380px;
      height: 780px;
      background: #000;
      border: 8px solid #232731;
      border-radius: 46px;
      box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 30px rgba(102, 157, 246, 0.1);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      user-select: none;
    }

    /* PHYSICAL BUTTONS */
    .hw-button-power {
      position: absolute;
      right: -14px;
      top: 180px;
      width: 6px;
      height: 60px;
      background: #475569;
      border-radius: 0 4px 4px 0;
      cursor: pointer;
      transition: background 0.15s;
    }
    .hw-button-power:hover { background: var(--android-primary); }
    .hw-button-vol-up {
      position: absolute;
      left: -14px;
      top: 150px;
      width: 6px;
      height: 50px;
      background: #475569;
      border-radius: 4px 0 0 4px;
    }
    .hw-button-vol-down {
      position: absolute;
      left: -14px;
      top: 210px;
      width: 6px;
      height: 50px;
      background: #475569;
      border-radius: 4px 0 0 4px;
    }
    .power-hint {
      position: absolute;
      right: -100px;
      top: 195px;
      font-size: 0.72rem;
      color: var(--android-primary);
      font-family: 'JetBrains Mono', monospace;
      white-space: nowrap;
    }

    /* CAMERA PUNCH HOLE */
    .punch-camera {
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      width: 12px;
      height: 12px;
      background: #000;
      border: 1.5px solid #1a1e26;
      border-radius: 50%;
      z-index: 100;
    }

    /* FLASHLIGHT TORCH INDICATOR ON TOP */
    .torch-beam {
      position: absolute;
      top: -30px;
      left: 50%;
      transform: translateX(-50%);
      background: #fbbf24;
      color: #000;
      font-size: 0.68rem;
      font-weight: 700;
      padding: 3px 12px;
      border-radius: 20px;
      opacity: 0;
      transition: opacity 0.3s ease;
      box-shadow: 0 0 20px #fbbf24;
    }
    .torch-active .torch-beam { opacity: 1; }

    /* PHONE SCREEN */
    .screen {
      flex: 1;
      background: #000000;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      transition: filter 0.3s ease;
      --theme-clock: #ffffff;
      --theme-border: #283244;
    }

    /* PALETTE COLOR MODES */
    .screen.palette-monochrome {
      --theme-clock: #ffffff;
      --theme-border: #334155;
    }
    .screen.palette-monochrome .app-icon-shape svg {
      filter: grayscale(100%) brightness(1.2);
    }

    .screen.palette-amber {
      --theme-clock: #fbbf24;
      --theme-border: #78350f;
    }
    .screen.palette-amber .app-icon-shape svg {
      filter: sepia(100%) saturate(300%) hue-rotate(5deg) brightness(1.05);
    }

    .screen.palette-emerald {
      --theme-clock: #34d399;
      --theme-border: #064e3b;
    }
    .screen.palette-emerald .app-icon-shape svg {
      filter: sepia(100%) saturate(400%) hue-rotate(95deg) brightness(1.05);
    }

    .screen.palette-cyan {
      --theme-clock: #38bdf8;
      --theme-border: #075985;
    }
    .screen.palette-cyan .app-icon-shape svg {
      filter: sepia(100%) saturate(400%) hue-rotate(155deg) brightness(1.15);
    }

    .screen.grayscale-mode {
      filter: grayscale(100%) contrast(1.05);
    }

    /* 1. ANDROID STATUS BAR */
    .android-status-bar {
      height: 38px;
      padding: 8px 18px 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.76rem;
      font-weight: 500;
      color: #fff;
      z-index: 10;
    }
    .status-left {
      font-weight: 600;
      letter-spacing: -0.2px;
    }
    .status-right {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .status-hotspot-icon {
      color: var(--android-green);
      font-size: 0.75rem;
      display: none;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
    .status-hotspot-icon.visible { display: inline-block; }

    /* 2. ANDROID NOTIFICATION CARDS */
    .notification-shelf {
      padding: 0 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 4px;
      z-index: 20;
    }
    .android-notif {
      background: #141923;
      border-radius: 14px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border: 1px solid #222b3b;
      animation: slideDown 0.25s ease;
    }
    @keyframes slideDown { from { transform: translateY(-10px); opacity:0; } to { transform: translateY(0); opacity:1; } }
    .notif-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .notif-icon { font-size: 1.1rem; }
    .notif-title { font-size: 0.78rem; font-weight: 600; color: #fff; }
    .notif-desc { font-size: 0.68rem; color: var(--android-text-muted); }
    .notif-btn {
      background: rgba(255,255,255,0.1);
      color: #fff;
      border: none;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 0.7rem;
      cursor: pointer;
    }
    .notif-btn:hover { background: rgba(255,255,255,0.2); }

    /* 3. ANDROID HOME SCREEN WIDGETS */
    .home-content {
      flex: 1;
      padding: 14px 16px 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }

    /* Reachability / Micro-window mode */
    .screen.micro-active .reachability-dark-zone {
      display: flex;
    }
    .screen.micro-active .home-content {
      max-height: 380px;
    }
    .reachability-dark-zone {
      display: none;
      height: 360px;
      background: #000;
      color: #475569;
      font-size: 0.75rem;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 20px;
      border-bottom: 1px dashed #222;
      cursor: pointer;
    }

    .at-a-glance {
      margin-bottom: 8px;
    }
    .glance-date {
      font-size: 0.85rem;
      font-weight: 500;
      color: #94a3b8;
    }
    .glance-weather {
      font-size: 0.8rem;
      color: #cbd5e1;
      margin-top: 2px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .digital-clock-widget {
      margin: 8px 0 16px;
    }
    .clock-digits {
      font-size: 3.4rem;
      font-weight: 300;
      letter-spacing: -2px;
      line-height: 1;
      color: var(--theme-clock);
      transition: color 0.3s;
    }
    .battery-pill-glance {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 6px;
      background: #11141b;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 0.68rem;
      color: var(--android-green);
    }

    /* 4. ANDROID SEARCH / SETTINGS COMMAND BAR */
    .search-command-bar {
      background: #10141d;
      border: 1px solid var(--theme-border);
      border-radius: 26px;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.4);
      margin-bottom: 16px;
      transition: all 0.2s ease;
    }
    .search-command-bar:focus-within {
      border-color: var(--android-primary);
      background: #171d29;
      box-shadow: 0 0 0 2px rgba(168, 199, 250, 0.25);
    }
    .search-icon { color: var(--android-text-muted); font-size: 0.95rem; }
    .search-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 0.85rem;
      font-family: inherit;
    }
    .search-input::placeholder { color: #64748b; font-size: 0.8rem; }
    .search-mic {
      color: var(--android-primary);
      font-size: 0.95rem;
      cursor: pointer;
    }

    /* QUICK COMMAND CHIPS */
    .quick-chips-row {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 6px;
      margin-bottom: 14px;
    }
    .quick-chips-row::-webkit-scrollbar { display: none; }
    .android-chip {
      background: #11151c;
      border: 1px solid #1f2736;
      border-radius: 18px;
      padding: 5px 12px;
      font-size: 0.72rem;
      color: #cbd5e1;
      white-space: nowrap;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s ease;
    }
    .android-chip:hover {
      background: #1c2331;
      color: #fff;
      border-color: var(--android-primary);
    }

    /* 5. ANDROID APPS GRID (Pure OLED Zero-Watt Unboxed Official Icons) */
    .apps-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px 8px;
      padding: 4px 0 12px;
    }
    .app-icon-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: transform 0.12s ease;
      position: relative;
    }
    .app-icon-item:active { transform: scale(0.92); }
    .app-icon-shape {
      width: 48px;
      height: 48px;
      background: transparent;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      transition: transform 0.15s ease;
    }
    .app-icon-shape svg {
      width: 44px;
      height: 44px;
      transition: filter 0.25s ease, transform 0.15s ease;
    }
    .app-icon-item:hover .app-icon-shape {
      transform: scale(1.08);
    }
    .shield-badge-dot {
      position: absolute;
      top: -3px;
      right: -3px;
      background: var(--android-amber);
      color: #000;
      font-size: 0.55rem;
      font-weight: 800;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1.5px solid #000;
      z-index: 10;
    }
    .shield-badge-dot.cut {
      background: var(--android-red);
      color: #fff;
    }
    .app-label {
      font-size: 0.7rem;
      color: #94a3b8;
      text-align: center;
      max-width: 60px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* 6. BOTTOM ANDROID DOCK (Zero OLED Power Container) */
    .android-dock {
      background: transparent;
      border-radius: 0;
      padding: 6px 16px;
      display: flex;
      justify-content: space-around;
      align-items: center;
      margin-top: auto;
      border: none;
    }

    /* 7. ANDROID GESTURE BAR */
    .gesture-bar {
      width: 90px;
      height: 4px;
      background: #94a3b8;
      border-radius: 4px;
      margin: 10px auto 4px;
      opacity: 0.6;
    }

    /* MATERIAL 3 CONFIRMATION BOTTOM SHEET */
    .material-sheet-overlay {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: #161b24;
      border-radius: 28px 28px 0 0;
      padding: 22px 20px 24px;
      box-shadow: 0 -10px 40px rgba(0,0,0,0.8);
      border-top: 1px solid #283344;
      transform: translateY(100%);
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 90;
    }
    .material-sheet-overlay.active {
      transform: translateY(0);
    }
    .sheet-handle {
      width: 36px;
      height: 4px;
      background: #64748b;
      border-radius: 4px;
      margin: 0 auto 14px;
    }
    .sheet-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #fff;
      margin-bottom: 8px;
    }
    .sheet-desc {
      font-size: 0.8rem;
      color: #cbd5e1;
      line-height: 1.5;
      margin-bottom: 16px;
    }
    .sheet-bullets {
      font-size: 0.75rem;
      color: var(--android-text-muted);
      margin-bottom: 18px;
      padding-left: 16px;
      line-height: 1.6;
    }
    .sheet-actions {
      display: flex;
      gap: 10px;
    }
    .btn-android-primary {
      flex: 1;
      background: var(--android-primary);
      color: #0c121e;
      font-weight: 600;
      border: none;
      padding: 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      cursor: pointer;
    }
    .btn-android-secondary {
      flex: 1;
      background: #232b3a;
      color: #cbd5e1;
      border: none;
      padding: 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      cursor: pointer;
    }

    /* APP SETTINGS QUICK MODAL */
    .app-settings-modal {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: #141822;
      border-radius: 26px 26px 0 0;
      padding: 20px;
      border-top: 1px solid #232c3d;
      transform: translateY(100%);
      transition: transform 0.25s ease;
      z-index: 85;
    }
    .app-settings-modal.active { transform: translateY(0); }
    .modal-app-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }
    .modal-app-icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; }
    .modal-app-title { font-size: 1rem; font-weight: 600; color: #fff; }
    .modal-app-pkg { font-size: 0.68rem; color: #64748b; font-family: monospace; }
    .toggles-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 16px;
    }
    .toggle-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #1b212c;
      padding: 10px 14px;
      border-radius: 12px;
    }
    .toggle-info { font-size: 0.78rem; color: #e2e8f0; }
    .toggle-sub { font-size: 0.65rem; color: #94a3b8; }
    .switch-btn {
      padding: 5px 12px;
      border-radius: 14px;
      font-size: 0.7rem;
      border: none;
      cursor: pointer;
      font-weight: 600;
    }
    .switch-btn.active { background: var(--android-red); color: #fff; }
    .switch-btn.inactive { background: #334155; color: #94a3b8; }

    /* SYSTEM TOAST */
    .android-toast {
      position: absolute;
      bottom: 68px;
      left: 50%;
      transform: translateX(-50%);
      background: #252e3e;
      color: #fff;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 0.75rem;
      display: none;
      white-space: nowrap;
      z-index: 100;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    /* RIGHT TELEMETRY & KERNEL LOG PANEL */
    .telemetry-side {
      flex: 1;
      min-width: 380px;
      max-width: 560px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .side-box {
      background: #111620;
      border: 1px solid #1e2636;
      border-radius: 16px;
      padding: 18px;
    }
    .side-box-title {
      font-size: 0.95rem;
      font-weight: 600;
      color: #fff;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .grid-stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .stat-tile {
      background: #171e2c;
      padding: 12px;
      border-radius: 10px;
    }
    .stat-label { font-size: 0.7rem; color: #94a3b8; }
    .stat-val { font-size: 1.1rem; font-weight: 700; color: #fff; margin-top: 4px; }
    .kernel-terminal {
      background: #080b10;
      border: 1px solid #192130;
      border-radius: 10px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      color: #38bdf8;
      height: 200px;
      overflow-y: auto;
      line-height: 1.6;
    }
  </style>
</head>
<body>

  <div class="top-header">
    <h1>📱 ZeroOS - Pure Android OS with Official Brand Icons</h1>
    <p>Authentic official app icons without battery-draining boxes · Extreme battery & kernel privacy</p>
  </div>

  <div class="main-layout">

    <!-- REALISTIC SMARTPHONE BODY -->
    <div class="phone-container" id="phoneContainer">
      <div class="torch-beam" id="torchBeam">🔦 FLASHLIGHT ON</div>
      <div class="hw-button-power" onclick="triggerPowerButton()" title="Hold Power Button: Opens Universal Search Bar"></div>
      <div class="power-hint">👈 Hold Power</div>
      <div class="hw-button-vol-up"></div>
      <div class="hw-button-vol-down"></div>

      <div class="phone-body">
        <div class="punch-camera"></div>

        <div class="screen" id="phoneScreen">
          
          <!-- 1. ANDROID STATUS BAR -->
          <div class="android-status-bar">
            <span class="status-left" id="statusClock">11:28</span>
            <div class="status-right">
              <span class="status-hotspot-icon" id="statusHotspotIcon" title="Wi-Fi Hotspot Active">(((•)))</span>
              <span>📶 5G</span>
              <span id="statusBattery">🔋 88%</span>
            </div>
          </div>

          <!-- REACHABILITY (MICRO-WINDOW 0.00W ZONE) -->
          <div class="reachability-dark-zone" onclick="toggleMicroDisplay(false)">
            <div>
              <div style="font-size:1.1rem; font-weight:600; color:#fff; margin-bottom:4px;">⚡ 0.00W OLED Reachability</div>
              <div>80% of screen panel physically powered down. Tap to expand.</div>
            </div>
          </div>

          <!-- 2. ANDROID NOTIFICATION SHELF -->
          <div class="notification-shelf">
            
            <!-- Hotspot Notification -->
            <div class="android-notif" id="notifHotspot" style="display:none;">
              <div class="notif-left">
                <span class="notif-icon">(((•)))</span>
                <div>
                  <div class="notif-title">Wi-Fi Hotspot Active</div>
                  <div class="notif-desc"><span id="notifSsid">ZeroPhone-5G</span> · 1 device connected</div>
                </div>
              </div>
              <button class="notif-btn" onclick="sendCommand('turn off hotspot')">Turn Off</button>
            </div>

            <!-- Flashlight Notification -->
            <div class="android-notif" id="notifTorch" style="display:none;">
              <div class="notif-left">
                <span class="notif-icon">🔦</span>
                <div>
                  <div class="notif-title">Flashlight On</div>
                  <div class="notif-desc">Camera LED active</div>
                </div>
              </div>
              <button class="notif-btn" onclick="sendCommand('turn off flash')">Turn Off</button>
            </div>

          </div>

          <!-- 3. ANDROID HOME SCREEN CONTENT -->
          <div class="home-content">
            
            <!-- Top Widget: Date & Weather -->
            <div class="at-a-glance">
              <div class="glance-date">Thursday, Oct 29</div>
              <div class="glance-weather">⛅ 21°C · Clear Sky · Silent Shield</div>
            </div>

            <!-- Digital Clock Widget -->
            <div class="digital-clock-widget">
              <div class="clock-digits" id="widgetClock">11:28</div>
              <div class="battery-pill-glance" id="widgetBatteryPill">
                <span>🔋 4.2 Days Battery Remaining</span>
              </div>
            </div>

            <!-- 4. UNIVERSAL ANDROID SETTINGS & SEARCH BAR -->
            <div class="search-command-bar">
              <span class="search-icon">🔍</span>
              <input type="text" id="androidSearchInput" class="search-input" placeholder="Search apps or type command (e.g. hotspot, grayscale)..." onkeydown="if(event.key==='Enter') executeSearchCommand()" />
              <span class="search-mic" onclick="executeSearchCommand()" title="Execute">↵</span>
            </div>

            <!-- Quick Suggestions Chips -->
            <div class="quick-chips-row">
              <div class="android-chip" onclick="quickRun('turn on hotspot')">(((•))) Hotspot</div>
              <div class="android-chip" onclick="quickRun('turn on flash')">🔦 Flashlight</div>
              <div class="android-chip" onclick="quickRun('turn on grayscale')">🌓 Grayscale</div>
              <div class="android-chip" onclick="quickRun('micro window')">📱 Micro Display</div>
              <div class="android-chip" onclick="quickRun('nokia mode')">🔋 Nokia Mode</div>
              <div class="android-chip" onclick="quickRun('about phone')">ℹ️ About Phone</div>
            </div>

            <!-- 5. STANDARD ANDROID APP ICONS GRID (Official Brand SVGs) -->
            <div class="apps-grid">
              
              <div class="app-icon-item" onclick="launchApp('phone')">
                <div class="app-icon-shape" id="icon-phone"></div>
                <div class="app-label">Phone</div>
              </div>

              <div class="app-icon-item" onclick="launchApp('messages')">
                <div class="app-icon-shape" id="icon-messages"></div>
                <div class="app-label">Messages</div>
              </div>

              <div class="app-icon-item" onclick="launchApp('chrome')">
                <div class="app-icon-shape" id="icon-chrome"></div>
                <div class="app-label">Chrome</div>
              </div>

              <div class="app-icon-item" onclick="launchApp('camera')">
                <div class="app-icon-shape" id="icon-camera"></div>
                <div class="app-label">Camera</div>
              </div>

              <!-- Protected Apps -->
              <div class="app-icon-item" onclick="openAppShieldModal('whatsapp')">
                <div class="app-icon-shape" id="icon-whatsapp">
                  <span class="shield-badge-dot" id="dot-whatsapp" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">WhatsApp</div>
              </div>

              <div class="app-icon-item" onclick="openAppShieldModal('instagram')">
                <div class="app-icon-shape" id="icon-instagram">
                  <span class="shield-badge-dot" id="dot-instagram" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">Instagram</div>
              </div>

              <div class="app-icon-item" onclick="openAppShieldModal('tiktok')">
                <div class="app-icon-shape" id="icon-tiktok">
                  <span class="shield-badge-dot" id="dot-tiktok" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">TikTok</div>
              </div>

              <div class="app-icon-item" onclick="openAppShieldModal('youtube')">
                <div class="app-icon-shape" id="icon-youtube">
                  <span class="shield-badge-dot" id="dot-youtube" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">YouTube</div>
              </div>

              <div class="app-icon-item" onclick="openAppShieldModal('monzo')">
                <div class="app-icon-shape" id="icon-monzo">
                  <span class="shield-badge-dot" id="dot-monzo" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">Monzo</div>
              </div>

              <div class="app-icon-item" onclick="launchApp('spotify')">
                <div class="app-icon-shape" id="icon-spotify"></div>
                <div class="app-label">Spotify</div>
              </div>

              <div class="app-icon-item" onclick="launchApp('maps')">
                <div class="app-icon-shape" id="icon-maps"></div>
                <div class="app-label">Maps</div>
              </div>

              <div class="app-icon-item" onclick="quickRun('about phone')">
                <div class="app-icon-shape" id="icon-settings"></div>
                <div class="app-label">Settings</div>
              </div>

            </div>

            <!-- 6. STANDARD ANDROID DOCK (Pure Transparent OLED Black) -->
            <div class="android-dock">
              <div class="app-icon-item" onclick="launchApp('phone')">
                <div class="app-icon-shape" id="dock-phone"></div>
              </div>
              <div class="app-icon-item" onclick="launchApp('messages')">
                <div class="app-icon-shape" id="dock-messages"></div>
              </div>
              <div class="app-icon-item" onclick="launchApp('chrome')">
                <div class="app-icon-shape" id="dock-chrome"></div>
              </div>
              <div class="app-icon-item" onclick="launchApp('camera')">
                <div class="app-icon-shape" id="dock-camera"></div>
              </div>
            </div>

            <!-- 7. GESTURE NAVIGATION PILL -->
            <div class="gesture-bar"></div>

          </div>

          <!-- MATERIAL 3 CONFIRMATION BOTTOM SHEET -->
          <div class="material-sheet-overlay" id="materialSheet">
            <div class="sheet-handle"></div>
            <div class="sheet-title" id="sheetTitle">Turn on Grayscale?</div>
            <div class="sheet-desc" id="sheetDesc">
              Converts screen pixels to monochrome black & white.
            </div>
            <ul class="sheet-bullets" id="sheetBullets">
              <li>Eliminates visual dopamine addiction.</li>
              <li>Saves up to 18% OLED battery power.</li>
            </ul>
            <div class="sheet-actions">
              <button class="btn-android-secondary" onclick="dismissSheet()">Cancel</button>
              <button class="btn-android-primary" onclick="confirmSheetAction()">Turn On</button>
            </div>
          </div>

          <!-- APP PRIVACY QUICK MODAL -->
          <div class="app-settings-modal" id="appModal">
            <div class="sheet-handle"></div>
            <div class="modal-app-header">
              <div class="modal-app-icon" id="modalIcon"></div>
              <div>
                <div class="modal-app-title" id="modalTitle">Instagram</div>
                <div class="modal-app-pkg" id="modalPkg">com.instagram.android</div>
              </div>
            </div>
            <div class="toggles-list">
              <div class="toggle-row">
                <div>
                  <div class="toggle-info">Background Cellular & Wi-Fi</div>
                  <div class="toggle-sub">Kernel packet dropping (0 B/s)</div>
                </div>
                <button class="switch-btn inactive" id="btnToggleData" onclick="toggleShield('data')">Allow</button>
              </div>
              <div class="toggle-row">
                <div>
                  <div class="toggle-info">Microphone Sensor</div>
                  <div class="toggle-sub">Hardware register lock</div>
                </div>
                <button class="switch-btn inactive" id="btnToggleMic" onclick="toggleShield('mic')">Allow</button>
              </div>
              <div class="toggle-row">
                <div>
                  <div class="toggle-info">App Hibernation</div>
                  <div class="toggle-sub">Freeze background CPU usage</div>
                </div>
                <button class="switch-btn inactive" id="btnToggleFreeze" onclick="toggleShield('freeze')">Awake</button>
              </div>
            </div>
            <div class="sheet-actions">
              <button class="btn-android-secondary" style="flex:1;" onclick="closeAppModal()">Done</button>
              <button class="btn-android-primary" style="flex:1;" onclick="launchCurrentModalApp()">Open App</button>
            </div>
          </div>

          <!-- TOAST -->
          <div class="android-toast" id="androidToast">Action performed</div>

        </div>
      </div>
    </div>

    <!-- RIGHT TELEMETRY & KERNEL LOG MONITOR -->
    <div class="telemetry-side">
      
      <!-- 🎨 COLOR PALETTE SELECTOR -->
      <div class="side-box">
        <div class="side-box-title">🎨 Official Color Options & Palettes</div>
        <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">Select how official icons and highlights render (Screen remains 100% OLED #000000):</div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">
          <button class="android-chip" onclick="setPalette('official')">🌈 Official Brand Colors</button>
          <button class="android-chip" onclick="setPalette('monochrome')">⚪ Zen White (Mono)</button>
          <button class="android-chip" onclick="setPalette('amber')">🟡 Warm Amber (Night)</button>
          <button class="android-chip" onclick="setPalette('emerald')">🟢 Phosphor Green (Max Battery)</button>
          <button class="android-chip" onclick="setPalette('cyan')">🔵 Nordic Glacier Cyan</button>
        </div>
      </div>

      <div class="side-box">
        <div class="side-box-title">⚡ System Status & Telemetry</div>
        <div class="grid-stats">
          <div class="stat-tile">
            <div class="stat-label">Battery Estimation</div>
            <div class="stat-val" id="statBattery">4.2 Days</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Display Hardware</div>
            <div class="stat-val" id="statDisplay">120Hz Full OLED</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Active Hotspot</div>
            <div class="stat-val" id="statHotspot">OFF</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Push Bridge (FCM)</div>
            <div class="stat-val" style="color:var(--android-green);">Connected</div>
          </div>
        </div>
      </div>

      <div class="side-box">
        <div class="side-box-title">🖥️ Linux Kernel & Network Subsystem Log</div>
        <div class="kernel-terminal" id="kernelLogs">
          <!-- Logs go here -->
        </div>
      </div>

      <div class="side-box">
        <div class="side-box-title">💡 How to Test the Simple UI</div>
        <div style="font-size:0.78rem; line-height:1.6; color:#cbd5e1;">
          <p>• <b>Official Icons:</b> Notice real WhatsApp, YouTube, Instagram, TikTok, Chrome, Spotify, Maps, and Monzo logos floating borderless on OLED black.</p>
          <p style="margin-top:6px;">• <b>Color Options:</b> Click any of the 5 palettes above (e.g. <i>Warm Amber</i> for night mode or <i>Official Brand Colors</i>).</p>
          <p style="margin-top:6px;">• <b>Search Commands:</b> Type <code>hotspot</code>, <code>grayscale</code>, <code>nokia mode</code>, or <code>theme amber</code> into the search bar.</p>
        </div>
      </div>
    </div>

  </div>

  <script>
    // OFFICIAL BRAND SVG ASSETS
    const OFFICIAL_ICONS = {
      phone: `<svg viewBox="0 0 48 48"><path fill="#34A853" d="M11.2 5.5l5.2-1c1.2-.2 2.4.5 2.8 1.6l2.4 5.6c.4 1 .1 2.2-.7 2.9l-3.2 3.2c2.4 4.8 6.4 8.7 11.2 11.2l3.2-3.2c.7-.7 1.9-1 2.9-.7l5.6 2.4c1.1.5 1.8 1.6 1.6 2.8l-1 5.2c-.3 1.3-1.4 2.3-2.7 2.3C21 38 10 27 10 7.7c0-1.3 1-2.4 2.3-2.7l-1.1.5z"/></svg>`,
      messages: `<svg viewBox="0 0 48 48"><path fill="#1A73E8" d="M40 8H8c-2.2 0-4 1.8-4 4v28l8-8h28c2.2 0 4-1.8 4-4V12c0-2.2-1.8-4-4-4z"/><circle cx="16" cy="22" r="2.5" fill="#FFF"/><circle cx="24" cy="22" r="2.5" fill="#FFF"/><circle cx="32" cy="22" r="2.5" fill="#FFF"/></svg>`,
      chrome: `<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="19" fill="none"/><path fill="#EA4335" d="M24 4c8.4 0 15.6 5.2 18.5 12.6H24v7.4h-7.7L9.5 12.2C13.2 7.2 18.2 4 24 4z"/><path fill="#FBBC05" d="M9.5 12.2l6.8 11.8H8.5c-2.8 0-4.5-2.2-4.5-5 0-2.4 1-4.7 2.6-6.6l2.9-2.2z"/><path fill="#34A853" d="M16.3 24l-6.8 11.8C6.3 32.5 4 28.5 4 24c0-2.8 1.1-5.3 2.9-7.2l9.4 7.2z"/><path fill="#FBBC04" d="M24 44c-7.3 0-13.8-4-17.2-10l6.8-11.8 7.6 13.2L24 44z"/><path fill="#34A853" d="M42.5 16.6C43.5 18.9 44 21.4 44 24c0 11-9 20-20 20l7.2-12.4 8.7-2.6 2.6-12.4z"/><circle cx="24" cy="24" r="9" fill="#FFF"/><circle cx="24" cy="24" r="7.2" fill="#1A73E8"/></svg>`,
      camera: `<svg viewBox="0 0 48 48"><path fill="#5F6368" d="M18 8l-3.6 4H8c-2.2 0-4 1.8-4 4v20c0 2.2 1.8 4 4 4h32c2.2 0 4-1.8 4-4V16c0-2.2-1.8-4-4-4h-6.4L30 8H18z"/><circle cx="24" cy="26" r="8" fill="#4285F4"/><circle cx="24" cy="26" r="4.5" fill="#FFF"/><circle cx="35" cy="18" r="2" fill="#34A853"/></svg>`,
      whatsapp: `<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="20" fill="#25D366"/><path fill="#FFF" d="M34.8 29.8c-.4 1.2-2.1 2.3-3 2.4-.8.1-1.8.2-5.9-1.5-5.2-2.2-8.5-7.4-8.8-7.8-.3-.4-2.1-2.8-2.1-5.3s1.3-3.7 1.8-4.2c.4-.4 1-.7 1.6-.7.2 0 .4 0 .6.1.5 0 .9.1 1.2.9.4 1.1 1.5 3.8 1.6 4.1.2.3.3.7.1 1-.2.3-.3.6-.5.8-.3.3-.4.5-.7.7-.3.3-.5.5-.3 1 .4.6 1.5 2.4 3.1 3.9 2.2 1.9 4 2.5 4.6 2.8.6.3 1 .3 1.3-.2.3-.4 1.6-1.8 2-2.4.4-.6.9-.5 1.5-.3.6.3 3.8 1.8 4.5 2.2.7.3 1.1.5 1.3.8.2.3.2 1.8-.2 3z"/></svg>`,
      instagram: `<svg viewBox="0 0 48 48"><defs><radialGradient id="ig-grad" cx="20%" cy="105%" r="120%"><stop offset="0%" stop-color="#ffd600"/><stop offset="35%" stop-color="#ff0140"/><stop offset="70%" stop-color="#d800b9"/><stop offset="100%" stop-color="#7000ff"/></radialGradient></defs><rect x="6" y="6" width="36" height="36" rx="10" fill="none" stroke="url(#ig-grad)" stroke-width="3.5"/><circle cx="24" cy="24" r="8.5" fill="none" stroke="url(#ig-grad)" stroke-width="3.5"/><circle cx="34" cy="14" r="2.2" fill="url(#ig-grad)"/></svg>`,
      tiktok: `<svg viewBox="0 0 48 48"><path fill="#25F4EE" d="M30 10.5c2 .7 4.2 2.2 4.8 4.2 1.5 0 2.9-.5 4.2-1.2v6.5c-2.3 0-4.5-.6-6.4-1.8v13c0 6.6-5.4 12-12 12s-12-5.4-12-12 5.4-12 12-12c.7 0 1.3.1 2 .2V26c-.6-.2-1.3-.3-2-.3-3.3 0-6 2.7-6 6s2.7 6 6 6 6-2.7 6-6V6h5.4c0 1.6.8 3.2 2 4.5z"/><path fill="#FE2C55" d="M32 8.5c2 .7 4.2 2.2 4.8 4.2 1.5 0 2.9-.5 4.2-1.2v6.5c-2.3 0-4.5-.6-6.4-1.8v13c0 6.6-5.4 12-12 12s-12-5.4-12-12 5.4-12 12-12c.7 0 1.3.1 2 .2V24c-.6-.2-1.3-.3-2-.3-3.3 0-6 2.7-6 6s2.7 6 6 6 6-2.7 6-6V4h5.4c0 1.6.8 3.2 2 4.5z"/><path fill="#FFF" d="M31 9.5c2 .7 4.2 2.2 4.8 4.2 1.5 0 2.9-.5 4.2-1.2v6.5c-2.3 0-4.5-.6-6.4-1.8v13c0 6.6-5.4 12-12 12s-12-5.4-12-12 5.4-12 12-12c.7 0 1.3.1 2 .2V25c-.6-.2-1.3-.3-2-.3-3.3 0-6 2.7-6 6s2.7 6 6 6 6-2.7 6-6V5h5.4c0 1.6.8 3.2 2 4.5z"/></svg>`,
      youtube: `<svg viewBox="0 0 48 48"><path fill="#FF0000" d="M43.2 14.8c-.5-1.9-2-3.4-3.9-3.9C35.8 10 24 10 24 10s-11.8 0-15.3.9c-1.9.5-3.4 2-3.9 3.9C4 18.3 4 24 4 24s0 5.7.8 9.2c.5 1.9 2 3.4 3.9 3.9 3.5.9 15.3.9 15.3.9s11.8 0 15.3-.9c1.9-.5 3.4-2 3.9-3.9.8-3.5.8-9.2.8-9.2s0-5.7-.8-9.2z"/><path fill="#FFF" d="M20 30l10.4-6L20 18v12z"/></svg>`,
      spotify: `<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="20" fill="#1ED760"/><path fill="#000" d="M33.2 28.5c-.4.6-1.2.8-1.8.4-5-3-11.2-3.7-18.6-2-1 .2-1.5-.5-1.7-1.1-.2-.6.4-1.3 1-1.5 8.1-1.9 15-1 20.6 2.4.6.4.8 1.2.5 1.8zm2.4-5.3c-.5.8-1.5 1-2.3.5-5.7-3.5-14.4-4.5-21.1-2.5-.9.3-1.8-.2-2.1-1.1-.3-.9.2-1.8 1.1-2.1 7.7-2.3 17.3-1.2 23.9 2.8.8.5 1 1.6.5 2.4zm.2-5.5C29 13.7 18 13.3 11.6 15.2c-1.1.3-2.3-.3-2.6-1.5-.3-1.1.3-2.3 1.5-2.6 7.4-2.2 19.5-1.8 26.6 2.4 1 .6 1.3 2 .7 3-.6.9-2 1.2-3 .6z"/></svg>`,
      monzo: `<svg viewBox="0 0 48 48"><path fill="#FF3366" d="M6 14h7v20H6z"/><path fill="#FF9900" d="M15 14h7v20h-7z"/><path fill="#00D2D3" d="M26 14h7v20h-7z"/><path fill="#1B9CFC" d="M35 14h7v20h-7z"/><path fill="#FF3366" d="M13 14l11 12 11-12h7v4l-18 18-18-18v-4h7z"/></svg>`,
      maps: `<svg viewBox="0 0 48 48"><path fill="#4285F4" d="M37.5 17.5c0 8.2-13.5 24.5-13.5 24.5S10.5 25.7 10.5 17.5C10.5 10 16.5 4 24 4s13.5 6 13.5 13.5z"/><circle cx="24" cy="17.5" r="5.5" fill="#EA4335"/><circle cx="24" cy="17.5" r="2.8" fill="#FFF"/></svg>`,
      settings: `<svg viewBox="0 0 48 48"><path fill="#9AA0A6" d="M38.8 22.1l-3.5-.6c-.3-1.1-.7-2.1-1.3-3l2.2-2.8c.8-1 .7-2.5-.3-3.4l-2.8-2.8c-1-.9-2.4-1-3.4-.3l-2.8 2.2c-.9-.6-1.9-1-3-1.3l-.6-3.5c-.2-1.3-1.3-2.4-2.7-2.4h-4c-1.3 0-2.5 1.1-2.7 2.4l-.6 3.5c-1.1.3-2.1.7-3 1.3l-2.8-2.2c-1-.8-2.5-.7-3.4.3l-2.8 2.8c-.9 1-1 2.4-.3 3.4l2.2 2.8c-.6.9-1 1.9-1.3 3l-3.5.6c-1.3.2-2.4 1.3-2.4 2.7v4c0 1.3 1.1 2.5 2.4 2.7l3.5.6c.3 1.1.7 2.1 1.3 3l-2.2 2.8c-.8 1-.7 2.5.3 3.4l2.8 2.8c1 .9 2.4 1 3.4.3l2.8-2.2c.9.6 1.9 1 3 1.3l.6 3.5c.2 1.3 1.3 2.4 2.7 2.4h4c1.3 0 2.5-1.1 2.7-2.4l.6-3.5c1.1-.3 2.1-.7 3-1.3l2.8 2.2c1 .8 2.5.7 3.4-.3l2.8-2.8c.9-1 1-2.4.3-3.4l-2.2-2.8c.6-.9 1-1.9 1.3-3l3.5-.6c1.3-.2 2.4-1.3 2.4-2.7v-4c0-1.4-1.1-2.5-2.4-2.7zM24 31c-3.9 0-7-3.1-7-7s3.1-7 7-7 7 3.1 7 7-3.1 7-7 7z"/></svg>`
    };

    let state = {};
    let pendingAction = null;
    let selectedAppKey = null;

    async function loadState() {
      const res = await fetch('/api/state');
      state = await res.json();
      populateIcons();
      renderUI();
    }

    function populateIcons() {
      // Main Grid Icons
      for (const [key, svgHtml] of Object.entries(OFFICIAL_ICONS)) {
        const el = document.getElementById(`icon-${key}`);
        if (el) {
          // preserve dot if existing
          const existingDot = el.querySelector('.shield-badge-dot');
          el.innerHTML = svgHtml;
          if (existingDot) el.appendChild(existingDot);
        }
      }
      // Dock Icons
      const dockPhone = document.getElementById('dock-phone');
      if (dockPhone) dockPhone.innerHTML = OFFICIAL_ICONS.phone;
      const dockMessages = document.getElementById('dock-messages');
      if (dockMessages) dockMessages.innerHTML = OFFICIAL_ICONS.messages;
      const dockChrome = document.getElementById('dock-chrome');
      if (dockChrome) dockChrome.innerHTML = OFFICIAL_ICONS.chrome;
      const dockCamera = document.getElementById('dock-camera');
      if (dockCamera) dockCamera.innerHTML = OFFICIAL_ICONS.camera;
    }

    function renderUI() {
      // Clock
      const now = new Date();
      const timeStr = now.toTimeString().slice(0, 5);
      document.getElementById('statusClock').innerText = timeStr;
      document.getElementById('widgetClock').innerText = timeStr;

      // Battery
      document.getElementById('statusBattery').innerText = `🔋 ${state.battery_percent}%`;
      document.getElementById('widgetBatteryPill').innerHTML = `<span>🔋 ${state.battery_days_remaining} Days Battery Remaining</span>`;
      document.getElementById('statBattery').innerText = `${state.battery_days_remaining} Days`;

      // Palette styling
      const screen = document.getElementById('phoneScreen');
      screen.classList.remove('palette-official', 'palette-monochrome', 'palette-amber', 'palette-emerald', 'palette-cyan');
      screen.classList.add(`palette-${state.palette || 'official'}`);

      // Hotspot Status
      const hsIcon = document.getElementById('statusHotspotIcon');
      const notifHs = document.getElementById('notifHotspot');
      if (state.is_hotspot_on) {
        hsIcon.classList.add('visible');
        notifHs.style.display = 'flex';
        document.getElementById('notifSsid').innerText = state.hotspot_ssid;
        document.getElementById('statHotspot').innerText = 'BROADCASTING';
        document.getElementById('statHotspot').style.color = 'var(--android-green)';
      } else {
        hsIcon.classList.remove('visible');
        notifHs.style.display = 'none';
        document.getElementById('statHotspot').innerText = 'OFF';
        document.getElementById('statHotspot').style.color = '#fff';
      }

      // Torch Status
      const torchNotif = document.getElementById('notifTorch');
      const phoneCont = document.getElementById('phoneContainer');
      if (state.is_torch_on) {
        torchNotif.style.display = 'flex';
        phoneCont.classList.add('torch-active');
      } else {
        torchNotif.style.display = 'none';
        phoneCont.classList.remove('torch-active');
      }

      // Grayscale
      if (state.is_grayscale) {
        screen.classList.add('grayscale-mode');
      } else {
        screen.classList.remove('grayscale-mode');
      }

      // Micro window
      if (state.is_micro_window) {
        screen.classList.add('micro-active');
        document.getElementById('statDisplay').innerText = '1Hz Reachability (0W)';
      } else {
        screen.classList.remove('micro-active');
        document.getElementById('statDisplay').innerText = state.is_grayscale ? '120Hz Grayscale' : '120Hz Full OLED';
      }

      // App badge dots
      for (const [key, app] of Object.entries(state.app_shields)) {
        const dot = document.getElementById(`dot-${key}`);
        if (dot) {
          if (app.data_cut) {
            dot.style.display = 'flex';
            dot.className = 'shield-badge-dot cut';
            dot.innerText = '✕';
          } else if (app.mic_muted) {
            dot.style.display = 'flex';
            dot.className = 'shield-badge-dot';
            dot.innerText = '🛡️';
          } else {
            dot.style.display = 'none';
          }
        }
      }

      // Kernel terminal
      const logsBox = document.getElementById('kernelLogs');
      logsBox.innerHTML = state.kernel_logs.map(l => `<div>${l}</div>`).join('');
      logsBox.scrollTop = logsBox.scrollHeight;
    }

    async function sendCommand(text) {
      if (!text) return;
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: text })
      });
      const data = await res.json();
      state = data.state;

      if (data.confirmation_required) {
        showConfirmationSheet(data.confirm_title, data.confirm_desc, data.confirm_bullets, data.action_name);
      } else if (data.message) {
        showToast(data.message);
      }
      renderUI();
    }

    function executeSearchCommand() {
      const input = document.getElementById('androidSearchInput');
      const val = input.value.trim();
      if (!val) return;
      input.value = '';
      sendCommand(val);
    }

    function quickRun(cmd) {
      sendCommand(cmd);
    }

    async function setPalette(paletteName) {
      sendCommand(`theme ${paletteName}`);
    }

    function triggerPowerButton() {
      const input = document.getElementById('androidSearchInput');
      input.focus();
      showToast("⚡ Power Button Long-Press: Search & Settings Armed");
    }

    function showConfirmationSheet(title, desc, bullets, actionName) {
      document.getElementById('sheetTitle').innerText = title;
      document.getElementById('sheetDesc').innerText = desc || '';
      document.getElementById('sheetBullets').innerHTML = bullets.map(b => `<li>${b}</li>`).join('');
      document.getElementById('materialSheet').classList.add('active');
      pendingAction = actionName;
    }

    function dismissSheet() {
      document.getElementById('materialSheet').classList.remove('active');
      pendingAction = null;
    }

    async function confirmSheetAction() {
      document.getElementById('materialSheet').classList.remove('active');
      if (!pendingAction) return;

      const res = await fetch('/api/confirm_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: pendingAction })
      });
      const data = await res.json();
      state = data.state;
      showToast(data.message);
      renderUI();
      pendingAction = null;
    }

    function showToast(msg) {
      const toast = document.getElementById('androidToast');
      toast.innerText = msg;
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }

    function launchApp(name) {
      showToast(`Opening ${name.charAt(0).toUpperCase() + name.slice(1)}...`);
    }

    function openAppShieldModal(appKey) {
      selectedAppKey = appKey;
      const app = state.app_shields[appKey];
      if (!app) return;

      document.getElementById('modalIcon').innerHTML = OFFICIAL_ICONS[appKey] || '';
      document.getElementById('modalTitle').innerText = app.name;
      document.getElementById('modalPkg').innerText = app.package;

      updateModalButtons(app);
      document.getElementById('appModal').classList.add('active');
    }

    function closeAppModal() {
      document.getElementById('appModal').classList.remove('active');
      selectedAppKey = null;
    }

    function updateModalButtons(app) {
      const btnData = document.getElementById('btnToggleData');
      const btnMic = document.getElementById('btnToggleMic');
      const btnFreeze = document.getElementById('btnToggleFreeze');

      btnData.className = app.data_cut ? 'switch-btn active' : 'switch-btn inactive';
      btnData.innerText = app.data_cut ? 'Blocked (0 B/s)' : 'Allowed';

      btnMic.className = app.mic_muted ? 'switch-btn active' : 'switch-btn inactive';
      btnMic.innerText = app.mic_muted ? 'Muted' : 'Allowed';

      btnFreeze.className = app.is_frozen ? 'switch-btn active' : 'switch-btn inactive';
      btnFreeze.innerText = app.is_frozen ? 'Sleeping' : 'Awake';
    }

    async function toggleShield(type) {
      if (!selectedAppKey) return;
      const res = await fetch('/api/toggle_shield', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_key: selectedAppKey, shield_type: type })
      });
      const data = await res.json();
      state = data.state;
      updateModalButtons(state.app_shields[selectedAppKey]);
      renderUI();
      showToast(data.message);
    }

    function launchCurrentModalApp() {
      if (!selectedAppKey) return;
      const name = state.app_shields[selectedAppKey].name;
      closeAppModal();
      showToast(`Launching ${name}...`);
    }

    function toggleMicroDisplay(enable) {
      sendCommand(enable ? 'micro window' : 'micro window off');
    }

    // Auto-refresh clock
    loadState();
    setInterval(() => {
      const now = new Date();
      const timeStr = now.toTimeString().slice(0, 5);
      document.getElementById('statusClock').innerText = timeStr;
      document.getElementById('widgetClock').innerText = timeStr;
    }, 10000);
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/state")
def get_state():
    return jsonify(STATE)

@app.route("/api/command", methods=["POST"])
def process_command():
    data = request.json or {}
    raw_cmd = data.get("command", "").strip()
    lower = raw_cmd.lower()

    # THEME / PALETTE CHANGE
    if "theme" in lower or "color" in lower or "palette" in lower:
        if "amber" in lower:
            STATE["palette"] = "amber"
            msg = "🎨 Theme set to Warm Amber (0% blue light)."
        elif "green" in lower or "emerald" in lower:
            STATE["palette"] = "emerald"
            msg = "🎨 Theme set to Phosphor Emerald (Max OLED subpixel efficiency)."
        elif "cyan" in lower or "blue" in lower or "glacier" in lower:
            STATE["palette"] = "cyan"
            msg = "🎨 Theme set to Nordic Glacier Cyan."
        elif "mono" in lower or "white" in lower:
            STATE["palette"] = "monochrome"
            msg = "🎨 Theme set to Zen Monochrome White."
        else:
            STATE["palette"] = "official"
            msg = "🎨 Theme set to Official Full-Color Brand Logos."
        STATE["kernel_logs"].append(f"[THEME] Applied surface palette: {STATE['palette']}")
        return jsonify({"success": True, "message": msg, "state": STATE})

    # 1. HARDWARE: FLASHLIGHT
    if "flash" in lower or "torch" in lower:
        is_off = "off" in lower or "stop" in lower or "disable" in lower
        STATE["is_torch_on"] = not is_off
        msg = "🔦 Flashlight turned ON." if STATE["is_torch_on"] else "🔦 Flashlight turned OFF."
        STATE["kernel_logs"].append(f"[SYS_GPIO] cameraManager.setTorchMode(0, {STATE['is_torch_on']}) -> SUCCESS")
        return jsonify({"success": True, "message": msg, "state": STATE})

    # 2. HARDWARE: WI-FI HOTSPOT
    if "hotspot" in lower or "tether" in lower:
        is_off = "off" in lower or "stop" in lower or "disable" in lower
        STATE["is_hotspot_on"] = not is_off
        if STATE["is_hotspot_on"]:
            STATE["kernel_logs"].append("[HOSTAPD] /system/bin/hostapd -B /data/misc/wifi/hostapd.conf -> AP iface wlan0 UP")
            STATE["kernel_logs"].append(f"[HOSTAPD] Broadcasting SSID='{STATE['hotspot_ssid']}', WPA3-SAE (Band 5GHz Ch36)")
            STATE["kernel_logs"].append("[DNSMASQ] DHCP daemon active on 192.168.43.1/24 (DHCP lease pool: .100 - .200)")
            STATE["kernel_logs"].append("[IPTABLES] iptables -t nat -A POSTROUTING -s 192.168.43.0/24 -o rmnet_data0 -j MASQUERADE")
            STATE["kernel_logs"].append("[TETHER] TetheringManager: Client associated [3a:77:81:4c:0b:92] -> Assigned 192.168.43.125")
            msg = f"(((•))) Hotspot ACTIVE: Broadcasting '{STATE['hotspot_ssid']}'. 1 device connected."
        else:
            STATE["kernel_logs"].append("[HOSTAPD] hostapd daemon stopped. AP interface wlan0 DOWN.")
            STATE["kernel_logs"].append("[IPTABLES] Flushed POSTROUTING NAT rules for wlan0.")
            msg = "(((•))) Hotspot turned OFF."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # 3. HARDWARE: GRAYSCALE (Material 3 Confirmation Sheet)
    if "grayscale" in lower or "monochrome" in lower or "black and white" in lower:
        is_off = "off" in lower or "disable" in lower
        if is_off:
            STATE["is_grayscale"] = False
            STATE["kernel_logs"].append("[DALTONIZER] Settings.Secure.putInt('accessibility_display_daltonizer_enabled', 0)")
            return jsonify({"success": True, "message": "🌈 Color display restored.", "state": STATE})
        else:
            return jsonify({
                "confirmation_required": True,
                "confirm_title": "Turn on Grayscale?",
                "confirm_desc": "Converts all screen pixels to monochrome black & white.",
                "confirm_bullets": [
                    "Eliminates dopamine triggers and screen addiction.",
                    "Saves up to 18% OLED battery power.",
                    "You can turn it off anytime from the search bar or settings."
                ],
                "action_name": "enable_grayscale",
                "state": STATE
            })

    # 4. REBOOT / RESTART (Material 3 Confirmation Sheet)
    if "restart" in lower or "reboot" in lower:
        return jsonify({
            "confirmation_required": True,
            "confirm_title": "Restart Phone?",
            "confirm_desc": "Restarts Linux kernel and ZeroOS Android system server.",
            "confirm_bullets": [
                "Clears volatile RAM cache buffers.",
                "System will be back online in ~20 seconds."
            ],
            "action_name": "reboot_system",
            "state": STATE
        })

    # 5. NOKIA 4-DAY BATTERY MODE (Material 3 Confirmation Sheet)
    if "nokia" in lower or "deep sleep" in lower:
        is_off = "off" in lower or "exit" in lower
        if is_off:
            STATE["is_nokia_mode"] = False
            STATE["battery_days_remaining"] = 4.2
            return jsonify({"success": True, "message": "Nokia deep sleep mode deactivated.", "state": STATE})
        else:
            return jsonify({
                "confirmation_required": True,
                "confirm_title": "Turn on Nokia Mode?",
                "confirm_desc": "Forces CPU into deep Linux C-states with e-ink screen refresh rates.",
                "confirm_bullets": [
                    "Extends phone battery longevity to 4–6 full days.",
                    "Halts background ad tracking and social sync.",
                    "Incoming phone calls and SMS messages still ring 100% reliably."
                ],
                "action_name": "enable_nokia_mode",
                "state": STATE
            })

    # 6. REACHABILITY / MICRO DISPLAY
    if "micro" in lower or "sub display" in lower or "reachability" in lower:
        is_off = "off" in lower or "exit" in lower or "full" in lower
        STATE["is_micro_window"] = not is_off
        STATE["kernel_logs"].append(f"[SurfaceFlinger] Display bounding canvas clamped to bottom one-hand box. 80% OLED = 0W.")
        msg = "⚡ OLED Micro Mode ACTIVE: 80% of screen powered off (0W draw)." if STATE["is_micro_window"] else "Full OLED display restored."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # 7. ABOUT PHONE
    if "about" in lower or "system info" in lower:
        STATE["kernel_logs"].append("[UNAME] Linux zero-phone 5.10.198-aosp-hardened #1 PREEMPT")
        return jsonify({
            "success": True,
            "message": "📱 ZeroPhone Pro · Android 12 AOSP · Linux 5.10 Kernel · 8GB LPDDR5 · 6,000 mAh",
            "state": STATE
        })

    # 8. PRIVACY AUDIT
    if "spying" in lower or "audit" in lower:
        STATE["kernel_logs"].append("[PROC_NET] Audited active sockets. 42 background Meta beacons dropped.")
        return jsonify({
            "success": True,
            "message": "🛡️ Security Audit: 42 background trackers blocked. Microphone register SECURED.",
            "state": STATE
        })

    # 9. CUT DATA FOR APPS
    if "cut data" in lower or "block data" in lower:
        targets = [k for k in STATE["app_shields"].keys() if k in lower]
        if not targets:
            targets = ["instagram", "tiktok"]
        for t in targets:
            app = STATE["app_shields"][t]
            app["data_cut"] = True
            STATE["kernel_logs"].append(f"[iptables] iptables -I OUTPUT -m owner --uid-owner {app['package']} -j DROP")
        names = [STATE["app_shields"][t]["name"] for t in targets]
        return jsonify({
            "success": True,
            "message": f"⚡ Data severed at kernel level for: {', '.join(names)}.",
            "state": STATE
        })

    # 10. MUTE MIC FOR APPS
    if "mute mic" in lower or "kill mic" in lower:
        targets = [k for k in STATE["app_shields"].keys() if k in lower]
        if not targets:
            targets = ["whatsapp", "instagram"]
        for t in targets:
            app = STATE["app_shields"][t]
            app["mic_muted"] = True
            STATE["kernel_logs"].append(f"[AppOps] cmd appops set {app['package']} RECORD_AUDIO deny")
        names = [STATE["app_shields"][t]["name"] for t in targets]
        return jsonify({
            "success": True,
            "message": f"🎙️ Microphone hardware register LOCKED for: {', '.join(names)}.",
            "state": STATE
        })

    return jsonify({"success": True, "message": f"Opening '{raw_cmd}'...", "state": STATE})

@app.route("/api/confirm_action", methods=["POST"])
def confirm_action():
    action = (request.json or {}).get("action")
    if action == "enable_grayscale":
        STATE["is_grayscale"] = True
        STATE["kernel_logs"].append("[DALTONIZER] Settings.Secure.putInt('accessibility_display_daltonizer_enabled', 1)")
        STATE["kernel_logs"].append("[DALTONIZER] Settings.Secure.putInt('accessibility_display_daltonizer', 0)")
        return jsonify({"success": True, "message": "🌓 Grayscale Mode turned ON.", "state": STATE})

    elif action == "reboot_system":
        STATE["kernel_logs"].append("[POWER] PowerManager.reboot('User Command') -> Re-executing system server")
        return jsonify({"success": True, "message": "🔄 System restarting...", "state": STATE})

    elif action == "enable_nokia_mode":
        STATE["is_nokia_mode"] = True
        STATE["battery_days_remaining"] = 5.8
        STATE["kernel_logs"].append("[CPUFREQ] Scaled governor to powersave. Deep Linux C-states forced.")
        return jsonify({"success": True, "message": "🔋 Nokia 5-Day Battery Mode turned ON.", "state": STATE})

    return jsonify({"success": False, "message": "Unknown action", "state": STATE})

@app.route("/api/toggle_shield", methods=["POST"])
def toggle_shield():
    data = request.json or {}
    app_key = data.get("app_key")
    shield_type = data.get("shield_type")

    if app_key not in STATE["app_shields"]:
        return jsonify({"success": False, "message": "App not found", "state": STATE})

    app_obj = STATE["app_shields"][app_key]
    if shield_type == "data":
        app_obj["data_cut"] = not app_obj["data_cut"]
        act = "CUT (0 B/s)" if app_obj["data_cut"] else "RESTORED"
        STATE["kernel_logs"].append(f"[iptables] Mobile & Wi-Fi data {act} for {app_obj['package']}")
        msg = f"Data {act} for {app_obj['name']}."

    elif shield_type == "mic":
        app_obj["mic_muted"] = not app_obj["mic_muted"]
        act = "MUTED" if app_obj["mic_muted"] else "UNMUTED"
        STATE["kernel_logs"].append(f"[AppOps] Microphone hardware {act} for {app_obj['package']}")
        msg = f"Microphone {act} for {app_obj['name']}."

    elif shield_type == "freeze":
        app_obj["is_frozen"] = not app_obj["is_frozen"]
        act = "HIBERNATED" if app_obj["is_frozen"] else "AWOKEN"
        STATE["kernel_logs"].append(f"[PM] pm {'suspend' if app_obj['is_frozen'] else 'unsuspend'} {app_obj['package']}")
        msg = f"{app_obj['name']} is now {act}."
    else:
        msg = "Unknown shield toggle"

    return jsonify({"success": True, "message": msg, "state": STATE})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5077))
    print(f"ZeroOS Simple Android UI Simulator running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
