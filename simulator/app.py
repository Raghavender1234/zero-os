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
    "auto_airgap_enabled": True,  # Automatic zero-leak background killer
    "active_app": None,           # Currently running foreground app (null = Home)
    "is_ephemeral": False,        # Whether active app is in disposable RAM sandbox
    "palette": "official",        # official, monochrome, amber, emerald, cyan
    "screen_refresh_hz": 120,
    "battery_percent": 88,
    "battery_days_remaining": 4.2,
    "calm_digest_enabled": True,
    "calm_digest_items": [
        {"id": 1, "app": "Instagram", "title": "Social Update", "desc": "alex_99 and 4 others liked your story", "time": "18m ago"},
        {"id": 2, "app": "TikTok", "title": "Recommendation", "desc": "Trending sound: 'Midnight Beats' in your area", "time": "45m ago"},
        {"id": 3, "app": "UberEats", "title": "Promotion", "desc": "30% off your next lunch order before 2 PM", "time": "2h ago"}
    ],
    "impact_stats": {
        "trackers_blocked": 1420,
        "battery_hours_saved": 3.8,
        "mic_hours_locked": 22.4,
        "airgapped_apps": 8
    },
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
        "[0.840000] AutoAirGapManager registered. Zero-leak background killer armed",
        "[1.020000] SystemUI / Launcher booted. Material 3 Shell online (120Hz)"
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ZeroOS - Pure Everyday Operating System</title>
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
      gap: 32px;
      align-items: flex-start;
      justify-content: center;
      max-width: 1240px;
      width: 100%;
      flex-wrap: wrap;
    }

    /* REALISTIC ANDROID PHONE HARDWARE */
    .phone-container {
      position: relative;
    }
    .phone-body {
      width: 380px;
      height: 790px;
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

    /* Physical buttons */
    .hw-btn-power {
      position: absolute;
      right: -13px;
      top: 170px;
      width: 5px;
      height: 58px;
      background: #3a4252;
      border-radius: 0 4px 4px 0;
      cursor: pointer;
      transition: background 0.15s;
    }
    .hw-btn-power:active { background: var(--android-accent); }
    .hw-btn-vol-up {
      position: absolute;
      left: -13px;
      top: 150px;
      width: 5px;
      height: 50px;
      background: #3a4252;
      border-radius: 4px 0 0 4px;
    }
    .hw-btn-vol-down {
      position: absolute;
      left: -13px;
      top: 215px;
      width: 5px;
      height: 50px;
      background: #3a4252;
      border-radius: 4px 0 0 4px;
    }

    /* OLED SCREEN CONTAINER */
    .oled-screen {
      flex: 1;
      background: #000000;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      transition: filter 0.3s ease;
    }
    .oled-screen.grayscale-active {
      filter: grayscale(100%);
    }
    .oled-screen.nokia-active {
      filter: grayscale(100%) contrast(140%);
    }

    /* Punch-hole Camera */
    .camera-punch-hole {
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      width: 14px;
      height: 14px;
      background: #000;
      border: 1.5px solid #14171d;
      border-radius: 50%;
      z-index: 100;
    }

    /* 1. ANDROID STATUS BAR */
    .android-status-bar {
      height: 38px;
      padding: 0 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.72rem;
      font-weight: 500;
      color: #cbd5e1;
      z-index: 90;
      background: transparent;
    }
    .status-left {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .status-right {
      display: flex;
      align-items: center;
      gap: 7px;
    }
    .hardware-indicator {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      padding: 2px 6px;
      border-radius: 10px;
      font-size: 0.65rem;
      font-weight: 600;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.65; }
    }

    /* DYNAMIC NOTIFICATION PILL / BANNER */
    .hotspot-banner {
      margin: 4px 14px 6px 14px;
      background: #141a24;
      border: 1px solid #1e293b;
      border-radius: 14px;
      padding: 8px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .hotspot-banner-title {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #e2e8f0;
      font-weight: 500;
    }
    .hotspot-kill-btn {
      background: #ef4444;
      color: #fff;
      border: none;
      padding: 4px 10px;
      border-radius: 10px;
      font-size: 0.7rem;
      font-weight: 600;
      cursor: pointer;
    }

    /* HOME SCREEN SCROLL AREA */
    .home-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 0 16px;
      overflow-y: auto;
      scrollbar-width: none;
    }
    .home-content::-webkit-scrollbar { display: none; }

    /* 3. DIGITAL CLOCK & BATTERY AT A GLANCE */
    .digital-clock-widget {
      text-align: center;
      margin: 10px 0 8px 0;
    }
    .clock-digits {
      font-size: 3.2rem;
      font-weight: 300;
      color: #ffffff;
      letter-spacing: -1.5px;
      line-height: 1;
    }
    .battery-pill-glance {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 6px;
      font-size: 0.73rem;
      color: #94a3b8;
    }
    .nokia-mode-badge {
      display: inline-block;
      margin-left: 6px;
      padding: 2px 7px;
      border-radius: 10px;
      font-size: 0.65rem;
      font-weight: 700;
      background: #ffffff;
      color: #000000;
    }

    /* CALM DIGEST PILL */
    .calm-digest-pill {
      margin: 4px 0 10px 0;
      background: #111620;
      border: 1px solid #1c2433;
      border-radius: 16px;
      padding: 7px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: background 0.15s;
    }
    .calm-digest-pill:hover { background: #161e2e; }
    .digest-pill-text {
      font-size: 0.72rem;
      color: #94a3b8;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .digest-count-badge {
      background: #2563eb;
      color: #fff;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 8px;
    }

    /* ZERO IMPACT METRICS CARD */
    .impact-metrics-card {
      background: #0d121a;
      border: 1px solid #182232;
      border-radius: 16px;
      padding: 10px 12px;
      margin-bottom: 12px;
    }
    .impact-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .impact-card-title {
      font-size: 0.72rem;
      font-weight: 600;
      color: #cbd5e1;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .impact-badge-safe {
      font-size: 0.62rem;
      color: #34d399;
      background: rgba(52, 211, 153, 0.1);
      padding: 1px 6px;
      border-radius: 6px;
    }
    .impact-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      text-align: center;
    }
    .impact-tile {
      background: #141b26;
      padding: 6px 4px;
      border-radius: 10px;
    }
    .impact-val {
      font-size: 0.85rem;
      font-weight: 700;
      color: #fff;
      line-height: 1.1;
    }
    .impact-lbl {
      font-size: 0.58rem;
      color: #64748b;
      margin-top: 2px;
    }

    /* 4. NATURAL LANGUAGE COMMAND SEARCH BAR */
    .search-command-bar {
      background: #181d26;
      border-radius: 24px;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
      border: 1px solid #232a38;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .search-icon { font-size: 0.9rem; color: #94a3b8; }
    .search-input {
      background: transparent;
      border: none;
      color: #fff;
      font-size: 0.82rem;
      flex: 1;
      outline: none;
      font-family: inherit;
    }
    .search-input::placeholder { color: #64748b; }
    .search-mic {
      font-size: 0.85rem;
      color: var(--android-primary);
      cursor: pointer;
    }

    /* QUICK CHIPS ROW */
    .quick-chips-row {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 8px;
      margin-bottom: 10px;
      scrollbar-width: none;
    }
    .quick-chips-row::-webkit-scrollbar { display: none; }
    .android-chip {
      background: #161b24;
      color: #cbd5e1;
      padding: 5px 11px;
      border-radius: 14px;
      font-size: 0.72rem;
      white-space: nowrap;
      cursor: pointer;
      border: 1px solid #222938;
      transition: background 0.15s, border-color 0.15s;
    }
    .android-chip:hover {
      background: #202734;
      border-color: #3b465c;
    }

    /* 5. STANDARD ANDROID APP ICONS GRID (Border-Free Official SVGs) */
    .apps-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      row-gap: 16px;
      column-gap: 8px;
      margin-bottom: 16px;
      text-align: center;
    }
    .app-icon-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      position: relative;
    }
    .app-icon-item:active { transform: scale(0.92); }
    .app-icon-shape {
      width: 50px;
      height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
      position: relative;
      transition: filter 0.2s;
    }
    .app-icon-shape svg {
      width: 100%;
      height: 100%;
    }
    .app-label {
      font-size: 0.68rem;
      color: #cbd5e1;
      margin-top: 5px;
      font-weight: 400;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 68px;
    }
    .shield-badge-dot {
      position: absolute;
      top: -2px;
      right: -2px;
      font-size: 0.75rem;
      z-index: 10;
    }

    /* PALETTE FILTERS */
    .palette-monochrome .app-icon-shape svg { filter: grayscale(100%) brightness(1.2); }
    .palette-amber .app-icon-shape svg { filter: sepia(100%) saturate(300%) hue-rotate(5deg) brightness(1.1); }
    .palette-emerald .app-icon-shape svg { filter: sepia(100%) saturate(400%) hue-rotate(95deg) brightness(1.1); }
    .palette-cyan .app-icon-shape svg { filter: sepia(100%) saturate(400%) hue-rotate(150deg) brightness(1.2); }

    /* 6. ANDROID DOCK */
    .android-dock {
      display: flex;
      justify-content: space-around;
      align-items: center;
      padding: 10px 16px 6px 16px;
      background: transparent;
    }

    /* 7. GESTURE NAVIGATION PILL */
    .gesture-bar-container {
      height: 22px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
    }
    .gesture-bar {
      width: 80px;
      height: 4px;
      background: #475569;
      border-radius: 3px;
    }

    /* ACTIVE FOREGROUND APP WINDOW */
    .active-app-window {
      position: absolute;
      top: 38px;
      left: 0;
      right: 0;
      bottom: 0;
      background: #090c10;
      z-index: 80;
      display: flex;
      flex-direction: column;
      animation: slideUp 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

    .app-window-header {
      padding: 12px 16px;
      background: #141923;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #202838;
    }
    .app-header-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .app-header-icon {
      width: 28px;
      height: 28px;
    }
    .app-header-title {
      font-size: 0.92rem;
      font-weight: 600;
      color: #fff;
    }
    .badge-ephemeral {
      font-size: 0.62rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 8px;
      background: #dc2626;
      color: #fff;
    }
    .badge-normal-airgap {
      font-size: 0.62rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 8px;
      background: #059669;
      color: #fff;
    }
    .btn-close-app {
      background: #232c3d;
      color: #cbd5e1;
      border: none;
      padding: 6px 12px;
      border-radius: 12px;
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-close-app:hover { background: #334155; color: #fff; }

    .app-window-body {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
    }
    .app-window-footer {
      padding: 12px 16px;
      background: #0f131a;
      border-top: 1px solid #1e2636;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }
    .swipe-home-btn {
      width: 100%;
      background: #1e2636;
      border: 1px solid #2d3748;
      color: #38bdf8;
      padding: 10px;
      border-radius: 14px;
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .swipe-home-btn:hover { background: #283548; }

    /* CHAT BUBBLES IN DEMO */
    .chat-bubble {
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 0.8rem;
      max-width: 82%;
      margin-bottom: 12px;
      line-height: 1.4;
    }
    .chat-bubble.left {
      background: #1e2636;
      color: #e2e8f0;
      align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .chat-bubble.right {
      background: #10b981;
      color: #000;
      font-weight: 500;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }

    /* MATERIAL 3 SHEETS & MODALS */
    .material-sheet-overlay {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: #181c25;
      border-radius: 28px 28px 0 0;
      padding: 22px 20px;
      border-top: 1px solid #28303f;
      transform: translateY(100%);
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 110;
      box-shadow: 0 -10px 40px rgba(0,0,0,0.8);
    }
    .material-sheet-overlay.active { transform: translateY(0); }
    .sheet-handle {
      width: 36px;
      height: 4px;
      background: #475569;
      border-radius: 2px;
      margin: 0 auto 16px auto;
    }
    .sheet-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #fff;
      margin-bottom: 8px;
    }
    .sheet-desc {
      font-size: 0.8rem;
      color: #94a3b8;
      line-height: 1.45;
      margin-bottom: 14px;
    }
    .sheet-bullets {
      list-style: none;
      margin-bottom: 18px;
    }
    .sheet-bullets li {
      font-size: 0.76rem;
      color: #cbd5e1;
      padding-left: 18px;
      position: relative;
      margin-bottom: 6px;
    }
    .sheet-bullets li::before {
      content: "•";
      position: absolute;
      left: 4px;
      color: var(--android-primary);
      font-weight: bold;
    }
    .sheet-actions {
      display: flex;
      gap: 12px;
    }
    .btn-android-primary {
      flex: 1;
      background: var(--android-primary);
      color: #0c0f14;
      border: none;
      padding: 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
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

    /* CALM DIGEST LIST ITEM */
    .digest-list-item {
      background: #1e2636;
      border-radius: 12px;
      padding: 10px 12px;
      margin-bottom: 8px;
    }
    .digest-item-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 3px;
    }
    .digest-item-app {
      font-size: 0.72rem;
      font-weight: 700;
      color: #a8c7fa;
    }
    .digest-item-time {
      font-size: 0.65rem;
      color: #64748b;
    }
    .digest-item-body {
      font-size: 0.75rem;
      color: #e2e8f0;
      line-height: 1.35;
    }

    /* TOAST */
    .android-toast {
      position: absolute;
      bottom: 45px;
      left: 50%;
      transform: translateX(-50%);
      background: #27303f;
      color: #fff;
      padding: 9px 18px;
      border-radius: 24px;
      font-size: 0.75rem;
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      display: none;
      z-index: 120;
      white-space: nowrap;
      border: 1px solid #374151;
    }

    /* RIGHT TELEMETRY & KERNEL LOG MONITOR */
    .telemetry-side {
      flex: 1;
      min-width: 320px;
      max-width: 480px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .side-box {
      background: #11151d;
      border: 1px solid #1c2330;
      border-radius: 20px;
      padding: 16px 18px;
    }
    .side-box-title {
      font-size: 0.88rem;
      font-weight: 600;
      color: #fff;
      margin-bottom: 10px;
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
      background: #171d28;
      padding: 10px;
      border-radius: 12px;
      border: 1px solid #222b3b;
    }
    .stat-label { font-size: 0.68rem; color: #94a3b8; }
    .stat-val { font-size: 1.05rem; font-weight: 600; color: #fff; margin-top: 2px; }

    .kernel-terminal {
      background: #080a0e;
      border: 1px solid #1a202c;
      border-radius: 12px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      color: #38bdf8;
      height: 220px;
      overflow-y: auto;
      line-height: 1.45;
    }
  </style>
</head>
<body>

  <div class="top-header">
    <h1>📱 ZeroOS · Pure Everyday Operating System</h1>
    <p>Zero-Leak Automatic Air-Gap · Calm Digest · Nokia 4-Day Mode · Ephemeral Disposable Sandbox</p>
  </div>

  <div class="main-layout">

    <!-- REALISTIC PHONE HARDWARE -->
    <div class="phone-container">
      <div class="hw-btn-power" onclick="triggerPowerButton()" title="Power Button (Click to trigger voice/text bar)"></div>
      <div class="hw-btn-vol-up" onclick="showToast('Volume Up')"></div>
      <div class="hw-btn-vol-down" onclick="showToast('Volume Down')"></div>

      <div class="phone-body">
        
        <div class="camera-punch-hole"></div>

        <div class="oled-screen" id="oledScreen">

          <!-- 1. ANDROID STATUS BAR -->
          <div class="android-status-bar">
            <div class="status-left">
              <span id="statusClock">11:28</span>
              <span id="statusTorch" style="display:none;">🔦</span>
              <span id="statusHotspot" class="hardware-indicator" style="display:none;">(((•)))</span>
            </div>
            <div class="status-right">
              <span id="statusShield" title="Auto Air-Gap Active">🛡️</span>
              <span id="status5G">5G</span>
              <span id="statusBattery">🔋 88%</span>
            </div>
          </div>

          <!-- NOTIFICATION BANNER (Hotspot / Sensor Kill) -->
          <div id="hotspotBanner" class="hotspot-banner" style="display:none;">
            <div class="hotspot-banner-title">
              <span>(((•))) Hotspot Active</span>
            </div>
            <button class="hotspot-kill-btn" onclick="sendCommand('turn off hotspot')">Stop</button>
          </div>

          <!-- FOREGROUND ACTIVE APP WINDOW -->
          <div id="activeAppWindow" class="active-app-window" style="display:none;">
            <div class="app-window-header">
              <div class="app-header-left">
                <div class="app-header-icon" id="appHeaderIcon"></div>
                <div>
                  <div class="app-header-title" id="appHeaderTitle">WhatsApp</div>
                  <span id="appHeaderBadge" class="badge-normal-airgap">AIR-GAP PROTECTED</span>
                </div>
              </div>
              <button class="btn-close-app" onclick="closeActiveApp()">Close & Air-Gap</button>
            </div>
            
            <div class="app-window-body" id="appWindowBody">
              <!-- Rendered per app -->
            </div>

            <div class="app-window-footer">
              <button class="swipe-home-btn" onclick="closeActiveApp()">
                <span>⬆️ Swipe Home to Cut Network & Lock Mic</span>
              </button>
              <div class="gesture-bar-container" onclick="closeActiveApp()">
                <div class="gesture-bar"></div>
              </div>
            </div>
          </div>

          <!-- 2. HOME SCREEN CONTENT -->
          <div class="home-content">

            <!-- 3. DIGITAL CLOCK & BATTERY AT A GLANCE -->
            <div class="digital-clock-widget">
              <div class="clock-digits" id="widgetClock">11:28</div>
              <div class="battery-pill-glance">
                <span id="widgetBatteryText">🔋 4.2 Days Battery Remaining</span>
                <span id="widgetNokiaBadge" class="nokia-mode-badge" style="display:none;">NOKIA MODE</span>
              </div>
            </div>

            <!-- CALM DIGEST PILL -->
            <div class="calm-digest-pill" onclick="openCalmDigestSheet()">
              <div class="digest-pill-text">
                <span>🔕 Calm Digest</span>
                <span class="digest-count-badge" id="digestCountBadge">3 alerts held</span>
              </div>
              <span style="font-size:0.75rem; color:#64748b;">View ›</span>
            </div>

            <!-- ZERO IMPACT DASHBOARD CARD -->
            <div class="impact-metrics-card">
              <div class="impact-card-header">
                <span class="impact-card-title">🛡️ Zero-Leak Impact Today</span>
                <span class="impact-badge-safe">AIR-GAP ACTIVE</span>
              </div>
              <div class="impact-grid">
                <div class="impact-tile">
                  <div class="impact-val" id="impactTrackers">1,420</div>
                  <div class="impact-lbl">Trackers Blocked</div>
                </div>
                <div class="impact-tile">
                  <div class="impact-val" id="impactBattery">3.8h</div>
                  <div class="impact-lbl">Battery Saved</div>
                </div>
                <div class="impact-tile">
                  <div class="impact-val" id="impactMic">22.4h</div>
                  <div class="impact-lbl">Mic Locked</div>
                </div>
                <div class="impact-tile">
                  <div class="impact-val" id="impactAirgapped">8</div>
                  <div class="impact-lbl">Apps Air-Gapped</div>
                </div>
              </div>
            </div>

            <!-- 4. NATURAL LANGUAGE COMMAND & SEARCH BAR -->
            <div class="search-command-bar">
              <span class="search-icon">🔍</span>
              <input type="text" id="androidSearchInput" class="search-input" placeholder="Type plain English (e.g. hotspot, nokia mode, cut mic)..." onkeydown="if(event.key==='Enter') executeSearchCommand()" />
              <span class="search-mic" onclick="executeSearchCommand()" title="Execute Command">↵</span>
            </div>

            <!-- QUICK CHIPS ROW -->
            <div class="quick-chips-row">
              <div class="android-chip" onclick="quickRun('turn on hotspot')">(((•))) Hotspot</div>
              <div class="android-chip" onclick="quickRun('nokia mode')">🔋 Nokia Mode</div>
              <div class="android-chip" onclick="quickRun('turn on flash')">🔦 Torch</div>
              <div class="android-chip" onclick="quickRun('turn on grayscale')">🌓 Grayscale</div>
              <div class="android-chip" onclick="quickRun('calm digest')">🔕 Calm Digest</div>
              <div class="android-chip" onclick="quickRun('ephemeral instagram')">🛡️ Ephemeral IG</div>
              <div class="android-chip" onclick="quickRun('cut mic for whatsapp')">🎙️ Cut WhatsApp Mic</div>
            </div>

            <!-- 5. STANDARD ANDROID APP ICONS GRID -->
            <div class="apps-grid">
              
              <div class="app-icon-item" onclick="launchForegroundApp('phone')">
                <div class="app-icon-shape" id="icon-phone"></div>
                <div class="app-label">Phone</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('messages')">
                <div class="app-icon-shape" id="icon-messages"></div>
                <div class="app-label">Messages</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('chrome')">
                <div class="app-icon-shape" id="icon-chrome"></div>
                <div class="app-label">Chrome</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('camera')">
                <div class="app-icon-shape" id="icon-camera"></div>
                <div class="app-label">Camera</div>
              </div>

              <!-- Mainstream Apps with Automatic Air-Gap Protection -->
              <div class="app-icon-item" onclick="launchForegroundApp('whatsapp')">
                <div class="app-icon-shape" id="icon-whatsapp">
                  <span class="shield-badge-dot" id="dot-whatsapp" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">WhatsApp</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('instagram')">
                <div class="app-icon-shape" id="icon-instagram">
                  <span class="shield-badge-dot" id="dot-instagram" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">Instagram</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('tiktok')">
                <div class="app-icon-shape" id="icon-tiktok">
                  <span class="shield-badge-dot" id="dot-tiktok" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">TikTok</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('youtube')">
                <div class="app-icon-shape" id="icon-youtube">
                  <span class="shield-badge-dot" id="dot-youtube" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">YouTube</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('monzo')">
                <div class="app-icon-shape" id="icon-monzo">
                  <span class="shield-badge-dot" id="dot-monzo" style="display:none;">🛡️</span>
                </div>
                <div class="app-label">Monzo</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('spotify')">
                <div class="app-icon-shape" id="icon-spotify"></div>
                <div class="app-label">Spotify</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('maps')">
                <div class="app-icon-shape" id="icon-maps"></div>
                <div class="app-label">Maps</div>
              </div>

              <div class="app-icon-item" onclick="quickRun('about phone')">
                <div class="app-icon-shape" id="icon-settings"></div>
                <div class="app-label">Settings</div>
              </div>

            </div>

            <!-- 6. STANDARD ANDROID DOCK -->
            <div class="android-dock">
              <div class="app-icon-item" onclick="launchForegroundApp('phone')">
                <div class="app-icon-shape" id="dock-phone"></div>
              </div>
              <div class="app-icon-item" onclick="launchForegroundApp('messages')">
                <div class="app-icon-shape" id="dock-messages"></div>
              </div>
              <div class="app-icon-item" onclick="launchForegroundApp('chrome')">
                <div class="app-icon-shape" id="dock-chrome"></div>
              </div>
              <div class="app-icon-item" onclick="launchForegroundApp('camera')">
                <div class="app-icon-shape" id="dock-camera"></div>
              </div>
            </div>

            <!-- 7. GESTURE NAVIGATION PILL -->
            <div class="gesture-bar-container">
              <div class="gesture-bar"></div>
            </div>

          </div>

          <!-- MATERIAL 3 CONFIRMATION BOTTOM SHEET -->
          <div class="material-sheet-overlay" id="materialSheet">
            <div class="sheet-handle"></div>
            <div class="sheet-title" id="sheetTitle">Confirmation</div>
            <div class="sheet-desc" id="sheetDesc">Description</div>
            <ul class="sheet-bullets" id="sheetBullets"></ul>
            <div class="sheet-actions">
              <button class="btn-android-secondary" onclick="dismissSheet()">Cancel</button>
              <button class="btn-android-primary" onclick="confirmSheetAction()">Turn On</button>
            </div>
          </div>

          <!-- CALM DIGEST BOTTOM SHEET -->
          <div class="material-sheet-overlay" id="digestSheet">
            <div class="sheet-handle"></div>
            <div class="sheet-title">🔕 Calm Notification Digest</div>
            <div class="sheet-desc">
              Non-urgent alerts held quietly to protect your focus and battery.
            </div>
            <div id="digestItemsList"></div>
            <div class="sheet-actions" style="margin-top:12px;">
              <button class="btn-android-secondary" onclick="dismissDigestSheet()">Close</button>
              <button class="btn-android-primary" onclick="clearDigestSheet()">Mark All Read</button>
            </div>
          </div>

          <!-- TOAST -->
          <div class="android-toast" id="androidToast">Action performed</div>

        </div>
      </div>
    </div>

    <!-- RIGHT TELEMETRY & KERNEL LOG MONITOR -->
    <div class="telemetry-side">
      
      <!-- COLOR PALETTES -->
      <div class="side-box">
        <div class="side-box-title">🎨 Display Themes (Screen Remains 100% OLED Black)</div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">
          <button class="android-chip" onclick="setPalette('official')">🌈 Official Colors</button>
          <button class="android-chip" onclick="setPalette('monochrome')">⚪ Zen White (Mono)</button>
          <button class="android-chip" onclick="setPalette('amber')">🟡 Warm Amber (Night)</button>
          <button class="android-chip" onclick="setPalette('emerald')">🟢 Phosphor Emerald</button>
          <button class="android-chip" onclick="setPalette('cyan')">🔵 Nordic Glacier Cyan</button>
        </div>
      </div>

      <!-- SYSTEM TELEMETRY -->
      <div class="side-box">
        <div class="side-box-title">⚡ Real-Time Hardware Telemetry</div>
        <div class="grid-stats">
          <div class="stat-tile">
            <div class="stat-label">Battery Estimation</div>
            <div class="stat-val" id="statBattery">4.2 Days</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Display Mode</div>
            <div class="stat-val" id="statDisplay">120Hz Full OLED</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Active Hotspot</div>
            <div class="stat-val" id="statHotspot">OFF</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Push Bridge (FCM)</div>
            <div class="stat-val" style="color:var(--android-green);">Connected (0% CPU)</div>
          </div>
        </div>
      </div>

      <!-- LINUX KERNEL LOG -->
      <div class="side-box">
        <div class="side-box-title">🖥️ Linux Kernel & Network Subsystem Log</div>
        <div class="kernel-terminal" id="kernelLogs"></div>
      </div>

      <!-- USER GUIDANCE -->
      <div class="side-box">
        <div class="side-box-title">💡 How Everyday Users Experience ZeroOS</div>
        <div style="font-size:0.78rem; line-height:1.6; color:#cbd5e1;">
          <p>• <b>Tap Any App:</b> Tap <i>WhatsApp</i> or <i>Instagram</i>. Notice how it opens instantly. When you click <b>Swipe Home to Air-Gap</b>, watch the terminal slam the door (0 B/s data, mic locked, 0% CPU).</p>
          <p style="margin-top:6px;">• <b>Disposable Apps:</b> Try typing <code>ephemeral instagram</code>. It runs in an isolated RAM overlay and permanently vaporizes all cookies upon exit.</p>
          <p style="margin-top:6px;">• <b>Nokia Mode:</b> Type <code>nokia mode</code>. Extends battery to 4–6 days with 1-bit monochrome and 60Hz throttling.</p>
          <p style="margin-top:6px;">• <b>Calm Digest:</b> Click the <i>Calm Digest</i> pill to view non-urgent notifications held quietly.</p>
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
      youtube: `<svg viewBox="0 0 48 48"><path fill="#FF0000" d="M43.2 13.8c-.5-1.9-2-3.4-3.9-3.9C35.9 9 24 9 24 9s-11.9 0-15.3.9c-1.9.5-3.4 2-3.9 3.9C4 17.2 4 24 4 24s0 6.8.8 10.2c.5 1.9 2 3.4 3.9 3.9 3.4.9 15.3.9 15.3.9s11.9 0 15.3-.9c1.9-.5 3.4-2 3.9-3.9.8-3.4.8-10.2.8-10.2s0-6.8-.8-10.2z"/><path fill="#FFF" d="M20 30l10.4-6L20 18z"/></svg>`,
      spotify: `<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="20" fill="#1ED760"/><path fill="#000" d="M33.6 30.6c-.4.6-1.1.8-1.7.4-4.7-2.9-10.6-3.5-17.5-1.9-.7.2-1.4-.3-1.6-1-.2-.7.3-1.4 1-1.6 7.6-1.7 14.1-1 19.4 2.2.6.4.8 1.2.4 1.9zm2.4-5.3c-.5.8-1.5 1-2.2.5-5.9-3.6-14.8-4.7-21.7-2.6-.9.3-1.8-.2-2.1-1.1-.3-.9.2-1.8 1.1-2.1 7.9-2.4 17.8-1.2 24.4 2.9.8.5 1 1.6.5 2.4zm.2-5.5C29.1 15.5 17.5 15.1 10.8 17.1c-1.1.3-2.2-.3-2.5-1.4-.3-1.1.3-2.2 1.4-2.5 7.8-2.4 20.6-1.9 28.5 2.8 1 .6 1.3 1.9.7 2.9-.6 1-1.9 1.3-2.7.9z"/></svg>`,
      monzo: `<svg viewBox="0 0 48 48"><path fill="#EE6554" d="M11 26l7-14h12l7 14-7 14H18z"/><circle cx="24" cy="26" r="5" fill="#FFF"/></svg>`,
      maps: `<svg viewBox="0 0 48 48"><path fill="#4285F4" d="M24 4C14.1 4 6 12.1 6 22c0 13.5 18 22 18 22s18-8.5 18-22c0-9.9-8.1-18-18-18z"/><circle cx="24" cy="20" r="7" fill="#EA4335"/><circle cx="24" cy="20" r="3.5" fill="#FFF"/></svg>`,
      settings: `<svg viewBox="0 0 48 48"><path fill="#9AA0A6" d="M38.9 26.2c.1-.7.1-1.4.1-2.2s0-1.5-.1-2.2l4.4-3.4c.4-.3.5-.9.2-1.4l-4.2-7.2c-.3-.5-.8-.7-1.3-.5l-5.1 2.1c-1.1-.8-2.2-1.5-3.5-2l-.8-5.4c-.1-.5-.6-.9-1.1-.9h-8.3c-.6 0-1 .4-1.1.9l-.8 5.4c-1.3.5-2.4 1.2-3.5 2l-5.1-2.1c-.5-.2-1.1 0-1.3.5l-4.2 7.2c-.3.5-.1 1.1.2 1.4l4.4 3.4c-.1.7-.1 1.4-.1 2.2s0 1.5.1 2.2l-4.4 3.4c-.4.3-.5.9-.2 1.4l4.2 7.2c.3.5.8.7 1.3.5l5.1-2.1c1.1.8 2.2 1.5 3.5 2l.8 5.4c.1.5.6.9 1.1.9h8.3c.6 0 1-.4 1.1-.9l.8-5.4c1.3-.5 2.4-1.2 3.5-2l5.1 2.1c.5.2 1.1 0 1.3-.5l4.2-7.2c.3-.5.1-1.1-.2-1.4l-4.4-3.4zM24 31c-3.9 0-7-3.1-7-7s3.1-7 7-7 7 3.1 7 7-3.1 7-7 7z"/></svg>`
    };

    let state = {};
    let pendingAction = null;

    async function loadState() {
      const res = await fetch('/api/state');
      state = await res.json();
      renderIcons();
      renderUI();
    }

    function renderIcons() {
      Object.keys(OFFICIAL_ICONS).forEach(key => {
        const el = document.getElementById(`icon-${key}`);
        if (el) el.innerHTML = OFFICIAL_ICONS[key];
        const dockEl = document.getElementById(`dock-${key}`);
        if (dockEl) dockEl.innerHTML = OFFICIAL_ICONS[key];
      });
    }

    function renderUI() {
      // 1. Status Bar & Battery
      document.getElementById('statusTorch').style.display = state.is_torch_on ? 'inline-block' : 'none';
      document.getElementById('statusHotspot').style.display = state.is_hotspot_on ? 'inline-flex' : 'none';
      document.getElementById('hotspotBanner').style.display = state.is_hotspot_on ? 'flex' : 'none';

      const oled = document.getElementById('oledScreen');
      if (state.is_nokia_mode) {
        oled.className = 'oled-screen nokia-active';
        document.getElementById('widgetNokiaBadge').style.display = 'inline-block';
        document.getElementById('widgetBatteryText').innerText = '🔋 5.8 Days (Nokia Deep Sleep)';
        document.getElementById('statDisplay').innerText = '60Hz E-Ink Profile';
        document.getElementById('statBattery').innerText = '5.8 Days';
      } else if (state.is_grayscale) {
        oled.className = 'oled-screen grayscale-active';
        document.getElementById('widgetNokiaBadge').style.display = 'none';
        document.getElementById('widgetBatteryText').innerText = `🔋 ${state.battery_days_remaining} Days Battery Remaining`;
        document.getElementById('statDisplay').innerText = '120Hz Monochrome';
        document.getElementById('statBattery').innerText = `${state.battery_days_remaining} Days`;
      } else {
        oled.className = `oled-screen palette-${state.palette}`;
        document.getElementById('widgetNokiaBadge').style.display = 'none';
        document.getElementById('widgetBatteryText').innerText = `🔋 ${state.battery_days_remaining} Days Battery Remaining`;
        document.getElementById('statDisplay').innerText = '120Hz Full OLED';
        document.getElementById('statBattery').innerText = `${state.battery_days_remaining} Days`;
      }

      document.getElementById('statHotspot').innerText = state.is_hotspot_on ? 'ON (1 client)' : 'OFF';

      // 2. Calm Digest Badge
      const digestCount = state.calm_digest_items ? state.calm_digest_items.length : 0;
      document.getElementById('digestCountBadge').innerText = `${digestCount} non-urgent held`;

      // 3. Impact Dashboard
      if (state.impact_stats) {
        document.getElementById('impactTrackers').innerText = state.impact_stats.trackers_blocked.toLocaleString();
        document.getElementById('impactBattery').innerText = `${state.impact_stats.battery_hours_saved}h`;
        document.getElementById('impactMic').innerText = `${state.impact_stats.mic_hours_locked}h`;
        document.getElementById('impactAirgapped').innerText = state.impact_stats.airgapped_apps;
      }

      // 4. Foreground App Overlay
      const appWin = document.getElementById('activeAppWindow');
      if (state.active_app) {
        appWin.style.display = 'flex';
        renderActiveAppContent(state.active_app, state.is_ephemeral);
      } else {
        appWin.style.display = 'none';
      }

      // 5. App Shield Badges
      if (state.app_shields) {
        Object.keys(state.app_shields).forEach(k => {
          const s = state.app_shields[k];
          const dot = document.getElementById(`dot-${k}`);
          if (dot) {
            dot.style.display = (s.data_cut || s.mic_muted || s.is_frozen) ? 'inline-block' : 'none';
          }
        });
      }

      // 6. Kernel terminal
      const logsBox = document.getElementById('kernelLogs');
      logsBox.innerHTML = state.kernel_logs.map(l => `<div>${l}</div>`).join('');
      logsBox.scrollTop = logsBox.scrollHeight;
    }

    function renderActiveAppContent(appKey, isEphemeral) {
      const headerIcon = document.getElementById('appHeaderIcon');
      headerIcon.innerHTML = OFFICIAL_ICONS[appKey] || '';
      
      const appName = appKey.charAt(0).toUpperCase() + appKey.slice(1);
      document.getElementById('appHeaderTitle').innerText = appName;

      const badge = document.getElementById('appHeaderBadge');
      if (isEphemeral) {
        badge.className = 'badge-ephemeral';
        badge.innerText = '🛡️ EPHEMERAL RAM (WIPED ON EXIT)';
      } else {
        badge.className = 'badge-normal-airgap';
        badge.innerText = 'AUTOMATIC AIR-GAP ACTIVE';
      }

      const body = document.getElementById('appWindowBody');
      if (appKey === 'whatsapp') {
        body.innerHTML = `
          <div style="font-size:0.75rem; color:#94a3b8; text-align:center; margin-bottom:12px;">🔒 End-to-end encrypted · Decoupled Push</div>
          <div class="chat-bubble left">Hey! Are you free for coffee this afternoon?</div>
          <div class="chat-bubble right">Yes! Testing out ZeroOS right now. Battery is incredible.</div>
          <div class="chat-bubble left">Did your phone cut background telemetry?</div>
          <div class="chat-bubble right">Completely. The second I swipe home, WhatsApp mic & data are severed.</div>
        `;
      } else if (appKey === 'instagram') {
        body.innerHTML = `
          <div style="background:#141b26; border-radius:14px; padding:12px; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
              <div style="width:24px; height:24px; border-radius:50%; background:#e1306c;"></div>
              <span style="font-size:0.8rem; font-weight:600; color:#fff;">natgeo</span>
            </div>
            <div style="height:150px; background:#1b2332; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#64748b; font-size:0.8rem;">
              [OLED Optimized Image Stream]
            </div>
            <div style="font-size:0.75rem; color:#cbd5e1; margin-top:8px;">Glacier national park at dawn. Zero battery wasted.</div>
          </div>
        `;
      } else {
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; flex:1; text-align:center; padding:20px;">
            <div style="width:50px; height:50px; margin-bottom:12px;">${OFFICIAL_ICONS[appKey] || ''}</div>
            <div style="font-size:1rem; font-weight:600; color:#fff; margin-bottom:6px;">${appName} Running Live</div>
            <div style="font-size:0.75rem; color:#94a3b8; max-width:240px; line-height:1.5;">
              Active foreground session. When finished, swipe home or click Close to trigger instant zero-leak lockdown.
            </div>
          </div>
        `;
      }
    }

    async function launchForegroundApp(appKey, isEphemeral = false) {
      const res = await fetch('/api/launch_app', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_key: appKey, is_ephemeral: isEphemeral })
      });
      const data = await res.json();
      state = data.state;
      renderUI();
      showToast(data.message);
    }

    async function closeActiveApp() {
      const res = await fetch('/api/close_app', { method: 'POST' });
      const data = await res.json();
      state = data.state;
      renderUI();
      showToast(data.message);
    }

    function openCalmDigestSheet() {
      const listEl = document.getElementById('digestItemsList');
      if (state.calm_digest_items && state.calm_digest_items.length > 0) {
        listEl.innerHTML = state.calm_digest_items.map(item => `
          <div class="digest-list-item">
            <div class="digest-item-top">
              <span class="digest-item-app">${item.app}</span>
              <span class="digest-item-time">${item.time}</span>
            </div>
            <div class="digest-item-body">${item.desc}</div>
          </div>
        `).join('');
      } else {
        listEl.innerHTML = `<div style="text-align:center; padding:16px; color:#64748b; font-size:0.8rem;">🎉 All calm! Zero pending notifications.</div>`;
      }
      document.getElementById('digestSheet').classList.add('active');
    }

    function dismissDigestSheet() {
      document.getElementById('digestSheet').classList.remove('active');
    }

    async function clearDigestSheet() {
      const res = await fetch('/api/clear_digest', { method: 'POST' });
      const data = await res.json();
      state = data.state;
      renderUI();
      dismissDigestSheet();
      showToast(data.message);
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
      showToast("⚡ Power Button Long-Press: Command Bar Armed");
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

@app.route("/api/launch_app", methods=["POST"])
def launch_app():
    data = request.json or {}
    app_key = data.get("app_key")
    is_ephemeral = data.get("is_ephemeral", False)

    STATE["active_app"] = app_key
    STATE["is_ephemeral"] = is_ephemeral

    app_name = app_key.capitalize() if app_key else "App"
    STATE["kernel_logs"].append(f"[AutoAirGap] '{app_name}' FOREGROUND: Restored network sockets & camera/mic registers")
    
    if is_ephemeral:
        STATE["kernel_logs"].append(f"[EphemeralSandbox] Mounted tmpfs RAM overlay on /data/data/{app_key}. Session is disposable.")
        msg = f"🛡️ Opened {app_name} in Disposable Ephemeral RAM Sandbox."
    else:
        msg = f"Opened {app_name}. Automatic Air-Gap will freeze background on exit."

    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/close_app", methods=["POST"])
def close_app():
    closed_app = STATE["active_app"] or "App"
    is_ephemeral = STATE["is_ephemeral"]

    # 1. Trigger Air-Gap lockdown
    STATE["active_app"] = None
    STATE["is_ephemeral"] = False

    app_name = closed_app.capitalize()
    STATE["kernel_logs"].append(f"[AutoAirGap] '{app_name}' BACKGROUND: Slamming steel door!")
    STATE["kernel_logs"].append(f"[iptables] iptables -I OUTPUT -m owner --uid-owner com.{closed_app} -j DROP (0 B/s)")
    STATE["kernel_logs"].append(f"[AppOps] cmd appops set com.{closed_app} RECORD_AUDIO deny (Hardware silence)")
    STATE["kernel_logs"].append(f"[cgroups] Scaled CPU quota to 0%. Frozen into Linux deep sleep.")

    # 2. If Ephemeral, wipe all data
    if is_ephemeral:
        STATE["kernel_logs"].append(f"[EphemeralSandbox] Vaporizing all temporary cookies, storage & tokens for com.{closed_app}!")
        msg = f"🔒 {app_name} closed: All session data & cookies vaporized permanently."
    else:
        msg = f"🔒 {app_name} closed: Background network severed & mic locked automatically."

    # 3. Update Impact Tracker
    STATE["impact_stats"]["trackers_blocked"] += 14
    STATE["impact_stats"]["airgapped_apps"] += 1

    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/clear_digest", methods=["POST"])
def clear_digest():
    count = len(STATE["calm_digest_items"])
    STATE["calm_digest_items"] = []
    STATE["kernel_logs"].append(f"[CalmDigest] Cleared {count} held notification items.")
    return jsonify({"success": True, "message": f"Archived {count} alerts from Calm Digest.", "state": STATE})

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

    # HARDWARE: FLASHLIGHT / TORCH
    if "flash" in lower or "torch" in lower:
        is_off = "off" in lower or "stop" in lower or "disable" in lower
        STATE["is_torch_on"] = not is_off
        msg = "🔦 Flashlight turned ON." if STATE["is_torch_on"] else "🔦 Flashlight turned OFF."
        STATE["kernel_logs"].append(f"[SYS_GPIO] cameraManager.setTorchMode(0, {STATE['is_torch_on']}) -> SUCCESS")
        return jsonify({"success": True, "message": msg, "state": STATE})

    # HARDWARE: WI-FI HOTSPOT
    if "hotspot" in lower or "tether" in lower:
        is_off = "off" in lower or "stop" in lower or "disable" in lower
        STATE["is_hotspot_on"] = not is_off
        if STATE["is_hotspot_on"]:
            STATE["kernel_logs"].append(f"[HOSTAPD] Broadcasting SSID='{STATE['hotspot_ssid']}', WPA3-SAE (5GHz)")
            STATE["kernel_logs"].append("[IPTABLES] iptables -t nat -A POSTROUTING -s 192.168.43.0/24 -o rmnet_data0 -j MASQUERADE")
            msg = f"(((•))) Hotspot ACTIVE: Broadcasting '{STATE['hotspot_ssid']}'. 1 device connected."
        else:
            STATE["kernel_logs"].append("[HOSTAPD] hostapd daemon stopped. AP interface wlan0 DOWN.")
            msg = "(((•))) Hotspot turned OFF."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # NOKIA 4-6 DAY BATTERY MODE
    if "nokia" in lower or "deep sleep" in lower:
        is_off = "off" in lower or "exit" in lower or "disable" in lower
        if is_off:
            STATE["is_nokia_mode"] = False
            STATE["battery_days_remaining"] = 4.2
            STATE["kernel_logs"].append("[CPUFREQ] Restored normal governor. 120Hz display online.")
            return jsonify({"success": True, "message": "Nokia Mode deactivated. Full color & 120Hz restored.", "state": STATE})
        else:
            return jsonify({
                "confirmation_required": True,
                "confirm_title": "Turn on Nokia Mode?",
                "confirm_desc": "Forces CPU into deep Linux C-states with 60Hz 1-bit monochrome display.",
                "confirm_bullets": [
                    "Extends battery longevity to 4–6 full days.",
                    "Disables 5G radios (drops to low-power VoLTE).",
                    "Incoming phone calls and SMS messages still ring 100% reliably."
                ],
                "action_name": "enable_nokia_mode",
                "state": STATE
            })

    # GRAYSCALE
    if "grayscale" in lower or "monochrome" in lower:
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
                    "Saves up to 18% OLED battery power."
                ],
                "action_name": "enable_grayscale",
                "state": STATE
            })

    # CALM DIGEST COMMAND
    if "calm" in lower or "digest" in lower:
        return jsonify({
            "success": True,
            "message": "🔕 Calm Digest active: Non-urgent alerts are bundled into scheduled quiet batches.",
            "state": STATE
        })

    # EPHEMERAL APP LAUNCH
    if "ephemeral" in lower or "disposable" in lower or "temp " in lower:
        target = "instagram"
        for k in ["whatsapp", "instagram", "tiktok", "youtube", "monzo", "chrome"]:
            if k in lower:
                target = k
                break
        return launch_app_internal(target, is_ephemeral=True)

    # CUT MIC FOR APPS
    has_mic_word = any(w in lower for w in ["mic", "microphone", "audio", "listen"])
    has_cut_word = any(w in lower for w in ["cut", "block", "kill", "stop", "disable", "mute"])
    if has_mic_word and has_cut_word:
        targets = [k for k in STATE["app_shields"].keys() if k in lower] or ["whatsapp"]
        for t in targets:
            app_obj = STATE["app_shields"][t]
            app_obj["mic_muted"] = True
            STATE["kernel_logs"].append(f"[AppOps] cmd appops set {app_obj['package']} RECORD_AUDIO deny -> REGISTER LOCKED")
            STATE["kernel_logs"].append(f"[AudioHAL] Fed digital silence (/dev/zero) to UID PCM audio stream.")
        names = [STATE["app_shields"][t]["name"] for t in targets]
        return jsonify({
            "success": True,
            "message": f"🎙️ Microphone hardware register LOCKED for: {', '.join(names)}. Audio feeds dead silence.",
            "state": STATE
        })

    # CUT DATA FOR APPS
    has_data_word = any(w in lower for w in ["data", "internet", "wifi", "cellular", "net"])
    if has_data_word and has_cut_word:
        targets = [k for k in STATE["app_shields"].keys() if k in lower] or ["instagram", "tiktok"]
        for t in targets:
            app_obj = STATE["app_shields"][t]
            app_obj["data_cut"] = True
            STATE["kernel_logs"].append(f"[iptables] iptables -I OUTPUT -m owner --uid-owner {app_obj['package']} -j DROP")
        names = [STATE["app_shields"][t]["name"] for t in targets]
        return jsonify({
            "success": True,
            "message": f"⚡ Data severed at kernel level for: {', '.join(names)}. Background draw = 0 B/s.",
            "state": STATE
        })

    # CLOSE / HOME COMMAND
    if lower in ["close", "exit", "home", "back"]:
        return close_app()

    # ABOUT PHONE
    if "about" in lower:
        return jsonify({
            "success": True,
            "message": "📱 ZeroPhone Pro · Android 14 AOSP · Linux 5.10 Kernel · Auto-AirGap Active · 6,000 mAh",
            "state": STATE
        })

    # FALLBACK APP LAUNCH
    for k in ["whatsapp", "instagram", "tiktok", "youtube", "monzo", "chrome", "camera", "phone", "messages", "spotify", "maps"]:
        if k in lower:
            return launch_app_internal(k, is_ephemeral=False)

    return jsonify({"success": True, "message": f"Command received: '{raw_cmd}'. Executing on device.", "state": STATE})

def launch_app_internal(app_key, is_ephemeral=False):
    STATE["active_app"] = app_key
    STATE["is_ephemeral"] = is_ephemeral
    app_name = app_key.capitalize()
    STATE["kernel_logs"].append(f"[AutoAirGap] '{app_name}' entering FOREGROUND: Restored network sockets & hardware")
    if is_ephemeral:
        STATE["kernel_logs"].append(f"[EphemeralSandbox] Mounted tmpfs RAM overlay on /data/data/{app_key}.")
        msg = f"🛡️ Opened {app_name} in Disposable Ephemeral RAM Sandbox."
    else:
        msg = f"Opened {app_name}. Automatic Air-Gap will freeze background on exit."
    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/confirm_action", methods=["POST"])
def confirm_action():
    action = (request.json or {}).get("action")
    if action == "enable_nokia_mode":
        STATE["is_nokia_mode"] = True
        STATE["battery_days_remaining"] = 5.8
        STATE["kernel_logs"].append("[CPUFREQ] Governor scaled to powersave. Deep Linux C-states forced.")
        return jsonify({"success": True, "message": "🔋 Nokia 5-Day Mode turned ON. Display clamped to 60Hz 1-bit monochrome.", "state": STATE})
    elif action == "enable_grayscale":
        STATE["is_grayscale"] = True
        STATE["kernel_logs"].append("[DALTONIZER] Settings.Secure.putInt('accessibility_display_daltonizer_enabled', 1)")
        return jsonify({"success": True, "message": "🌓 Grayscale Mode turned ON.", "state": STATE})
    return jsonify({"success": False, "message": "Unknown action", "state": STATE})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5077))
    print(f"ZeroOS Simple Android UI Simulator running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
