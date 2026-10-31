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
    "is_wifi_on": True,
    "wifi_ssid": "Home-5G",
    "is_bluetooth_on": True,
    "bluetooth_device": "Sony WH-1000XM5",
    "sound_mode": "sound", # "sound", "vibrate", "silent"
    "volume": 70,
    "is_grayscale": False,
    "is_micro_window": False,
    "is_dia_mode": False,
    "is_mic_killed": False,
    "auto_airgap_enabled": True,  # Automatic zero-leak background killer
    "active_app": None,           # Currently running foreground app (null = Home)
    "is_ephemeral": False,        # Whether active app is in disposable RAM sandbox
    "palette": "official",        # official, monochrome, amber, emerald, cyan
    "screen_refresh_hz": 120,
    "brightness": 85,
    "battery_percent": 88,
    "battery_days_remaining": 4.2,
    "calm_digest_enabled": True,
    "calm_digest_items": [
        {"id": 1, "app": "Instagram", "title": "Social Update", "desc": "alex_99 and 4 others liked your story", "time": "18m ago"},
        {"id": 2, "app": "TikTok", "title": "Recommendation", "desc": "Trending sound: 'Midnight Beats' in your area", "time": "45m ago"},
        {"id": 3, "app": "UberEats", "title": "Promotion", "desc": "30% off your next lunch order before 2 PM", "time": "2h ago"}
    ],
    "impact_stats": {
        "trackers_blocked": 1448,
        "battery_hours_saved": 3.8,
        "mic_hours_locked": 22.4,
        "airgapped_apps": 10
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
        "amazon_music": {
            "name": "Amazon Music",
            "package": "com.amazon.mp3",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 0
        },
        "waze": {
            "name": "Waze",
            "package": "com.waze",
            "data_cut": False,
            "mic_muted": False,
            "is_frozen": False,
            "trackers_blocked": 0
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
        "[1.020000] SystemUI online. One UI reachability + Pixel Material You layout loaded."
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ZeroOS - Pure Everyday Mobile OS (One UI + Pixel Hybrid)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --android-bg: #000000;
      --oneui-surface: #0a0a0a;
      --oneui-card: #121212;
      --oneui-tile: #171717;
      --tile-active: #ffffff;
      --tile-active-text: #000000;
      --pixel-primary: #ffffff;
      --pixel-accent: #e2e8f0;
      --text-main: #f8fafc;
      --text-sub: #8e8e93;
      --text-muted: #636366;
      --accent-green: #30d158;
      --accent-red: #ff453a;
      --accent-amber: #ffd60a;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.28);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #06090e;
      color: var(--text-main);
      font-family: 'Roboto', -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 16px;
    }

    .top-header {
      text-align: center;
      margin-bottom: 16px;
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
      color: var(--text-sub);
      margin-top: 4px;
    }

    .main-layout {
      display: flex;
      gap: 32px;
      align-items: flex-start;
      justify-content: center;
      max-width: 1260px;
      width: 100%;
      flex-wrap: wrap;
    }

    
    
    /* IN-CALL BUTTONS */
    .in-call-btn {
      background: #1c1c1e;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 10px 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #fff;
      cursor: pointer;
      transition: none !important;
      outline: none;
    }
    .in-call-icon { font-size: 1.25rem; margin-bottom: 2px; }
    .in-call-label { font-size: 0.68rem; color: #8e8e93; }

    /* DIALER TABS */
    .dialer-tab {
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 0.78rem;
      font-weight: 500;
      padding: 6px 12px;
      border-radius: 14px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .dialer-tab.active {
      background: #171717;
      color: #fff;
      font-weight: 700;
    }

    /* REALISTIC ANDROID HARDWARE CHASSIS */
    .phone-container {
      position: relative;
    }
    .phone-body {
      width: 384px;
      height: 796px;
      background: #000;
      border: 8px solid #232731;
      border-radius: 48px;
      box-shadow: 0 25px 60px rgba(0,0,0,0.85), 0 0 35px rgba(102, 157, 246, 0.12);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      user-select: none;
    }

    /* Hardware buttons */
    .hw-btn-power {
      position: absolute;
      right: -13px;
      top: 170px;
      width: 5px;
      height: 58px;
      background: #3a4252;
      border-radius: 0 4px 4px 0;
      cursor: pointer;
    }
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

    /* OLED DISPLAY CONTAINER */
    .oled-screen {
      flex: 1;
      background: #000000;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      transition: filter 0.3s ease;
    }
    .oled-screen.grayscale-active { filter: grayscale(100%); }
    .oled-screen.dia-active { filter: grayscale(100%) contrast(140%); }

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
      z-index: 110;
    }

    /* 1. ANDROID STATUS BAR (Click or Drag down opens Notification Center) */
    .android-status-bar {
      height: 38px;
      padding: 0 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.74rem;
      font-weight: 500;
      color: #cbd5e1;
      z-index: 95;
      background: transparent;
      cursor: pointer;
      transition: background 0.15s;
    }
    .android-status-bar:hover {
      background: rgba(255, 255, 255, 0.06);
    }
    .status-left { display: flex; align-items: center; gap: 6px; }
    .status-right { display: flex; align-items: center; gap: 7px; }

    /* ========================================================= */
    /* SAMSUNG ONE UI + PIXEL MATERIAL YOU NOTIFICATION CENTER   */
    /* (Slides down over Home with authentic Android physics)    */
    /* ========================================================= */
    .oneui-notification-center {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(10, 14, 20, 0.98);
      backdrop-filter: blur(28px);
      z-index: 100;
      display: flex;
      flex-direction: column;
      padding: 42px 16px 14px 16px;
      transform: translateY(-100%);
      transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 25px 60px rgba(0,0,0,0.95);
      overflow-y: auto;
      scrollbar-width: none;
    }
    .oneui-notification-center::-webkit-scrollbar { display: none; }
    .oneui-notification-center.open {
      transform: translateY(0);
    }

    /* ONE UI TOP VIEWING AREA (Comfortable Reachability Header) */
    .oneui-header-viewing {
      padding: 4px 6px 14px 6px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      margin-bottom: 14px;
    }
    .oneui-clock-huge {
      font-size: 2.1rem;
      font-weight: 300;
      color: #ffffff;
      letter-spacing: -0.5px;
      line-height: 1;
    }
    .oneui-date-line {
      font-size: 0.78rem;
      color: var(--text-sub);
      margin-top: 5px;
      font-weight: 400;
    }
    .oneui-header-icons {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .oneui-icon-btn {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: var(--oneui-card);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #cbd5e1;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      cursor: pointer;
    }
    .oneui-icon-btn:hover { background: #222c3e; color: #fff; }

    
    /* DUAL SLIDERS: BRIGHTNESS & VOLUME */
    .dual-sliders-card {
      background: var(--oneui-card);
      border-radius: 20px;
      padding: 12px 16px;
      margin-bottom: 12px;
      border: 1px solid var(--border-subtle);
    }
    .slider-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .slider-icon { font-size: 0.95rem; color: #94a3b8; width: 20px; text-align: center; }
    .slider-val { font-size: 0.72rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; width: 34px; text-align: right; }
    .material-slider {
      flex: 1;
      accent-color: var(--pixel-primary);
      cursor: pointer;
      height: 6px;
    }

    /* HERO TILES GRID (2x2) */
    .hero-tiles-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 12px;
    }

    /* COMMAND CENTER & QUICK CHIPS */
    .command-center-container {
      margin: 10px 0 16px 0;
      width: 100%;
    }
    .quick-chips-row {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 8px;
      scrollbar-width: none;
    }
    .quick-chips-row::-webkit-scrollbar { display: none; }
    .quick-chip {
      background: var(--oneui-card);
      border: 1px solid var(--border-subtle);
      color: #cbd5e1;
      border-radius: 20px;
      padding: 6px 12px;
      font-size: 0.72rem;
      white-space: nowrap;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s ease;
    }
    .quick-chip:hover {
      background: var(--oneui-tile);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.2);
    }
    .quick-chip:active {
      transform: scale(0.95);
    }
    .command-symbol {
      font-size: 1.1rem;
      color: var(--accent-green);
      font-weight: bold;
      padding-left: 12px;
    }
    .btn-execute-cmd {
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 1.1rem;
      padding: 0 14px;
      cursor: pointer;
      transition: color 0.15s;
    }
    .btn-execute-cmd:hover {
      color: #fff;
    }

    /* MATERIAL 3 BRIGHTNESS PILL SLIDER */
    .oneui-brightness-card {
      background: var(--oneui-card);
      border-radius: 20px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .slider-sun { font-size: 0.95rem; color: #94a3b8; }
    .material-slider {
      flex: 1;
      accent-color: var(--pixel-primary);
      cursor: pointer;
      height: 6px;
    }

    /* HERO QUICK TILES (Pixel-Style Top Large Dual Pills) */
    .hero-tiles-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 10px;
    }
    .hero-pill {
      background: var(--oneui-tile);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 20px;
      padding: 13px 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      transition: background 0.18s, border-color 0.18s, transform 0.08s;
    }
    .hero-pill:active { transform: scale(0.96); }
    .hero-pill.active {
      background: var(--pixel-primary);
      border-color: #669df6;
      color: #0c0f14;
    }
    .hero-pill.active .hero-title { color: #0c0f14; font-weight: 700; }
    .hero-pill.active .hero-sub { color: #1e293b; font-weight: 600; }
    .hero-pill.active .hero-icon-bubble { background: rgba(0,0,0,0.15); color: #000; }

    .hero-icon-bubble {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #2a374d;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.05rem;
      flex-shrink: 0;
    }
    .hero-info { display: flex; flex-direction: column; overflow: hidden; }
    .hero-title { font-size: 0.8rem; font-weight: 600; color: #f1f5f9; white-space: nowrap; }
    .hero-sub { font-size: 0.66rem; color: var(--text-sub); white-space: nowrap; margin-top: 1px; }

    /* SECONDARY QUICK SQUIRCLES GRID (One UI 6 Style 4x1) */
    .squircles-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-bottom: 18px;
    }
    .squircle-tile {
      background: var(--oneui-card);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 18px;
      padding: 10px 4px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      cursor: pointer;
      transition: background 0.18s, border-color 0.18s, transform 0.08s;
    }
    .squircle-tile:active { transform: scale(0.94); }
    .squircle-tile.active {
      background: var(--pixel-primary);
      border-color: #669df6;
      color: #0c0f14;
    }
    .squircle-tile.active .squircle-icon { background: rgba(0,0,0,0.15); color: #000; }
    .squircle-tile.active .squircle-lbl { color: #0c0f14; font-weight: 700; }

    .squircle-icon {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #232e41;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.95rem;
      margin-bottom: 5px;
    }
    .squircle-lbl {
      font-size: 0.65rem;
      font-weight: 500;
      color: #cbd5e1;
      white-space: nowrap;
    }

    /* ONE UI NOTIFICATIONS STREAM (Rounded Card Containers) */
    .oneui-notifications-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .notif-section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 4px;
      margin-bottom: 2px;
    }
    .notif-section-title {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .btn-clear-all {
      background: transparent;
      border: none;
      color: #a8c7fa;
      font-size: 0.72rem;
      cursor: pointer;
      font-weight: 600;
    }

    /* One UI Rounded Notification Cards */
    .oneui-notif-card {
      background: var(--oneui-card);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 18px;
      padding: 12px 14px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }
    .card-app-icon {
      width: 32px;
      height: 32px;
      border-radius: 10px;
      background: #232d3d;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.05rem;
      flex-shrink: 0;
    }
    .card-content-area { flex: 1; overflow: hidden; }
    .card-meta-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2px;
    }
    .card-app-title { font-size: 0.74rem; font-weight: 700; color: #a8c7fa; }
    .card-time-ago { font-size: 0.65rem; color: var(--text-muted); }
    .card-body-text { font-size: 0.78rem; color: #e2e8f0; line-height: 1.35; }
    .card-action-button {
      margin-top: 8px;
      background: var(--accent-red);
      color: #fff;
      border: none;
      padding: 5px 12px;
      border-radius: 10px;
      font-size: 0.7rem;
      font-weight: 600;
      cursor: pointer;
    }

    /* Bottom Swipe Up Handle Pill */
    .oneui-bottom-handle {
      height: 28px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      margin-top: auto;
    }
    .oneui-drag-pill {
      width: 68px;
      height: 4px;
      background: #475569;
      border-radius: 2px;
    }

    /* ============================================ */
    /* CLEAN DISTRACTION-FREE HOME SCREEN           */
    /* (NO HOTSPOT BUTTONS, NO CHAOS)              */
    /* ============================================ */
    .home-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 0 16px;
      overflow-y: auto;
      scrollbar-width: none;
    }
    .home-content::-webkit-scrollbar { display: none; }

    /* DIGITAL CLOCK & BATTERY (At a Glance) */
    .digital-clock-widget {
      text-align: center;
      margin: 16px 0 8px 0;
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
    .dia-mode-badge {
      display: inline-block;
      margin-left: 6px;
      padding: 2px 7px;
      border-radius: 10px;
      font-size: 0.65rem;
      font-weight: 700;
      background: #ffffff;
      color: #000000;
    }

    /* CALM DIGEST PILL (Clicking pulls down shade) */
    .calm-digest-pill {
      margin: 6px 0 12px 0;
      background: #111620;
      border: 1px solid #1c2433;
      border-radius: 16px;
      padding: 8px 14px;
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

    /* ZERO IMPACT SECURITY CARD */
    .impact-metrics-card {
      background: #0d121a;
      border: 1px solid #182232;
      border-radius: 16px;
      padding: 10px 12px;
      margin-bottom: 14px;
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
    .impact-val { font-size: 0.85rem; font-weight: 700; color: #fff; line-height: 1.1; }
    .impact-lbl { font-size: 0.58rem; color: #64748b; margin-top: 2px; }

    /* NATURAL LANGUAGE COMMAND & SEARCH BAR */
    .search-command-bar {
      background: #181d26;
      border-radius: 24px;
      padding: 11px 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
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
      color: var(--pixel-primary);
      cursor: pointer;
    }

    /* STANDARD APP ICONS GRID (Border-Free Official Brand SVGs) */
    .apps-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      row-gap: 18px;
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
    .app-icon-shape svg { width: 100%; height: 100%; }
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

    /* DOCK */
    .android-dock {
      display: flex;
      justify-content: space-around;
      align-items: center;
      padding: 10px 16px 6px 16px;
      background: transparent;
    }
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

    /* FOREGROUND ACTIVE APP WINDOW */
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
    .app-header-left { display: flex; align-items: center; gap: 10px; }
    .app-header-icon { width: 28px; height: 28px; }
    .app-header-title { font-size: 0.92rem; font-weight: 600; color: #fff; }
    .badge-ephemeral { font-size: 0.62rem; font-weight: 700; padding: 2px 7px; border-radius: 8px; background: #dc2626; color: #fff; }
    .badge-normal-airgap { font-size: 0.62rem; font-weight: 700; padding: 2px 7px; border-radius: 8px; background: #059669; color: #fff; }
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
    .app-window-body { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; }
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

    /* CHAT BUBBLES IN DEMO */
    .chat-bubble { padding: 10px 14px; border-radius: 14px; font-size: 0.8rem; max-width: 82%; margin-bottom: 12px; line-height: 1.4; }
    .chat-bubble.left { background: #1e2636; color: #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; }
    .chat-bubble.right { background: #10b981; color: #000; font-weight: 500; align-self: flex-end; border-bottom-right-radius: 4px; }

    /* SYSTEM SETTINGS & APPS UI */
    .settings-card {
      background: #141a24;
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 14px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      transition: background 0.15s, transform 0.1s;
    }
    .settings-card:hover {
      background: #1c2433;
      transform: translateY(-1px);
    }
    .settings-icon {
      width: 34px;
      height: 34px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.05rem;
      flex-shrink: 0;
    }
    .settings-content {
      display: flex;
      flex-direction: column;
      gap: 2px;
      flex: 1;
    }
    .settings-title {
      font-size: 0.82rem;
      font-weight: 600;
      color: #fff;
    }
    .settings-sub {
      font-size: 0.68rem;
      color: #94a3b8;
      line-height: 1.3;
    }
    .dialpad-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      width: 210px;
      margin: 0 auto;
    }
    .dial-key {
      background: #171717;
      border-radius: 50%;
      width: 58px;
      height: 58px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 500;
      color: #fff;
      cursor: pointer;
      border: 1px solid rgba(255, 255, 255, 0.08);
      margin: 0 auto;
      transition: none !important;
      animation: none !important;
      outline: none;
      user-select: none;
    }
    .dial-key:hover, .dial-key:active, .dial-key:focus {
      background: #171717 !important;
      transform: none !important;
      filter: none !important;
      outline: none !important;
    }
    .call-btn-green {
      background: #10b981;
      color: #000;
      border: none;
      padding: 10px 24px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
    }
    .call-btn-del {
      background: #232c3d;
      color: #cbd5e1;
      border: none;
      padding: 10px 16px;
      border-radius: 20px;
      font-size: 0.85rem;
      cursor: pointer;
    }
    .camera-lens-view {
      width: 100%;
      flex: 1;
      background: #090d14;
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      margin: 8px 0;
    }
    .camera-shutter-btn {
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: #fff;
      border: 4px solid #141923;
      box-shadow: 0 0 0 2px #fff;
      cursor: pointer;
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
    <h1>📱 ZeroOS · Flagship Android Architecture</h1>
    <p>Samsung One UI Reachability · Google Pixel Material You Quick Tiles · Zero Bloatware</p>
  </div>

  <div class="main-layout">

    <!-- REALISTIC PHONE HARDWARE -->
    <div class="phone-container">
      <div class="hw-btn-power" onclick="triggerPowerButton()" title="Power Button"></div>
      <div class="hw-btn-vol-up" onclick="showToast('Volume Up')"></div>
      <div class="hw-btn-vol-down" onclick="showToast('Volume Down')"></div>

      <div class="phone-body">
        
        <div class="camera-punch-hole"></div>

        <div class="oled-screen" id="oledScreen">

          <!-- ANDROID STATUS BAR (Click or Swipe Down opens standard Notification Center) -->
          <div class="android-status-bar" onclick="toggleNotificationShade()" title="Click to toggle Notification Center">
            <div class="status-left">
              <span id="statusClock">11:28</span>
              <span id="statusTorch" style="display:none;">🔦</span>
              <span id="statusHotspot" style="display:none; color:#34d399; font-weight:bold;">(((•)))</span>
            </div>
            <div class="status-right">
              <span id="statusShield" title="Auto Air-Gap Active">🛡️</span>
              <span id="status5G">5G</span>
              <span id="statusBattery">🔋 88%</span>
            </div>
          </div>

          <!-- ======================================================== -->
          <!-- ONE UI + PIXEL PULL-DOWN NOTIFICATION CENTER             -->
          <!-- ======================================================== -->
          <div id="notificationShade" class="oneui-notification-center">
            
            <!-- One UI Reachability Viewing Header -->
            <div class="oneui-header-viewing">
              <div>
                <div class="oneui-clock-huge" id="shadeClock">11:28</div>
                <div class="oneui-date-line">Wednesday, October 29 · 🔋 88%</div>
              </div>
              <div class="oneui-header-icons">
                <button class="oneui-icon-btn" onclick="quickRun('reboot')" title="Power Menu">⏻</button>
                <button class="oneui-icon-btn" onclick="launchSettingsFromShade()" title="Settings">⚙️</button>
              </div>
            </div>

            <!-- Dual Sliders: Brightness & Volume -->
            <div class="dual-sliders-card">
              <div class="slider-row">
                <span class="slider-icon">☀️</span>
                <input type="range" id="sliderBrightness" class="material-slider" min="10" max="100" value="85" oninput="setBrightness(this.value)" />
                <span class="slider-val" id="valBrightness">85%</span>
              </div>
              <div class="slider-row" style="margin-top: 8px;">
                <span class="slider-icon">🔊</span>
                <input type="range" id="sliderVolume" class="material-slider" min="0" max="100" value="70" oninput="setVolume(this.value)" />
                <span class="slider-val" id="valVolume">70%</span>
              </div>
            </div>

            <!-- Top Everyday Hero Quick Tiles (4 Capsules) -->
            <div class="hero-tiles-grid">
              
              <!-- Wi-Fi Tile -->
              <div class="hero-pill active" id="tileWifi" onclick="toggleFeature('wifi')">
                <div class="hero-icon-bubble">📶</div>
                <div class="hero-info">
                  <div class="hero-title">Wi-Fi</div>
                  <div class="hero-sub" id="subWifi">Home-5G</div>
                </div>
              </div>

              <!-- Bluetooth Tile -->
              <div class="hero-pill active" id="tileBt" onclick="toggleFeature('bluetooth')">
                <div class="hero-icon-bubble">ᛒ</div>
                <div class="hero-info">
                  <div class="hero-title">Bluetooth</div>
                  <div class="hero-sub" id="subBt">WH-1000XM5</div>
                </div>
              </div>

              <!-- Sound Mode Tile -->
              <div class="hero-pill active" id="tileSound" onclick="toggleFeature('sound')">
                <div class="hero-icon-bubble" id="iconSound">🔔</div>
                <div class="hero-info">
                  <div class="hero-title">Sound</div>
                  <div class="hero-sub" id="subSound">Ring</div>
                </div>
              </div>

              <!-- Flashlight / Torch Tile -->
              <div class="hero-pill" id="tileTorch" onclick="toggleFeature('torch')">
                <div class="hero-icon-bubble">🔦</div>
                <div class="hero-info">
                  <div class="hero-title">Torch</div>
                  <div class="hero-sub" id="subTorch">Off</div>
                </div>
              </div>

            </div>

            <!-- Secondary System & Privacy Squircles (4 Tiles) -->
            <div class="squircles-grid">
              
              <div class="squircle-tile" id="tileHotspot" onclick="toggleFeature('hotspot')">
                <div class="squircle-icon">(((•)))</div>
                <div class="squircle-lbl">Hotspot</div>
              </div>

              <div class="squircle-tile" id="tileGrayscale" onclick="toggleFeature('grayscale')">
                <div class="squircle-icon">🌓</div>
                <div class="squircle-lbl">0W Mono</div>
              </div>

              <div class="squircle-tile active" id="tileAirgap" onclick="toggleFeature('airgap')">
                <div class="squircle-icon">🛡️</div>
                <div class="squircle-lbl">Air-Gap</div>
              </div>

              <div class="squircle-tile" id="tileDia" onclick="toggleFeature('dia')">
                <div class="squircle-icon">🔋</div>
                <div class="squircle-lbl">DIA Mode</div>
              </div>

            </div>

            <!-- One UI Notification Stream with Grouped Cards -->
            <div class="oneui-notifications-container">
              
              <div class="notif-section-header">
                <span class="notif-section-title">Notifications</span>
                <button class="btn-clear-all" onclick="clearDigestNotifications()">Clear all</button>
              </div>

              <!-- Hotspot Active Card (Only appears when Hotspot is on!) -->
              <div id="shadeHotspotCard" class="oneui-notif-card" style="display:none;">
                <div class="card-app-icon" style="color:#34d399;">(((•)))</div>
                <div class="card-content-area">
                  <div class="card-meta-row">
                    <span class="card-app-title">Tethering</span>
                    <span class="card-time-ago">Active now</span>
                  </div>
                  <div class="card-body-text" id="shadeHotspotSub">Broadcasting ZeroPhone-5G · 1 client connected</div>
                  <button class="card-action-button" onclick="toggleFeature('hotspot')">Turn Off</button>
                </div>
              </div>

              <!-- Direct 1-on-1 Message (Urgent priority lane) -->
              <div class="oneui-notif-card">
                <div class="card-app-icon" style="color:#25d366;">💬</div>
                <div class="card-content-area">
                  <div class="card-meta-row">
                    <span class="card-app-title">WhatsApp</span>
                    <span class="card-time-ago">4m ago</span>
                  </div>
                  <div class="card-body-text"><b>Mom:</b> Call me when you get home this evening!</div>
                </div>
              </div>

              <!-- Calm Digest Bundled Alerts -->
              <div class="oneui-notif-card">
                <div class="card-app-icon" style="color:#60a5fa;">🔕</div>
                <div class="card-content-area">
                  <div class="card-meta-row">
                    <span class="card-app-title">Calm Digest</span>
                    <span class="card-time-ago" id="shadeDigestTime">Held quietly</span>
                  </div>
                  <div class="card-body-text" id="shadeDigestSub">3 promotional & social alerts held quietly to save battery.</div>
                </div>
              </div>

              <!-- Zero-Leak Security Status -->
              <div class="oneui-notif-card">
                <div class="card-app-icon" style="color:#34d399;">🛡️</div>
                <div class="card-content-area">
                  <div class="card-meta-row">
                    <span class="card-app-title">ZeroOS Kernel Shield</span>
                    <span class="card-time-ago">Active</span>
                  </div>
                  <div class="card-body-text">10 apps air-gapped in background · 0 B/s data leakage.</div>
                </div>
              </div>

            </div>

            <!-- Bottom Swipe-Up Handle Pill -->
            <div class="oneui-bottom-handle" onclick="closeNotificationShade()" title="Click to close shade">
              <div class="oneui-drag-pill"></div>
            </div>

          </div>

          <!-- ============================================ -->
          <!-- CLEAN DISTRACTION-FREE HOME SCREEN           -->
          <!-- (NO HOTSPOT BUTTONS, NO CHAOS)              -->
          <!-- ============================================ -->
          <div class="home-content" id="homeContent">

            <!-- Digital Clock & Battery Status -->
            <div class="digital-clock-widget">
              <div class="clock-digits" id="widgetClock">11:28</div>
              <div class="battery-pill-glance">
                <span id="widgetBatteryText">🔋 4.2 Days Battery Remaining</span>
                <span id="widgetDiaBadge" class="dia-mode-badge" style="display:none;">DIA MODE</span>
              </div>
            </div>

            <!-- Calm Digest Glance Pill (Click opens pull-down shade) -->
            <div class="calm-digest-pill" onclick="openNotificationShade()">
              <div class="digest-pill-text">
                <span>🔕 Calm Digest</span>
                <span class="digest-count-badge" id="digestCountBadge">3 alerts held</span>
              </div>
              <span style="font-size:0.75rem; color:#64748b;">Pull down shade ›</span>
            </div>

            <!-- Floating Ergonomic ZeroOS Command Center -->
            <div class="command-center-container">
              <div class="quick-chips-row">
                <button class="quick-chip" onclick="quickRun('toggle wifi')">📶 Wi-Fi</button>
                <button class="quick-chip" onclick="quickRun('toggle bluetooth')">ᛒ Bluetooth</button>
                <button class="quick-chip" onclick="quickRun('cycle sound')">🔔 Sound</button>
                <button class="quick-chip" onclick="quickRun('torch')">🔦 Torch</button>
                <button class="quick-chip" onclick="quickRun('mute mic for social media')">🎙️ Mute Mic</button>
                <button class="quick-chip" onclick="quickRun('battery report')">🔋 Battery</button>
              </div>

              <div class="search-command-bar">
                <span class="command-symbol">⌘</span>
                <input type="text" id="androidSearchInput" class="search-input" placeholder="Type setting, command or app ('wifi off', 'brightness 60', 'waze')..." onkeydown="if(event.key==='Enter') executeSearchCommand()" />
                <button class="btn-execute-cmd" onclick="executeSearchCommand()" title="Execute Command">↵</button>
              </div>
            </div>

            <!-- Standard Clean App Grid (Official Vector Logos) -->
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

              <!-- ZeroChat: Native Peer-to-Peer Encrypted Tor Messenger -->
              <div class="app-icon-item" onclick="launchForegroundApp('zerochat')">
                <div class="app-icon-shape" id="icon-zerochat" style="background:#005c4b; border:1px solid #00a884;">
                  <span style="font-size:1.4rem;">💬</span>
                  <span class="shield-badge-dot" style="display:block; background:#00a884; box-shadow:0 0 6px #00a884;">🧅</span>
                </div>
                <div class="app-label" style="color:#00a884; font-weight:600;">ZeroChat</div>
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
                <div class="app-label" style="color:#00a884; font-weight:600;">ZeroMaps</div>
              </div>

              <div class="app-icon-item" onclick="launchForegroundApp('settings')">
                <div class="app-icon-shape" id="icon-settings"></div>
                <div class="app-label">Settings</div>
              </div>

            </div>

            <!-- Standard Android Dock -->
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

            <!-- Gesture Navigation Bar -->
            <div class="gesture-bar-container">
              <div class="gesture-bar"></div>
            </div>

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
              <button class="btn-close-app" onclick="closeActiveApp()">Close & Exit</button>
            </div>
            
            <div class="app-window-body" id="appWindowBody"></div>

            <div class="app-window-footer">
              <button class="swipe-home-btn" onclick="closeActiveApp()">
                <span>🔒 Swipe Home to Exit & Sever Network</span>
              </button>
              <div class="gesture-bar-container" onclick="closeActiveApp()">
                <div class="gesture-bar"></div>
              </div>
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
          <button style="background:#161b24; color:#fff; border:1px solid #222b3b; padding:6px 12px; border-radius:12px; font-size:0.75rem; cursor:pointer;" onclick="setPalette('official')">🌈 Official Colors</button>
          <button style="background:#161b24; color:#fff; border:1px solid #222b3b; padding:6px 12px; border-radius:12px; font-size:0.75rem; cursor:pointer;" onclick="setPalette('monochrome')">⚪ Zen White</button>
          <button style="background:#161b24; color:#fff; border:1px solid #222b3b; padding:6px 12px; border-radius:12px; font-size:0.75rem; cursor:pointer;" onclick="setPalette('amber')">🟡 Warm Amber</button>
          <button style="background:#161b24; color:#fff; border:1px solid #222b3b; padding:6px 12px; border-radius:12px; font-size:0.75rem; cursor:pointer;" onclick="setPalette('emerald')">🟢 Phosphor Emerald</button>
          <button style="background:#161b24; color:#fff; border:1px solid #222b3b; padding:6px 12px; border-radius:12px; font-size:0.75rem; cursor:pointer;" onclick="setPalette('cyan')">🔵 Glacier Cyan</button>
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
            <div class="stat-label">Kernel Air-Gap</div>
            <div class="stat-val" style="color:var(--accent-green);">Active (0 B/s leak)</div>
          </div>
          <div class="stat-tile">
            <div class="stat-label">Push Bridge (FCM)</div>
            <div class="stat-val" style="color:var(--accent-green);">Connected (0% CPU)</div>
          </div>
        </div>
      </div>

      <!-- STANDBY BATTERY COMPARISON AUDIT -->
      <div class="side-box">
        <div class="side-box-title">🔋 Standby Battery Drain Audit (Stock Android vs ZeroOS)</div>
        <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">
          Empirical hardware power draw (measured on a standard 5,000 mAh battery cell):
        </div>
        <div style="display:flex; flex-direction:column; gap:8px;">
          <div style="background:#131822; padding:10px 12px; border-radius:10px; border-left:3px solid #ef4444;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
              <span style="font-size:0.8rem; font-weight:600; color:#f87171;">Stock Normal Android</span>
              <span style="font-size:0.8rem; font-weight:700; color:#f87171;">~2.1% / hour</span>
            </div>
            <div style="font-size:0.7rem; color:#94a3b8; line-height:1.4;">
              • Current Draw: <b>95 mA - 120 mA</b> avg<br>
              • Background Wakelocks: <b>~640 per 8h night</b> (Meta, TikTok, Google Analytics)<br>
              • Standby Duration: <b>~42 hours max</b> (1.75 Days)
            </div>
          </div>

          <div style="background:#131822; padding:10px 12px; border-radius:10px; border-left:3px solid #34d399;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
              <span style="font-size:0.8rem; font-weight:600; color:#34d399;">ZeroOS Auto-AirGap Standby</span>
              <span style="font-size:0.8rem; font-weight:700; color:#34d399;">~0.22% / hour</span>
            </div>
            <div style="font-size:0.7rem; color:#cbd5e1; line-height:1.4;">
              • Current Draw: <b>11 mA</b> avg (<b>88% power reduction!</b>)<br>
              • Background Wakelocks: <b>0 wakelocks</b> (cgroups 0% freeze)<br>
              • Network Sockets: <b>0 B/s leak</b> (iptables netfilter steel door)<br>
              • Standby Duration: <b>~4.5 Days</b> (108 hours)
            </div>
          </div>

          <div style="background:#131822; padding:10px 12px; border-radius:10px; border-left:3px solid #60a5fa;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
              <span style="font-size:0.8rem; font-weight:600; color:#60a5fa;">ZeroOS DIA Mode (Deep Sleep)</span>
              <span style="font-size:0.8rem; font-weight:700; color:#60a5fa;">~0.09% / hour</span>
            </div>
            <div style="font-size:0.7rem; color:#cbd5e1; line-height:1.4;">
              • Current Draw: <b>4.8 mA</b> avg (<b>95% power reduction!</b>)<br>
              • CPU: Linux low-frequency powersave C-states<br>
              • Standby Duration: <b>~6.5 - 8.0 Days</b> (160+ hours)
            </div>
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
        <div class="side-box-title">💡 One UI Reachability + Pixel Material Layout</div>
        <div style="font-size:0.78rem; line-height:1.6; color:#cbd5e1;">
          <p>• <b>One UI Pull-Down:</b> Click the <b>Top Status Bar</b>. Notice how the top 25% provides comfortable viewing, while all interactive quick tiles and notifications sit in the thumb zone.</p>
          <p style="margin-top:6px;">• <b>Pixel Dual Pills:</b> Hotspot and DIA Mode are large hero pills at top of the grid. Torch, Grayscale, Digest, and Air-Gap are One UI squircles.</p>
          <p style="margin-top:6px;">• <b>Bidirectional Toggles:</b> Every button turns ON on first click and OFF on second click.</p>
        </div>
      </div>

    </div>

  </div>

  <script>
    // OFFICIAL BRAND SVG ASSETS
    const OFFICIAL_ICONS = {
      zerochat: `<svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="20" fill="#00A884"/><path fill="#FFF" d="M24 10c-7.7 0-14 5.8-14 13 0 2.6.9 5.1 2.5 7.1L11 36l6.3-1.6c2.1 1 4.3 1.6 6.7 1.6 7.7 0 14-5.8 14-13s-6.3-13-14-13zm0 22c-2 0-3.9-.5-5.6-1.5l-.4-.2-3.7 1 1-3.6-.3-.4c-1.3-1.8-2-3.9-2-6.3 0-5.5 4.9-10 11-10s11 4.5 11 10-4.9 10-11 10z"/><circle cx="19" cy="22" r="2" fill="#FFF"/><circle cx="29" cy="22" r="2" fill="#FFF"/></svg>`,

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

    async function loadState() {
      if (window.location.search.includes('shade')) {
        setTimeout(openNotificationShade, 250);
      }
      if (window.location.search.includes('call')) {
        setTimeout(() => {
          launchForegroundApp('phone');
          setTimeout(() => startCall('Mom', '+1 (555) 234-5678'), 200);
        }, 200);
      }
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

    function openNotificationShade() {
      document.getElementById('notificationShade').classList.add('open');
    }

    function closeNotificationShade() {
      document.getElementById('notificationShade').classList.remove('open');
    }

    function toggleNotificationShade() {
      const shade = document.getElementById('notificationShade');
      if (shade.classList.contains('open')) {
        closeNotificationShade();
      } else {
        openNotificationShade();
      }
    }

    function launchSettingsFromShade() {
      closeNotificationShade();
      launchForegroundApp('settings');
    }

    let currentDial = "";
    let isCallActive = false;
    let isCallRecording = false;
    let callContactName = "Mom";
    let callContactNumber = "+1 (555) 234-5678";
    let callSeconds = 0;
    let callInterval = null;

    function startCall(name, number) {
      const cleanNum = (number || name || "").replace(/[^0-9]/g, "");
      if (['911', '112', '999', '100', '108'].includes(cleanNum)) {
        showToast('🚨 EMERGENCY CALL (' + cleanNum + '): Sensor killswitches bypassed · High-accuracy GNSS & AML active.');
      }
      isCallActive = true;
      isCallRecording = false;
      callContactName = name || (currentDial || "Mom");
      callContactNumber = number || (currentDial || "+1 (555) 234-5678");
      callSeconds = 0;
      if (callInterval) clearInterval(callInterval);
      callInterval = setInterval(() => {
        callSeconds++;
        const timerEl = document.getElementById('callTimerDisplay');
        if (timerEl) {
          const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
          const secs = String(callSeconds % 60).padStart(2, '0');
          timerEl.innerText = `${mins}:${secs}`;
        }
      }, 1000);
      renderActiveAppContent('phone', false);
    }

    function toggleCallRecording() {
      isCallRecording = !isCallRecording;
      const btn = document.getElementById('btnCallRecord');
      if (isCallRecording) {
        if (btn) {
          btn.style.background = '#ff453a';
          btn.style.color = '#fff';
          btn.innerHTML = '🔴 Recording...';
        }
        showToast('⏺ Local Call Recording STARTED (Directly to device · No cloud / No announcements)');
      } else {
        if (btn) {
          btn.style.background = '#27272a';
          btn.style.color = '#fff';
          btn.innerHTML = '⏺ Record';
        }
        showToast('✅ Call Recording SAVED to /storage/Recordings/' + callContactName.replace(/\s+/g, '_') + '.m4a');
      }
    }

    function endCall() {
      isCallActive = false;
      isCallRecording = false;
      if (callInterval) clearInterval(callInterval);
      currentDial = "";
      renderActiveAppContent('phone', false);
      showToast('🔒 Call ENDED. Microphone hardware register LOCKED instantly.');
    }

    function copyAndAutoDeleteOTP(code) {
      navigator.clipboard?.writeText(code);
      showToast('📋 Copied OTP ' + code + '! Message will self-destruct in 15 minutes.');
      const card = document.getElementById('otpCard');
      if (card) {
        card.style.opacity = '0.4';
        card.innerHTML = `<div style="font-size:0.75rem; color:#30d158; text-align:center; padding:6px;">✓ Copied! Auto-delete timer running (14m 58s remaining)...</div>`;
      }
    }

    
    function switchDialerTab(tab) {
      document.getElementById('dialerViewRecents').style.display = tab === 'recents' ? 'flex' : 'none';
      document.getElementById('dialerViewContacts').style.display = tab === 'contacts' ? 'flex' : 'none';
      document.getElementById('dialerViewKeypad').style.display = tab === 'keypad' ? 'flex' : 'none';

      document.getElementById('dialerTabRecents').className = tab === 'recents' ? 'dialer-tab active' : 'dialer-tab';
      document.getElementById('dialerTabContacts').className = tab === 'contacts' ? 'dialer-tab active' : 'dialer-tab';
      document.getElementById('dialerTabKeypad').className = tab === 'keypad' ? 'dialer-tab active' : 'dialer-tab';
    }

    function appendDial(digit) {
      currentDial += digit;
      const el = document.getElementById('dialDisplay');
      if (el) el.innerText = currentDial;
    }
    function clearDial() {
      currentDial = currentDial.slice(0, -1);
      const el = document.getElementById('dialDisplay');
      if (el) el.innerText = currentDial || "Enter Number";
    }

    function renderUI() {
      // 1. Status Bar
      document.getElementById('statusTorch').style.display = state.is_torch_on ? 'inline-block' : 'none';
      document.getElementById('statusHotspot').style.display = state.is_hotspot_on ? 'inline-block' : 'none';

      const oled = document.getElementById('oledScreen');
      if (state.is_nokia_mode) {
        oled.className = 'oled-screen dia-active';
        document.getElementById('widgetDiaBadge').style.display = 'inline-block';
        document.getElementById('widgetBatteryText').innerText = '🔋 5.8 Days (Nokia Deep Sleep)';
        document.getElementById('statDisplay').innerText = '60Hz E-Ink Profile';
        document.getElementById('statBattery').innerText = '5.8 Days';
      } else if (state.is_grayscale) {
        oled.className = 'oled-screen grayscale-active';
        document.getElementById('widgetDiaBadge').style.display = 'none';
        document.getElementById('widgetBatteryText').innerText = `🔋 ${state.battery_days_remaining} Days Battery Remaining`;
        document.getElementById('statDisplay').innerText = '120Hz Monochrome';
        document.getElementById('statBattery').innerText = `${state.battery_days_remaining} Days`;
      } else {
        oled.className = `oled-screen palette-${state.palette}`;
        document.getElementById('widgetDiaBadge').style.display = 'none';
        document.getElementById('widgetBatteryText').innerText = `🔋 ${state.battery_days_remaining} Days Battery Remaining`;
        document.getElementById('statDisplay').innerText = '120Hz Full OLED';
        document.getElementById('statBattery').innerText = `${state.battery_days_remaining} Days`;
      }

      // 2. Everyday Hero Quick Pills
      updateHeroPill('tileWifi', 'subWifi', state.is_wifi_on, state.wifi_ssid || 'Home-5G', 'Off');
      updateHeroPill('tileBt', 'subBt', state.is_bluetooth_on, state.bluetooth_device || 'Connected', 'Off');
      
      const soundMode = state.sound_mode || 'sound';
      const soundIcon = soundMode === 'sound' ? '🔔' : (soundMode === 'vibrate' ? '📳' : '🔕');
      const soundSub = soundMode.charAt(0).toUpperCase() + soundMode.slice(1);
      const soundPill = document.getElementById('tileSound');
      if (soundPill) {
        if (soundMode !== 'silent') soundPill.classList.add('active');
        else soundPill.classList.remove('active');
        document.getElementById('iconSound').innerText = soundIcon;
        document.getElementById('subSound').innerText = soundSub;
      }

      updateHeroPill('tileTorch', 'subTorch', state.is_torch_on, 'On', 'Off');

      // 3. System & Privacy Squircles
      updateSquircle('tileHotspot', state.is_hotspot_on);
      updateSquircle('tileGrayscale', state.is_grayscale);
      updateSquircle('tileAirgap', state.auto_airgap_enabled);
      updateSquircle('tileDia', state.is_nokia_mode);

      // 4. Dual Sliders: Brightness & Volume
      if (state.brightness !== undefined) {
        const bSlider = document.getElementById('sliderBrightness');
        const bVal = document.getElementById('valBrightness');
        if (bSlider) bSlider.value = state.brightness;
        if (bVal) bVal.innerText = `${state.brightness}%`;
      }
      if (state.volume !== undefined) {
        const vSlider = document.getElementById('sliderVolume');
        const vVal = document.getElementById('valVolume');
        if (vSlider) vSlider.value = state.volume;
        if (vVal) vVal.innerText = `${state.volume}%`;
      }

      // 5. Hotspot notification card inside shade
      const hotspotCard = document.getElementById('shadeHotspotCard');
      if (hotspotCard) hotspotCard.style.display = state.is_hotspot_on ? 'flex' : 'none';

      // 6. Calm Digest Count
      const digestCount = state.calm_digest_items ? state.calm_digest_items.length : 0;
      const countBadge = document.getElementById('digestCountBadge');
      if (countBadge) countBadge.innerText = `${digestCount} held quietly`;
      const shadeSub = document.getElementById('shadeDigestSub');
      if (shadeSub) shadeSub.innerText = `${digestCount} non-urgent alerts held quietly to save battery.`;

      // 7. Foreground App Overlay
      const appWin = document.getElementById('activeAppWindow');
      if (state.active_app) {
        appWin.style.display = 'flex';
        renderActiveAppContent(state.active_app, state.is_ephemeral);
      } else {
        appWin.style.display = 'none';
      }

      // 8. App Shield Badges
      if (state.app_shields) {
        Object.keys(state.app_shields).forEach(k => {
          const s = state.app_shields[k];
          const dot = document.getElementById(`dot-${k}`);
          if (dot) {
            dot.style.display = (s.data_cut || s.mic_muted || s.is_frozen) ? 'inline-block' : 'none';
          }
        });
      }

      // 9. Kernel Terminal
      const logsBox = document.getElementById('kernelLogs');
      logsBox.innerHTML = state.kernel_logs.map(l => `<div>${l}</div>`).join('');
      logsBox.scrollTop = logsBox.scrollHeight;
    }

    function updateHeroPill(tileId, subId, isActive, activeText, inactiveText) {
      const tile = document.getElementById(tileId);
      const sub = document.getElementById(subId);
      if (!tile || !sub) return;
      if (isActive) {
        tile.classList.add('active');
        sub.innerText = activeText;
      } else {
        tile.classList.remove('active');
        sub.innerText = inactiveText;
      }
    }

    function updateSquircle(tileId, isActive) {
      const tile = document.getElementById(tileId);
      if (!tile) return;
      if (isActive) {
        tile.classList.add('active');
      } else {
        tile.classList.remove('active');
      }
    }

    
    async function setBrightness(val) {
      document.getElementById('valBrightness').innerText = `${val}%`;
      await fetch('/api/set_brightness', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brightness: parseInt(val) })
      });
    }

    async function setVolume(val) {
      document.getElementById('valVolume').innerText = `${val}%`;
      await fetch('/api/set_volume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ volume: parseInt(val) })
      });
    }

    async function toggleFeature(featureName) {
      const res = await fetch('/api/toggle_feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature: featureName })
      });
      const data = await res.json();
      state = data.state;
      renderUI();
      showToast(data.message);
    }

    function renderActiveAppContent(appKey, isEphemeral) {
      const headerIcon = document.getElementById('appHeaderIcon');
      headerIcon.innerHTML = OFFICIAL_ICONS[appKey] || '';
      
      const appName = appKey.charAt(0).toUpperCase() + appKey.slice(1);
      document.getElementById('appHeaderTitle').innerText = appName;

      const badge = document.getElementById('appHeaderBadge');
      const shield = (state.app_shields && state.app_shields[appKey]) || {};
      const isMicHardMuted = shield.mic_hard_muted || shield.mic_muted;
      const isDataHardCut = shield.data_hard_cut || shield.data_cut;

      if (isMicHardMuted && isDataHardCut) {
        badge.className = 'badge-ephemeral';
        badge.innerText = '🚫 DATA CUT & MIC MUTED';
      } else if (isMicHardMuted) {
        badge.className = 'badge-ephemeral';
        badge.innerText = '🎙️ MIC HARD-MUTED';
      } else if (isDataHardCut) {
        badge.className = 'badge-ephemeral';
        badge.innerText = '⚡ DATA HARD-CUT';
      } else if (isEphemeral) {
        badge.className = 'badge-ephemeral';
        badge.innerText = '🛡️ EPHEMERAL RAM';
      } else {
        badge.className = 'badge-normal-airgap';
        badge.innerText = 'AIR-GAP PROTECTED';
      }

      const body = document.getElementById('appWindowBody');
      if (appKey === 'zerochat') {
        body.innerHTML = `
          <div style="background:#0b141a; min-height:100%; display:flex; flex-direction:column; margin:-16px; padding:12px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <!-- P2P Peer Network Header Pill -->
            <div style="background:#182229; border:1px solid #22323c; border-radius:10px; padding:8px 12px; margin-bottom:12px; display:flex; align-items:center; justify-content:space-between;">
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1rem;">🧅</span>
                <div>
                  <div style="font-size:0.75rem; font-weight:700; color:#00a884;">TOR v3 PEER-TO-PEER</div>
                  <div style="font-size:0.65rem; color:#8696a0;">0 Central Servers · Direct Phone-to-Phone</div>
                </div>
              </div>
              <span style="font-size:0.65rem; background:#005c4b; color:#fff; padding:2px 8px; border-radius:12px; font-weight:600;">ENCRYPTED</span>
            </div>

            <!-- E2E Security Banner -->
            <div style="background:#182229; border-radius:8px; padding:8px 10px; margin-bottom:12px; text-align:center;">
              <span style="font-size:0.7rem; color:#ffd279; line-height:1.4;">🔒 Messages and files are end-to-end encrypted directly device-to-device over Tor v3 onion circuits. No Meta, Google, or cloud servers exist.</span>
            </div>

            <!-- Active Chat Thread: Alex Rivera -->
            <div id="zerochatMessages" style="flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:8px; margin-bottom:12px; max-height:280px; padding-right:4px;">
              <div class="chat-bubble left" style="background:#202c33; color:#e9edef; border-radius:12px 12px 12px 2px; padding:8px 12px; max-width:85%; align-self:flex-start; font-size:0.8rem; box-shadow:0 1px 2px rgba(0,0,0,0.3);">
                Hey! Is this connection completely serverless?
                <div style="font-size:0.65rem; color:#8696a0; text-align:right; margin-top:4px;">12:38 PM</div>
              </div>

              <div class="chat-bubble right" style="background:#005c4b; color:#e9edef; border-radius:12px 12px 2px 12px; padding:8px 12px; max-width:85%; align-self:flex-end; font-size:0.8rem; box-shadow:0 1px 2px rgba(0,0,0,0.3);">
                Yes 100%. We are communicating directly device-to-device over Tor v3 onion routing. No central database exists.
                <div style="font-size:0.65rem; color:#8696a0; text-align:right; margin-top:4px;">12:40 PM <span style="color:#53bdeb; font-weight:bold;">✓✓</span></div>
              </div>

              <!-- File Attachment Card -->
              <div class="chat-bubble left" style="background:#202c33; color:#e9edef; border-radius:12px 12px 12px 2px; padding:8px 12px; max-width:85%; align-self:flex-start; font-size:0.8rem; box-shadow:0 1px 2px rgba(0,0,0,0.3);">
                <div style="background:#111b21; border-radius:6px; padding:8px; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                  <span style="font-size:1.4rem;">📄</span>
                  <div>
                    <div style="font-size:0.75rem; font-weight:600; color:#fff;">ZeroOS_Whitepaper_v1.pdf</div>
                    <div style="font-size:0.65rem; color:#8696a0;">4.2 MB · Direct Tor P2P Stream</div>
                  </div>
                </div>
                Here is the architectural whitepaper streamed to your phone storage.
                <div style="font-size:0.65rem; color:#8696a0; text-align:right; margin-top:4px;">12:41 PM</div>
              </div>

              <div class="chat-bubble right" style="background:#005c4b; color:#e9edef; border-radius:12px 12px 2px 12px; padding:8px 12px; max-width:85%; align-self:flex-end; font-size:0.8rem; box-shadow:0 1px 2px rgba(0,0,0,0.3);">
                Received and verified SHA256 integrity digest!
                <div style="font-size:0.65rem; color:#8696a0; text-align:right; margin-top:4px;">12:42 PM <span style="color:#53bdeb; font-weight:bold;">✓✓</span></div>
              </div>
            </div>

            <!-- 1-Time Silent SMS Handshake Card (For Unpaired Contacts) -->
            <div id="handshakeCard" style="background:#182229; border:1px solid #334e5e; border-radius:10px; padding:10px; margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:0.75rem; font-weight:700; color:#fff;">⚡ 1-Time Carrier Handshake</span>
                <span style="font-size:0.65rem; color:#f59e0b; font-weight:bold;">1 UNPAIRED CONTACT</span>
              </div>
              <div style="font-size:0.7rem; color:#8696a0; margin-bottom:8px;">
                Pair with <strong>David Kumar (+91 98765-43210)</strong> via an invisible background carrier SMS. Once exchanged, carrier SMS is never used again.
              </div>
              <button onclick="triggerSilentHandshake()" style="width:100%; background:#00a884; color:#000; border:none; padding:8px; border-radius:6px; font-size:0.75rem; font-weight:700; cursor:pointer;">
                🤝 Initiate 1-Time Silent Handshake
              </button>
            </div>

            <!-- WhatsApp 6-Icon Attachment Sheet (Popup) -->
            <div id="zerochatAttachmentSheet" style="display:none; grid-template-columns:repeat(3, 1fr); gap:10px; background:#182229; border:1px solid #2a3942; border-radius:14px; padding:12px; margin-bottom:8px; box-shadow:0 4px 12px rgba(0,0,0,0.5);">
              <div onclick="sendP2PAttachment('document')" style="display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; padding:8px; border-radius:8px; background:#1f2c34;">
                <span style="font-size:1.5rem; background:#5f66cd; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">📄</span>
                <span style="font-size:0.7rem; color:#e9edef;">Document</span>
              </div>
              <div onclick="sendP2PAttachment('camera')" style="display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; padding:8px; border-radius:8px; background:#1f2c34;">
                <span style="font-size:1.5rem; background:#d3396d; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">📷</span>
                <span style="font-size:0.7rem; color:#e9edef;">Camera</span>
              </div>
              <div onclick="sendP2PAttachment('gallery')" style="display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; padding:8px; border-radius:8px; background:#1f2c34;">
                <span style="font-size:1.5rem; background:#ac44cf; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">🖼️</span>
                <span style="font-size:0.7rem; color:#e9edef;">Gallery</span>
              </div>
              <div onclick="sendP2PAttachment('voice')" style="display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; padding:8px; border-radius:8px; background:#1f2c34;">
                <span style="font-size:1.5rem; background:#e07b22; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">🎙️</span>
                <span style="font-size:0.7rem; color:#e9edef;">Audio</span>
              </div>
              <div onclick="sendP2PAttachment('location')" style="display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; padding:8px; border-radius:8px; background:#1f2c34;">
                <span style="font-size:1.5rem; background:#1fa855; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">📍</span>
                <span style="font-size:0.7rem; color:#e9edef;">Location</span>
              </div>
              <div onclick="sendP2PAttachment('contact')" style="display:flex; flex-direction:column; align-items:center; gap:4px; cursor:pointer; padding:8px; border-radius:8px; background:#1f2c34;">
                <span style="font-size:1.5rem; background:#009de2; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center;">👤</span>
                <span style="font-size:0.7rem; color:#e9edef;">Contact</span>
              </div>
            </div>

            <!-- Input Bar -->
            <div style="display:flex; gap:6px; align-items:center; background:#202c33; border-radius:24px; padding:4px 8px;">
              <span style="font-size:1.1rem; cursor:pointer; padding-left:4px;" onclick="toggleAttachmentSheet()" title="Share Media, Location, Contacts, Files">📎</span>
              <input id="zerochatInput" type="text" placeholder="Message via Tor P2P..." style="flex:1; background:transparent; border:none; color:#fff; font-size:0.8rem; outline:none; padding:6px;" onkeydown="if(event.key==='Enter') sendZeroChatMessage()">
              <button onclick="sendZeroChatMessage()" style="width:34px; height:34px; border-radius:50%; background:#00a884; color:#000; border:none; font-size:0.9rem; font-weight:bold; cursor:pointer; display:flex; align-items:center; justify-content:center;">
                ➤
              </button>
            </div>
          </div>
        `;
      } else if (appKey === 'whatsapp') {
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
      } else if (appKey === 'settings') {
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; gap:8px; width:100%; height:100%; overflow-y:auto; padding-right:2px;">
            <div style="font-size:1.2rem; font-weight:300; color:#fff; padding:2px 0 6px 0;">ZeroOS Settings</div>
            
            <div class="settings-card" onclick="toggleFeature('nokia')">
              <div class="settings-icon" style="background:#10b981; color:#000;">🔋</div>
              <div class="settings-content">
                <div class="settings-title">Battery & Longevity</div>
                <div class="settings-sub">${state.battery_days_remaining} Days Remaining · DIA Mode: <b>${state.is_nokia_mode ? 'ON (60Hz)' : 'OFF (120Hz)'}</b></div>
              </div>
            </div>

            <div class="settings-card" onclick="toggleFeature('airgap')">
              <div class="settings-icon" style="background:#3b82f6; color:#fff;">🛡️</div>
              <div class="settings-content">
                <div class="settings-title">Kernel Air-Gap & Permissions</div>
                <div class="settings-sub">Background Killer: <b>${state.auto_airgap_enabled ? 'Active (0 B/s)' : 'Paused'}</b> · Ephemeral Session Guard Active</div>
              </div>
            </div>

            <div class="settings-card" onclick="toggleFeature('grayscale')">
              <div class="settings-icon" style="background:#8b5cf6; color:#fff;">🎨</div>
              <div class="settings-content">
                <div class="settings-title">Display & OLED Palette</div>
                <div class="settings-sub">Palette: <b>${(state.palette||'official').toUpperCase()}</b> · Daltonizer Grayscale: <b>${state.is_grayscale ? 'ACTIVE' : 'OFF'}</b></div>
              </div>
            </div>

            <div class="settings-card" onclick="toggleFeature('digest')">
              <div class="settings-icon" style="background:#f59e0b; color:#000;">🔕</div>
              <div class="settings-content">
                <div class="settings-title">Calm Notifications</div>
                <div class="settings-sub">Batch Digest: <b>${state.calm_digest_enabled ? 'Active (Noise Silenced)' : 'Off'}</b> · Calls/SMS Priority Rings</div>
              </div>
            </div>

            <div class="settings-card" onclick="toggleFeature('hotspot')">
              <div class="settings-icon" style="background:#ec4899; color:#fff;">📶</div>
              <div class="settings-content">
                <div class="settings-title">Hotspot & Radios</div>
                <div class="settings-sub">SSID: <b>${state.hotspot_ssid}</b> · Status: <b>${state.is_hotspot_on ? 'BROADCASTING (1 Device)' : 'OFF'}</b></div>
              </div>
            </div>

            <div class="settings-card">
              <div class="settings-icon" style="background:#06b6d4; color:#000;">🚗</div>
              <div class="settings-content">
                <div class="settings-title">Android Auto & Google Pay</div>
                <div class="settings-sub">Car Projection Privileged Stub: <b>READY</b> · Bank NFC HCE Tap-to-Pay: <b>ACTIVE</b></div>
              </div>
            </div>

            <div class="settings-card" onclick="showToast('☁️ Google Account: Contacts & Calendar Synced (Telemetry Blocked)')">
              <div class="settings-icon" style="background:#ea4335; color:#fff; font-weight:700;">G</div>
              <div class="settings-content">
                <div class="settings-title">Google Account & Cloud Sync</div>
                <div class="settings-sub">Signed in: <b>user@gmail.com</b> · Contacts & Calendar: <b>SYNCED</b> · Ad Trackers: <b>BLOCKED</b></div>
              </div>
            </div>

            <div class="settings-card" onclick="quickRun('about phone')">
              <div class="settings-icon" style="background:#475569; color:#fff;">📱</div>
              <div class="settings-content">
                <div class="settings-title">About ZeroPhone Pro</div>
                <div class="settings-sub">ZeroOS AOSP 14 · Linux 5.10 Kernel · Relocked Titan M2 AVB</div>
              </div>
            </div>
          </div>
        `;
      } else if (appKey === 'phone') {
        if (isCallActive) {
          // ==========================================
          // ACTIVE IN-CALL SCREEN (0W TRUE OLED BLACK)
          // ==========================================
          body.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:space-between; width:100%; height:100%; padding:14px 0 8px 0; background:#000;">
              
              <!-- Contact Info & Timer -->
              <div style="display:flex; flex-direction:column; align-items:center;">
                <div style="width:72px; height:72px; border-radius:50%; background:#1c1c1e; border:1px solid rgba(255,255,255,0.12); display:flex; align-items:center; justify-content:center; font-size:1.8rem; font-weight:bold; color:#fff; margin-bottom:12px;">
                  ${callContactName.charAt(0)}
                </div>
                <div style="font-size:1.25rem; font-weight:700; color:#fff;">${callContactName}</div>
                <div style="font-size:0.78rem; color:#8e8e93; margin-top:2px;">${callContactNumber}</div>
                <div style="font-size:0.85rem; color:#30d158; font-family:'JetBrains Mono', monospace; font-weight:600; margin-top:8px;" id="callTimerDisplay">00:01</div>
              </div>

              <!-- In-Call Actions Grid (Including 1-Tap Record) -->
              <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; width:100%; max-width:270px; margin:20px 0;">
                
                <button class="in-call-btn" onclick="showToast('🔇 Microphone muted for this call')">
                  <div class="in-call-icon">🔇</div>
                  <div class="in-call-label">Mute</div>
                </button>

                <button class="in-call-btn" onclick="showToast('🔢 Dialpad opened')">
                  <div class="in-call-icon">🔢</div>
                  <div class="in-call-label">Keypad</div>
                </button>

                <button class="in-call-btn" onclick="showToast('🔊 Speakerphone toggled')">
                  <div class="in-call-icon">🔊</div>
                  <div class="in-call-label">Speaker</div>
                </button>

                <!-- 1-TAP LOCAL CALL RECORDER -->
                <button id="btnCallRecord" class="in-call-btn" style="background:${isCallRecording ? '#ff453a' : '#27272a'}; color:#fff; border-radius:18px; padding:10px 4px;" onclick="toggleCallRecording()">
                  <div class="in-call-icon">${isCallRecording ? '🔴' : '⏺'}</div>
                  <div class="in-call-label" style="font-weight:700;">${isCallRecording ? 'Recording...' : 'Record'}</div>
                </button>

                <button class="in-call-btn" onclick="showToast('➕ Add call')">
                  <div class="in-call-icon">➕</div>
                  <div class="in-call-label">Add Call</div>
                </button>

                <button class="in-call-btn" onclick="showToast('👤 Contact card opened')">
                  <div class="in-call-icon">👤</div>
                  <div class="in-call-label">Contact</div>
                </button>

              </div>

              <!-- End Call Button -->
              <div style="width:100%; display:flex; justify-content:center;">
                <button style="width:64px; height:64px; border-radius:50%; background:#ff453a; border:none; display:flex; align-items:center; justify-content:center; font-size:1.8rem; color:#fff; cursor:pointer; box-shadow:0 6px 20px rgba(255, 69, 58, 0.4);" onclick="endCall()" title="End Call">
                  🛑
                </button>
              </div>

            </div>
          `;
        } else {
          // ==========================================
          // DIALER TABS: RECENTS, CONTACTS, KEYPAD
          // ==========================================
          body.innerHTML = `
            <div style="display:flex; flex-direction:column; width:100%; height:100%; overflow:hidden;">
              
              <!-- Standard Android Dialer Tabs -->
              <div style="display:flex; justify-content:space-around; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:8px; margin-bottom:8px;">
                <button id="dialerTabRecents" class="dialer-tab active" onclick="switchDialerTab('recents')">🕒 Recents</button>
                <button id="dialerTabContacts" class="dialer-tab" onclick="switchDialerTab('contacts')">👥 Contacts</button>
                <button id="dialerTabKeypad" class="dialer-tab" onclick="switchDialerTab('keypad')">🔢 Keypad</button>
              </div>

              <!-- 1. RECENTS CALL HISTORY TAB -->
              <div id="dialerViewRecents" style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; flex:1; padding-right:2px;">
                <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04);">
                  <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:36px; height:36px; border-radius:50%; background:#2563eb; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.85rem;">M</div>
                    <div>
                      <div style="font-size:0.85rem; font-weight:600; color:#fff;">Mom</div>
                      <div style="font-size:0.7rem; color:#94a3b8;">↙ Incoming · Mobile · 14m ago</div>
                    </div>
                  </div>
                  <button style="background:none; border:none; color:#30d158; font-size:1.1rem; cursor:pointer;" onclick="startCall('Mom', '+1 (555) 234-5678')">📞</button>
                </div>

                <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04);">
                  <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:36px; height:36px; border-radius:50%; background:#ea580c; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.85rem;">S</div>
                    <div>
                      <div style="font-size:0.85rem; font-weight:600; color:#ff453a;">Sarah Jenkins (Missed)</div>
                      <div style="font-size:0.7rem; color:#94a3b8;">↙ Missed · Mobile · 2h ago</div>
                    </div>
                  </div>
                  <button style="background:none; border:none; color:#30d158; font-size:1.1rem; cursor:pointer;" onclick="startCall('Sarah Jenkins', '+1 (555) 987-6543')">📞</button>
                </div>

                <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04);">
                  <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:36px; height:36px; border-radius:50%; background:#059669; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.85rem;">A</div>
                    <div>
                      <div style="font-size:0.85rem; font-weight:600; color:#fff;">Alex Rivera</div>
                      <div style="font-size:0.7rem; color:#94a3b8;">↗ Outgoing · 4m 12s · Yesterday</div>
                    </div>
                  </div>
                  <button style="background:none; border:none; color:#30d158; font-size:1.1rem; cursor:pointer;" onclick="startCall('Alex Rivera', '+1 (555) 345-6789')">📞</button>
                </div>

                <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04);">
                  <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:36px; height:36px; border-radius:50%; background:#64748b; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.85rem;">+44</div>
                    <div>
                      <div style="font-size:0.85rem; font-weight:600; color:#fff;">+44 7911 123456</div>
                      <div style="font-size:0.7rem; color:#94a3b8;">↙ Incoming · 1m 05s · 2 days ago</div>
                    </div>
                  </div>
                  <button style="background:none; border:none; color:#30d158; font-size:1.1rem; cursor:pointer;" onclick="startCall('+44 7911 123456', '+44 7911 123456')">📞</button>
                </div>
              </div>

              <!-- 2. CONTACTS TAB -->
              <div id="dialerViewContacts" style="display:none; flex-direction:column; gap:8px; overflow-y:auto; flex:1; padding-right:2px;">
                <input type="text" placeholder="🔍 Search 182 contacts..." style="background:#171717; border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:8px 12px; color:#fff; font-size:0.8rem; margin-bottom:4px;" />
                
                <div style="font-size:0.7rem; color:#94a3b8; font-weight:700; margin-top:4px;">A</div>
                <div style="padding:6px 4px; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.85rem; color:#fff; display:flex; justify-content:space-between; cursor:pointer;" onclick="startCall('Alex Rivera', '+1 (555) 345-6789')">
                  <span>Alex Rivera</span>
                  <span style="color:#64748b; font-size:0.72rem;">Mobile</span>
                </div>
                <div style="padding:6px 4px; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.85rem; color:#fff; display:flex; justify-content:space-between; cursor:pointer;" onclick="startCall('Aunt Clara', '+1 (555) 888-9999')">
                  <span>Aunt Clara</span>
                  <span style="color:#64748b; font-size:0.72rem;">Home</span>
                </div>

                <div style="font-size:0.7rem; color:#94a3b8; font-weight:700; margin-top:8px;">D</div>
                <div style="padding:6px 4px; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.85rem; color:#fff; display:flex; justify-content:space-between; cursor:pointer;" onclick="startCall('Dr. Michael Patel', '+1 (555) 444-2222')">
                  <span>Dr. Michael Patel</span>
                  <span style="color:#64748b; font-size:0.72rem;">Work</span>
                </div>

                <div style="font-size:0.7rem; color:#94a3b8; font-weight:700; margin-top:8px;">M</div>
                <div style="padding:6px 4px; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.85rem; color:#fff; display:flex; justify-content:space-between; cursor:pointer;" onclick="startCall('Mom', '+1 (555) 234-5678')">
                  <span>Mom</span>
                  <span style="color:#64748b; font-size:0.72rem;">Favorite</span>
                </div>

                <div style="font-size:0.7rem; color:#94a3b8; font-weight:700; margin-top:8px;">S</div>
                <div style="padding:6px 4px; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.85rem; color:#fff; display:flex; justify-content:space-between; cursor:pointer;" onclick="startCall('Sarah Jenkins', '+1 (555) 987-6543')">
                  <span>Sarah Jenkins</span>
                  <span style="color:#64748b; font-size:0.72rem;">Mobile</span>
                </div>
              </div>

              <!-- 3. KEYPAD TAB (STATIC ZERO-ANIMATION TACTILE KEYS) -->
              <div id="dialerViewKeypad" style="display:none; flex-direction:column; align-items:center; justify-content:center; flex:1;">
                <div style="font-size:1.35rem; font-weight:300; color:#fff; margin-bottom:10px; letter-spacing:1px; min-height:28px;" id="dialDisplay">Enter Number</div>
                <div class="dialpad-grid">
                  ${[1,2,3,4,5,6,7,8,9,'*',0,'#'].map(n => `<div class="dial-key" onclick="appendDial('${n}')">${n}</div>`).join('')}
                </div>
                <div style="margin-top:10px; display:flex; gap:14px; align-items:center;">
                  <button class="call-btn-green" onclick="startCall(currentDial, currentDial)">📞 Call</button>
                  <button class="call-btn-del" onclick="clearDial()">⌫</button>
                </div>
              </div>

            </div>
          `;
        }
      } else if (appKey === 'setup') {
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; justify-content:space-between; width:100%; height:100%; padding:16px 8px; background:#000;">
            <div style="text-align:center;">
              <div style="font-size:1.6rem; font-weight:800; color:#fff; letter-spacing:2px; font-family:'JetBrains Mono', monospace; margin-top:16px;">ZERO·OS</div>
              <div style="font-size:0.75rem; color:#8e8e93; margin-top:4px;">First-Boot Onboarding (OOBE)</div>
            </div>

            <div style="background:#121212; border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:16px;">
              <div style="font-size:0.95rem; font-weight:700; color:#fff; margin-bottom:8px;">1. Zero Mandatory Accounts</div>
              <div style="font-size:0.75rem; color:#8e8e93; line-height:1.5; margin-bottom:14px;">
                You are never forced to create or sign into an account. Your phone belongs to you, not a corporation.
              </div>

              <div style="font-size:0.95rem; font-weight:700; color:#fff; margin-bottom:8px;">2. User-Intent Air-Gap</div>
              <div style="font-size:0.75rem; color:#8e8e93; line-height:1.5;">
                When you close an app, network sockets are dropped at the Linux kernel level. 4 to 7 days battery longevity.
              </div>
            </div>

            <div>
              <button style="width:100%; background:#fff; color:#000; border:none; padding:12px; border-radius:14px; font-size:0.85rem; font-weight:700; cursor:pointer;" onclick="launchForegroundApp('phone')">
                Get Started with ZeroPhone ›
              </button>
              <button style="width:100%; background:none; border:none; color:#8e8e93; padding:10px; font-size:0.75rem; cursor:pointer; margin-top:4px;" onclick="closeAppWindow()">
                Skip to Home Screen
              </button>
            </div>
          </div>
        `;
      } else if (appKey === 'messages') {
        // ==========================================
        // ZEROMESSAGES: 2FA AUTO-CLEANUP & THREADS
        // ==========================================
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; width:100%; height:100%; overflow:hidden;">
            
            <!-- 1-TAP 2FA / OTP HERO CARD -->
            <div id="otpCard" style="background:#121212; border:1px solid rgba(48, 209, 88, 0.3); border-radius:16px; padding:12px; margin-bottom:10px; box-shadow:0 4px 16px rgba(0,0,0,0.4);">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <span style="font-size:0.72rem; color:#30d158; font-weight:700;">🔐 BANKING 2FA / OTP DETECTED</span>
                <span style="font-size:0.68rem; color:#8e8e93;">1m ago</span>
              </div>
              <div style="font-size:0.85rem; color:#fff; margin-bottom:8px;">
                <b>HDFC Bank / Chase:</b> Use code <b style="font-size:1.15rem; color:#30d158; font-family:'JetBrains Mono', monospace; letter-spacing:1px;">849 201</b> to verify transaction.
              </div>
              <div style="display:flex; align-items:center; justify-content:space-between;">
                <button style="background:#30d158; color:#000; border:none; padding:7px 14px; border-radius:12px; font-size:0.75rem; font-weight:700; cursor:pointer;" onclick="copyAndAutoDeleteOTP('849201')">
                  📋 Copy 849201 & Auto-Delete in 15m
                </button>
                <span style="font-size:0.65rem; color:#8e8e93;">Expires in 14m</span>
              </div>
            </div>

            <!-- Messages Conversation List -->
            <div style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; flex:1; padding-right:2px;">
              
              <div style="display:flex; align-items:center; gap:12px; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04); cursor:pointer;">
                <div style="width:38px; height:38px; border-radius:50%; background:#2563eb; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.9rem;">M</div>
                <div style="flex:1;">
                  <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:0.85rem; font-weight:600; color:#fff;">Mom</span>
                    <span style="font-size:0.68rem; color:#8e8e93;">4m ago</span>
                  </div>
                  <div style="font-size:0.74rem; color:#8e8e93; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Call me when you get home this evening!</div>
                </div>
              </div>

              <div style="display:flex; align-items:center; gap:12px; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04); cursor:pointer;">
                <div style="width:38px; height:38px; border-radius:50%; background:#ea580c; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.9rem;">S</div>
                <div style="flex:1;">
                  <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:0.85rem; font-weight:600; color:#fff;">Sarah Jenkins</span>
                    <span style="font-size:0.68rem; color:#8e8e93;">1h ago</span>
                  </div>
                  <div style="font-size:0.74rem; color:#8e8e93; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Are we still on for lunch tomorrow afternoon?</div>
                </div>
              </div>

              <div style="display:flex; align-items:center; gap:12px; padding:8px 6px; border-bottom:1px solid rgba(255,255,255,0.04); cursor:pointer;">
                <div style="width:38px; height:38px; border-radius:50%; background:#059669; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:0.9rem;">A</div>
                <div style="flex:1;">
                  <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:0.85rem; font-weight:600; color:#fff;">Alex Rivera</span>
                    <span style="font-size:0.68rem; color:#8e8e93;">Yesterday</span>
                  </div>
                  <div style="font-size:0.74rem; color:#8e8e93; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Sent you the project documents over email.</div>
                </div>
              </div>

              <!-- Calm Digest Marketing SMS Filter Banner -->
              <div style="background:#171717; border-radius:12px; padding:10px; margin-top:8px; border:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:0.72rem; color:#ffd60a; font-weight:600; display:flex; align-items:center; gap:6px;">
                  <span>🔕 Calm Digest Filter Active</span>
                </div>
                <div style="font-size:0.7rem; color:#8e8e93; margin-top:2px;">
                  3 marketing SMS (Uber, Domino's, Telecom) held quietly without notification buzz.
                </div>
              </div>

            </div>

          </div>
        `;
      } else if (appKey === 'camera') {
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; align-items:center; justify-content:space-between; width:100%; height:100%;">
            <div style="font-size:0.72rem; color:#94a3b8; text-align:center;">Raw Sensor Viewfinder · Zero Cloud Telemetry</div>
            <div class="camera-lens-view">
              <div style="width:40px; height:40px; border:1px dashed rgba(255,255,255,0.25); border-radius:50%; margin-bottom:8px;"></div>
              <div style="color:#64748b; font-size:0.75rem;">[Live Sony IMX Sensor Feed]</div>
            </div>
            <div style="display:flex; align-items:center; gap:24px; padding:6px 0 10px 0;">
              <div style="width:34px; height:34px; border-radius:50%; background:#1e293b;"></div>
              <button class="camera-shutter-btn" onclick="showToast('📸 Photo captured to encrypted storage')"></button>
              <div style="width:34px; height:34px; border-radius:50%; background:#1e293b;"></div>
            </div>
          </div>
        `;
      } else if (appKey === 'spotify') {
        const isPlaying = state.is_spotify_playing;
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; align-items:center; justify-content:space-between; width:100%; height:100%; padding:8px 0;">
            <div style="font-size:0.72rem; color:#94a3b8;">Intentional Media Session · Audio Streaming Only</div>
            
            <div style="width:130px; height:130px; border-radius:16px; background:#18202d; display:flex; align-items:center; justify-content:center; box-shadow:0 8px 24px rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.06);">
              <div style="width:64px; height:64px;">${OFFICIAL_ICONS['spotify']}</div>
            </div>

            <div style="text-align:center;">
              <div style="font-size:1.05rem; font-weight:700; color:#fff;">Blinding Lights</div>
              <div style="font-size:0.78rem; color:#94a3b8; margin-top:2px;">The Weeknd · After Hours</div>
            </div>

            <!-- Progress Bar -->
            <div style="width:100%; padding:0 8px;">
              <div style="height:4px; background:#232d3d; border-radius:2px; position:relative; overflow:hidden;">
                <div style="width:${isPlaying ? '68%' : '35%'}; height:100%; background:#1db954; transition:width 0.3s;"></div>
              </div>
              <div style="display:flex; justify-content:space-between; font-size:0.68rem; color:#64748b; margin-top:4px;">
                <span>${isPlaying ? '2:14' : '1:08'}</span>
                <span>3:20</span>
              </div>
            </div>

            <!-- Controls -->
            <div style="display:flex; align-items:center; gap:20px;">
              <button style="background:none; border:none; color:#cbd5e1; font-size:1.2rem; cursor:pointer;" onclick="showToast('⏮ Previous track')">⏮</button>
              <button style="background:#1db954; color:#000; border:none; width:48px; height:48px; border-radius:50%; font-size:1.2rem; display:flex; align-items:center; justify-content:center; cursor:pointer; font-weight:bold;" onclick="toggleMediaPlayback()">
                ${isPlaying ? '⏸' : '▶'}
              </button>
              <button style="background:none; border:none; color:#cbd5e1; font-size:1.2rem; cursor:pointer;" onclick="showToast('⏭ Next track')">⏭</button>
            </div>

            <div style="font-size:0.68rem; color:${isPlaying ? '#34d399' : '#94a3b8'}; text-align:center; padding:0 12px; line-height:1.3;">
              ${isPlaying ? '🎵 Audio plays in background when screen turns off (Ad trackers blocked).' : '⏸ Paused. Steel door will engage immediately when you exit.'}
            </div>
          </div>
        `;
      } else if (appKey === 'maps') {
        const isNav = state.is_maps_navigating;
        body.innerHTML = `
          <div style="display:flex; flex-direction:column; width:100%; height:100%; justify-content:space-between;">
            
            <div style="background:#141b26; border-radius:14px; padding:12px; border:1px solid rgba(255,255,255,0.06);">
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:34px; height:34px; border-radius:50%; background:#3b82f6; display:flex; align-items:center; justify-content:center; font-size:1.1rem; font-weight:bold; color:#fff;">↱</div>
                <div>
                  <div style="font-size:0.9rem; font-weight:700; color:#fff;">Turn right on Grand Ave</div>
                  <div style="font-size:0.72rem; color:#94a3b8;">In 250 meters · Then keep left</div>
                </div>
              </div>
              <div style="margin-top:10px; display:flex; justify-content:space-between; font-size:0.78rem; border-top:1px solid #1f2937; padding-top:6px;">
                <span style="color:#34d399; font-weight:700;">12 min</span>
                <span style="color:#94a3b8;">4.8 km · 14:48 arrival</span>
              </div>
            </div>

            <div style="flex:1; background:#0b1017; border-radius:12px; margin:8px 0; border:1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; align-items:center; justify-content:center;">
              <div style="color:#475569; font-size:0.75rem;">[Offline Vector Navigation View]</div>
              <div style="font-size:0.68rem; color:#64748b; margin-top:4px;">GNSS Live Coordinates: 51.5074° N, 0.1278° W</div>
              <div style="margin-top:6px; display:inline-block; padding:3px 8px; border-radius:8px; font-size:0.65rem; background:${isNav ? '#10b981' : '#334155'}; color:${isNav ? '#000' : '#cbd5e1'}; font-weight:700;">
                ${isNav ? 'ACTIVE TRIP NAVIGATION' : 'IDLE PREVIEW'}
              </div>
            </div>

            <div>
              <button style="width:100%; background:${isNav ? '#ef4444' : '#3b82f6'}; color:#fff; border:none; padding:11px; border-radius:12px; font-size:0.82rem; font-weight:700; cursor:pointer;" onclick="toggleTripNavigation()">
                ${isNav ? '🛑 End Navigation Trip' : '🧭 Start Turn-by-Turn Route'}
              </button>
            </div>
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

    async function toggleMediaPlayback() {
      const res = await fetch('/api/toggle_media', { method: 'POST' });
      const data = await res.json();
      state = data.state;
      renderUI();
      if (state.active_app) renderActiveAppContent(state.active_app, state.is_ephemeral);
      showToast(data.message);
    }

    async function toggleTripNavigation() {
      const res = await fetch('/api/toggle_navigation', { method: 'POST' });
      const data = await res.json();
      state = data.state;
      renderUI();
      if (state.active_app) renderActiveAppContent(state.active_app, state.is_ephemeral);
      showToast(data.message);
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

    async function clearDigestNotifications() {
      const res = await fetch('/api/clear_digest', { method: 'POST' });
      const data = await res.json();
      state = data.state;
      renderUI();
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
      if (data.message) {
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
      showToast("⚡ Power Button: Command Bar Armed");
    }

    function showToast(msg) {
      const toast = document.getElementById('androidToast');
      toast.innerText = msg;
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }

    // Auto-refresh clock
    loadState();

    // Tap outside shade or bottom drag handle to close naturally like stock Android
    const shadeEl = document.getElementById('notificationShade');
    shadeEl.addEventListener('click', function(e) {
      if (e.target === this || e.target.classList.contains('oneui-bottom-handle') || e.target.classList.contains('oneui-drag-pill')) {
        closeNotificationShade();
      }
    });
    setInterval(() => {
      const now = new Date();
      const timeStr = now.toTimeString().slice(0, 5);
      document.getElementById('statusClock').innerText = timeStr;
      document.getElementById('shadeClock').innerText = timeStr;
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

@app.route("/api/toggle_feature", methods=["POST"])
def toggle_feature():
    data = request.get_json(silent=True) or {}
    feat = data.get("feature")

    if feat == "wifi":
        STATE["is_wifi_on"] = not STATE.get("is_wifi_on", True)
        act = "CONNECTED (Home-5G)" if STATE["is_wifi_on"] else "DISCONNECTED"
        STATE["kernel_logs"].append(f"[Netd] wlan0 interface state -> {act}")
        msg = f"📶 Wi-Fi {act}."

    elif feat == "bluetooth":
        STATE["is_bluetooth_on"] = not STATE.get("is_bluetooth_on", True)
        act = "CONNECTED (WH-1000XM5)" if STATE["is_bluetooth_on"] else "OFF"
        STATE["kernel_logs"].append(f"[BlueDroid] Bluetooth adapter state -> {act}")
        msg = f"ᛒ Bluetooth {act}."

    elif feat == "sound":
        modes = ["sound", "vibrate", "silent"]
        curr = STATE.get("sound_mode", "sound")
        STATE["sound_mode"] = modes[(modes.index(curr) + 1) % len(modes)]
        STATE["kernel_logs"].append(f"[AudioService] Ringer mode changed to {STATE['sound_mode'].upper()}")
        msg = f"🔔 Sound mode: {STATE['sound_mode'].capitalize()}."

    elif feat == "hotspot":
        STATE["is_hotspot_on"] = not STATE["is_hotspot_on"]
        act = "ON" if STATE["is_hotspot_on"] else "OFF"
        if STATE["is_hotspot_on"]:
            STATE["kernel_logs"].append(f"[Tethering] Hotspot broadcast active: SSID '{STATE['hotspot_ssid']}'")
        else:
            STATE["kernel_logs"].append("[Tethering] Hotspot disabled. Radios offline.")
        msg = f"(((•))) Hotspot turned {act}."

    elif feat == "torch":
        STATE["is_torch_on"] = not STATE["is_torch_on"]
        act = "ON" if STATE["is_torch_on"] else "OFF"
        STATE["kernel_logs"].append(f"[GPIO] Flashlight toggled {act}")
        msg = f"🔦 Flashlight turned {act}."

    elif feat == "dia" or feat == "nokia":
        STATE["is_dia_mode"] = not STATE["is_dia_mode"]
        STATE["battery_days_remaining"] = 5.8 if STATE["is_dia_mode"] else 4.2
        act = "ON" if STATE["is_dia_mode"] else "OFF"
        STATE["kernel_logs"].append(f"[PowerHAL] DIA Mode toggled {act} (60Hz / 1-bit monochrome)")
        msg = f"🔋 DIA Mode turned {act}."

    elif feat == "grayscale":
        STATE["is_grayscale"] = not STATE["is_grayscale"]
        act = "ON" if STATE["is_grayscale"] else "OFF"
        STATE["kernel_logs"].append(f"[Daltonizer] Grayscale display mode toggled {act}")
        msg = f"🌓 Grayscale turned {act}."

    elif feat == "digest":
        STATE["calm_digest_enabled"] = not STATE["calm_digest_enabled"]
        act = "ACTIVE" if STATE["calm_digest_enabled"] else "PAUSED"
        STATE["kernel_logs"].append(f"[CalmDigest] Notification batching toggled {act}")
        msg = f"🔕 Calm Digest {act}."

    elif feat == "airgap":
        STATE["auto_airgap_enabled"] = not STATE["auto_airgap_enabled"]
        act = "ACTIVE" if STATE["auto_airgap_enabled"] else "PAUSED"
        STATE["kernel_logs"].append(f"[AutoAirGap] Automatic zero-leak policy {act}")
        msg = f"🛡️ Auto Air-Gap policy {act}."

    elif feat == "mic":
        STATE["is_mic_killed"] = not STATE["is_mic_killed"]
        act = "LOCKED (SILENCE)" if STATE["is_mic_killed"] else "UNLOCKED"
        STATE["kernel_logs"].append(f"[AppOps] Microphone hardware register toggled {act}")
        msg = f"🎙️ Microphone hardware register {act}."

    elif feat == "micro":
        STATE["is_micro_window"] = not STATE["is_micro_window"]
        act = "ON (0W Mode)" if STATE["is_micro_window"] else "OFF"
        STATE["kernel_logs"].append(f"[SurfaceFlinger] Micro window clamped display {act}")
        msg = f"📱 Micro Screen {act}."

    else:
        msg = "Unknown feature toggle."

    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/launch_app", methods=["POST"])
def launch_app():
    data = request.get_json(silent=True) or {}
    app_key = data.get("app_key")
    is_ephemeral = data.get("is_ephemeral", False)

    STATE["active_app"] = app_key
    STATE["is_ephemeral"] = is_ephemeral

    app_name = app_key.capitalize() if app_key else "App"
    shield = STATE["app_shields"].get(app_key, {})
    is_mic_hard_muted = shield.get("mic_hard_muted", False) or shield.get("mic_muted", False)
    is_data_hard_cut = shield.get("data_hard_cut", False) or shield.get("data_cut", False)

    # 1. Data check
    if is_data_hard_cut:
        STATE["kernel_logs"].append(f"[AutoAirGap] Policy Check: Mobile data is HARD-CUT for 'com.{app_key}'. Netfilter iptables DROP preserved in foreground!")
    else:
        STATE["kernel_logs"].append(f"[AutoAirGap] '{app_name}' FOREGROUND: Restored network sockets")

    # 2. Mic / Sensor check (Respect user permanent command)
    if is_mic_hard_muted:
        STATE["kernel_logs"].append(f"[SingleSessionPerm] Policy Check: Microphone is HARD-MUTED for 'com.{app_key}'. Hardware register locked to silence even during active session!")
        STATE["kernel_logs"].append(f"[AppOps] cmd appops set com.{app_key} RECORD_AUDIO deny")
    else:
        STATE["kernel_logs"].append(f"[SingleSessionPerm] Ephemeral session active for 'com.{app_key}'. Auto-revoked on exit.")

    # 3. Message formatting
    if is_mic_hard_muted and is_data_hard_cut:
        msg = f"Opened {app_name}. (Data is CUT & Mic is MUTED per your command)."
    elif is_mic_hard_muted:
        msg = f"Opened {app_name}. (Microphone is HARD-MUTED per your command - 0 audio access)."
    elif is_data_hard_cut:
        msg = f"Opened {app_name}. (Data is HARD-CUT per your command - 0 B/s)."
    elif is_ephemeral:
        STATE["kernel_logs"].append(f"[EphemeralSandbox] Mounted tmpfs RAM overlay on /data/data/{app_key}. Session is disposable.")
        msg = f"🛡️ Opened {app_name} in Ephemeral RAM Sandbox."
    else:
        msg = f"Opened {app_name}."

    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/toggle_media", methods=["POST"])
def toggle_media():
    STATE["is_spotify_playing"] = not STATE.get("is_spotify_playing", False)
    if STATE["is_spotify_playing"]:
        STATE["kernel_logs"].append("[MediaNavGuard] Spotify audio STARTED. Intentional playback granted streaming exception.")
        msg = "🎵 Spotify is now PLAYING (Will stay active when screen locks)."
    else:
        STATE["kernel_logs"].append("[MediaNavGuard] Spotify PAUSED. Instant zero-leak Air-Gap armed.")
        msg = "⏸ Spotify PAUSED. Background data severed."
    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/toggle_navigation", methods=["POST"])
def toggle_navigation():
    STATE["is_maps_navigating"] = not STATE.get("is_maps_navigating", False)
    if STATE["is_maps_navigating"]:
        STATE["kernel_logs"].append("[MediaNavGuard] Google Maps navigation STARTED. GNSS stream active for trip.")
        msg = "🧭 Turn-by-turn navigation ACTIVE (Will speak directions with screen off)."
    else:
        STATE["kernel_logs"].append("[MediaNavGuard] Navigation ENDED. GNSS sensor permissions wiped.")
        msg = "🛑 Navigation ENDED. GPS hardware revoked immediately."
    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/close_app", methods=["POST"])
def close_app():
    closed_app = STATE["active_app"] or "App"
    is_ephemeral = STATE["is_ephemeral"]

    # Check Intentional Media Exception (Spotify)
    if closed_app == "spotify" and STATE.get("is_spotify_playing", False):
        STATE["active_app"] = None
        STATE["kernel_logs"].append("[MediaNavGuard] Intentional Media Session: 'com.spotify.music' holding audio socket. Ad analytics dropped.")
        msg = "🎵 Spotify playing in background (Audio only · Trackers dropped)."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # Check Intentional Navigation Exception (Google Maps)
    if closed_app == "maps" and STATE.get("is_maps_navigating", False):
        STATE["active_app"] = None
        STATE["kernel_logs"].append("[MediaNavGuard] Active Navigation Session: 'com.google.android.apps.maps' holding GNSS stream for trip.")
        msg = "🧭 Google Maps navigating in background (Trip guidance active)."
        return jsonify({"success": True, "message": msg, "state": STATE})
    closed_app = STATE["active_app"] or "App"
    is_ephemeral = STATE["is_ephemeral"]

    # 1. Trigger Air-Gap lockdown & Single-Session PC-style Revocation
    STATE["active_app"] = None
    STATE["is_ephemeral"] = False

    app_name = closed_app.capitalize()
    STATE["kernel_logs"].append(f"[AutoAirGap] '{app_name}' BACKGROUND: Steel door slammed!")
    STATE["kernel_logs"].append(f"[SingleSessionPerm] PC-style auto-revocation: Revoked ACCESS_FINE_LOCATION and RECORD_AUDIO for com.{closed_app}")
    STATE["kernel_logs"].append(f"[AppOps] cmd appops set com.{closed_app} RECORD_AUDIO deny (Hardware silence)")
    STATE["kernel_logs"].append(f"[AppOps] cmd appops set com.{closed_app} ACCESS_FINE_LOCATION deny (GPS unlinked)")
    STATE["kernel_logs"].append(f"[pm] pm revoke com.{closed_app} android.permission.ACCESS_FINE_LOCATION (Auto-revoked)")
    STATE["kernel_logs"].append(f"[pm] pm revoke com.{closed_app} android.permission.RECORD_AUDIO (Auto-revoked)")
    STATE["kernel_logs"].append(f"[iptables] iptables -I OUTPUT -m owner --uid-owner com.{closed_app} -j DROP (0 B/s)")
    STATE["kernel_logs"].append(f"[cgroups] Scaled CPU quota to 0%. Frozen into Linux deep sleep.")

    # 2. If Ephemeral, wipe all data
    if is_ephemeral:
        STATE["kernel_logs"].append(f"[EphemeralSandbox] Vaporizing all temporary cookies, storage & tokens for com.{closed_app}!")
        msg = f"🔒 {app_name} closed: All session data wiped. Location & Mic turned OFF automatically."
    else:
        msg = f"🔒 {app_name} closed: Location & Mic turned OFF automatically (0 B/s data leak)."

    # 3. Update Impact Tracker
    STATE["impact_stats"]["trackers_blocked"] += 14
    STATE["impact_stats"]["airgapped_apps"] += 1
    STATE["impact_stats"]["mic_hours_locked"] += 0.5

    return jsonify({"success": True, "message": msg, "state": STATE})

@app.route("/api/clear_digest", methods=["POST"])
def clear_digest():
    count = len(STATE["calm_digest_items"])
    STATE["calm_digest_items"] = []
    STATE["kernel_logs"].append(f"[CalmDigest] Cleared {count} held notification items.")
    return jsonify({"success": True, "message": f"Archived {count} alerts from Calm Digest.", "state": STATE})

@app.route("/api/command", methods=["POST"])
def process_command():
    data = request.get_json(silent=True) or {}
    raw_cmd = data.get("command", "").strip()
    lower = raw_cmd.lower()

            # ZEROMAPS OFFLINE NAVIGATION
    if any(w in lower for w in ["zeromaps", "maps", "navigation", "navigate", "directions", "turn by turn", "gps"]):
        STATE["active_app"] = "maps"
        STATE["kernel_logs"].append("[ZeroMaps] Offline OpenStreetMap engine loaded. GNSS fix acquired (0 cloud requests).")
        return jsonify({"success": True, "message": "🗺️ Opened ZeroMaps (100% Offline Vector Navigation).", "state": STATE})

    # ZEROCHAT P2P MESSAGING COMMANDS
    if any(w in lower for w in ["zerochat", "p2p chat", "tor chat", "peer to peer"]) or (("chat" in lower or "message" in lower) and not "sms" in lower and not "delete" in lower):
        STATE["active_app"] = "zerochat"
        STATE["kernel_logs"].append("[ZeroMesh] ZeroChat invoked. Tor v3 onion listening socket active (0 servers).")
        return jsonify({"success": True, "message": "💬 Opened ZeroChat (100% Peer-to-Peer over Tor v3).", "state": STATE})

    if "handshake" in lower:
        STATE["active_app"] = "zerochat"
        STATE["kernel_logs"].append("[ZeroMesh] 1-Time Silent Carrier SMS dispatched to peer contact.")
        STATE["kernel_logs"].append("[ZeroMesh] Peer responded with Tor onion key: ed25519_pk_0x8f4a... PAIRING COMPLETE.")
        return jsonify({"success": True, "message": "🤝 1-Time Silent SMS Handshake SUCCESS! Contact is now paired over Tor v3.", "state": STATE})

    # FIRST-BOOT SETUP WIZARD (OOBE)
    if "setup" in lower or "oobe" in lower or "wizard" in lower:
        STATE["active_app"] = "setup"
        STATE["kernel_logs"].append("[OOBE] SetupWizardActivity invoked. First-boot onboarding active.")
        return jsonify({"success": True, "message": "🚀 Launched ZeroOS First-Boot Setup Wizard.", "state": STATE})

    # WI-FI TOGGLE & COMMAND
    if "wifi" in lower or "wi-fi" in lower:
        if "off" in lower or "disconnect" in lower or "disable" in lower:
            STATE["is_wifi_on"] = False
        elif "on" in lower or "connect" in lower or "enable" in lower:
            STATE["is_wifi_on"] = True
        else:
            STATE["is_wifi_on"] = not STATE.get("is_wifi_on", True)
        act = "CONNECTED (Home-5G)" if STATE["is_wifi_on"] else "DISCONNECTED"
        STATE["kernel_logs"].append(f"[Netd] wlan0 interface state -> {act}")
        return jsonify({"success": True, "message": f"📶 Wi-Fi is now {act}.", "state": STATE})

    # BLUETOOTH TOGGLE & COMMAND
    if "bluetooth" in lower or " bt" in lower or lower.startswith("bt"):
        if "off" in lower or "disconnect" in lower or "disable" in lower:
            STATE["is_bluetooth_on"] = False
        elif "on" in lower or "connect" in lower or "enable" in lower:
            STATE["is_bluetooth_on"] = True
        else:
            STATE["is_bluetooth_on"] = not STATE.get("is_bluetooth_on", True)
        act = "CONNECTED (WH-1000XM5)" if STATE["is_bluetooth_on"] else "OFF"
        STATE["kernel_logs"].append(f"[BlueDroid] Bluetooth adapter state -> {act}")
        return jsonify({"success": True, "message": f"ᛒ Bluetooth is now {act}.", "state": STATE})

    # SOUND / VIBRATE / SILENT MODE
    if any(w in lower for w in ["sound", "vibrate", "silent", "ringer", "dnd"]):
        if "silent" in lower or "mute" in lower or "dnd" in lower:
            STATE["sound_mode"] = "silent"
        elif "vibrate" in lower or "vib" in lower:
            STATE["sound_mode"] = "vibrate"
        elif "sound" in lower or "ring" in lower:
            STATE["sound_mode"] = "sound"
        else:
            modes = ["sound", "vibrate", "silent"]
            curr = STATE.get("sound_mode", "sound")
            STATE["sound_mode"] = modes[(modes.index(curr) + 1) % len(modes)]
        STATE["kernel_logs"].append(f"[AudioService] Ringer mode changed to {STATE['sound_mode'].upper()}")
        return jsonify({"success": True, "message": f"🔔 Sound mode: {STATE['sound_mode'].capitalize()}.", "state": STATE})

    # BRIGHTNESS SLIDER / COMMAND
    if "brightness" in lower or ("light" in lower and any(c.isdigit() for c in lower)):
        import re
        nums = re.findall(r'\d+', lower)
        if nums:
            val = max(10, min(100, int(nums[0])))
            STATE["brightness"] = val
            STATE["kernel_logs"].append(f"[DisplayPower] Backlight PWM set to {val}%")
            return jsonify({"success": True, "message": f"☀️ Brightness set to {val}%.", "state": STATE})

    # VOLUME SLIDER / COMMAND
    if "volume" in lower:
        import re
        nums = re.findall(r'\d+', lower)
        if nums:
            val = max(0, min(100, int(nums[0])))
            STATE["volume"] = val
            STATE["kernel_logs"].append(f"[AudioHAL] Master hardware gain set to {val}%")
            return jsonify({"success": True, "message": f"🔊 Media volume set to {val}%.", "state": STATE})

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

    # HARDWARE: FLASHLIGHT / TORCH (BIDIRECTIONAL TOGGLE)
    if "flash" in lower or "torch" in lower:
        if "off" in lower or "stop" in lower or "disable" in lower:
            STATE["is_torch_on"] = False
        elif "on" in lower or "start" in lower or "enable" in lower:
            STATE["is_torch_on"] = True
        else:
            STATE["is_torch_on"] = not STATE["is_torch_on"]
        msg = "🔦 Flashlight turned ON." if STATE["is_torch_on"] else "🔦 Flashlight turned OFF."
        STATE["kernel_logs"].append(f"[SYS_GPIO] cameraManager.setTorchMode(0, {STATE['is_torch_on']}) -> SUCCESS")
        return jsonify({"success": True, "message": msg, "state": STATE})

    # HARDWARE: WI-FI HOTSPOT (BIDIRECTIONAL TOGGLE)
    if "hotspot" in lower or "tether" in lower:
        if "off" in lower or "stop" in lower or "disable" in lower:
            STATE["is_hotspot_on"] = False
        elif "on" in lower or "start" in lower or "enable" in lower:
            STATE["is_hotspot_on"] = True
        else:
            STATE["is_hotspot_on"] = not STATE["is_hotspot_on"]
        if STATE["is_hotspot_on"]:
            STATE["kernel_logs"].append(f"[HOSTAPD] Broadcasting SSID='{STATE['hotspot_ssid']}', WPA3-SAE (5GHz)")
            msg = f"(((•))) Hotspot ACTIVE: Broadcasting '{STATE['hotspot_ssid']}'. 1 device connected."
        else:
            STATE["kernel_logs"].append("[HOSTAPD] hostapd daemon stopped. AP interface wlan0 DOWN.")
            msg = "(((•))) Hotspot turned OFF."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # DIA MODE (DEEP-IDLE ARCHITECTURE - 5-7 DAY BATTERY)
    if "dia" in lower or "nokia" in lower:
        if "off" in lower or "exit" in lower or "disable" in lower:
            STATE["is_dia_mode"] = False
            STATE["battery_days_remaining"] = 4.2
            STATE["kernel_logs"].append("[CPUFREQ] Restored normal governor. 120Hz display online.")
            msg = "DIA Mode deactivated. Full color & 120Hz restored."
        elif "on" in lower or "enable" in lower:
            STATE["is_dia_mode"] = True
            STATE["battery_days_remaining"] = 5.8
            STATE["kernel_logs"].append("[CPUFREQ] Scaled governor to powersave. Deep Linux C-states forced.")
            msg = "🔋 DIA Mode turned ON. Display clamped to 60Hz 1-bit monochrome."
        else:
            STATE["is_dia_mode"] = not STATE["is_dia_mode"]
            STATE["battery_days_remaining"] = 5.8 if STATE["is_dia_mode"] else 4.2
            act = "ON" if STATE["is_dia_mode"] else "OFF"
            STATE["kernel_logs"].append(f"[PowerHAL] DIA Mode toggled {act}.")
            msg = f"🔋 DIA Mode turned {act}."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # GRAYSCALE (BIDIRECTIONAL TOGGLE)
    if "grayscale" in lower or "monochrome" in lower:
        if "off" in lower or "disable" in lower:
            STATE["is_grayscale"] = False
            STATE["kernel_logs"].append("[DALTONIZER] Settings.Secure.putInt('accessibility_display_daltonizer_enabled', 0)")
            msg = "🌈 Color display restored."
        elif "on" in lower or "enable" in lower:
            STATE["is_grayscale"] = True
            STATE["kernel_logs"].append("[DALTONIZER] Settings.Secure.putInt('accessibility_display_daltonizer_enabled', 1)")
            msg = "🌓 Grayscale Mode turned ON."
        else:
            STATE["is_grayscale"] = not STATE["is_grayscale"]
            act = "ON" if STATE["is_grayscale"] else "OFF"
            STATE["kernel_logs"].append(f"[Daltonizer] Grayscale toggled {act}.")
            msg = f"🌓 Grayscale turned {act}."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # CALM DIGEST
    if "calm" in lower or "digest" in lower:
        STATE["calm_digest_enabled"] = not STATE["calm_digest_enabled"]
        act = "ACTIVE" if STATE["calm_digest_enabled"] else "PAUSED"
        msg = f"🔕 Calm Digest is now {act}."
        return jsonify({"success": True, "message": msg, "state": STATE})

    # EPHEMERAL APP LAUNCH
    if "ephemeral" in lower or "disposable" in lower or "temp " in lower:
        target = "instagram"
        for k in ["whatsapp", "instagram", "tiktok", "youtube", "monzo", "chrome"]:
            if k in lower:
                target = k
                break
        return launch_app_internal(target, is_ephemeral=True)

    SOCIAL_MEDIA_APPS = ["instagram", "tiktok", "youtube", "whatsapp"]
    ALL_SHIELD_APPS = list(STATE["app_shields"].keys())

    # BIDIRECTIONAL MIC ENGINE (UNMUTE & MUTE)
    has_unmute = any(w in lower for w in ["unmute", "un-mute", "allow", "restore", "turn on mic", "enable mic", "enable microphone"])
    has_mute = not has_unmute and any(w in lower for w in ["mute", "cut mic", "block mic", "kill mic", "disable mic", "turn off mic"])
    has_toggle = any(w in lower for w in ["toggle mic", "switch mic", "change mic"])

    # 1. UNMUTE MIC
    if has_unmute or (has_toggle and any(STATE["app_shields"][k].get("mic_hard_muted") for k in SOCIAL_MEDIA_APPS)):
        if "all" in lower or "everywhere" in lower:
            targets = ALL_SHIELD_APPS
        elif any(k in lower for k in STATE["app_shields"].keys()):
            targets = [k for k in STATE["app_shields"].keys() if k in lower]
        else:
            targets = SOCIAL_MEDIA_APPS  # Default target is all social media

        for t in targets:
            if t in STATE["app_shields"]:
                app_obj = STATE["app_shields"][t]
                app_obj["mic_muted"] = False
                app_obj["mic_hard_muted"] = False
                STATE["kernel_logs"].append(f"[AppOps] cmd appops set {app_obj['package']} RECORD_AUDIO allow -> Restored to Single-Session")
        names = [STATE["app_shields"][t]["name"] for t in targets if t in STATE["app_shields"]]
        return jsonify({
            "success": True,
            "message": f"🎙️ Microphone UNMUTED: Restored to automatic single-session for: {', '.join(names)}.",
            "state": STATE
        })

    # 2. MUTE MIC
    if has_mute or has_toggle or (any(w in lower for w in ["mic", "microphone"]) and any(w in lower for w in ["cut", "block", "kill", "stop", "disable", "off"])):
        if "all" in lower or "everywhere" in lower:
            targets = ALL_SHIELD_APPS
        elif any(k in lower for k in STATE["app_shields"].keys()):
            targets = [k for k in STATE["app_shields"].keys() if k in lower]
        else:
            targets = SOCIAL_MEDIA_APPS  # Default target is all social media
        
        for t in targets:
            if t in STATE["app_shields"]:
                app_obj = STATE["app_shields"][t]
                app_obj["mic_muted"] = True
                app_obj["mic_hard_muted"] = True
                STATE["kernel_logs"].append(f"[PolicyStore] PERMANENT HARD-MUTE rule: {app_obj['package']}")
                STATE["kernel_logs"].append(f"[AppOps] cmd appops set {app_obj['package']} RECORD_AUDIO deny")
                STATE["kernel_logs"].append(f"[AudioHAL] Directing digital silence (/dev/zero) to UID PCM stream for {t}.")
        names = [STATE["app_shields"][t]["name"] for t in targets if t in STATE["app_shields"]]
        return jsonify({
            "success": True,
            "message": f"🎙️ Microphone MUTED: Access permanently blocked for: {', '.join(names)}.",
            "state": STATE
        })

    # CUT DATA FOR APPS
    has_data_word = any(w in lower for w in ["data", "internet", "wifi", "cellular", "net"])
    if has_data_word and has_cut_word:
        if "social" in lower:
            targets = SOCIAL_MEDIA_APPS
        elif "all" in lower or "everywhere" in lower:
            targets = ALL_SHIELD_APPS
        else:
            targets = [k for k in STATE["app_shields"].keys() if k in lower] or ["instagram", "tiktok"]
        for t in targets:
            if t in STATE["app_shields"]:
                app_obj = STATE["app_shields"][t]
                app_obj["data_cut"] = True
                app_obj["data_hard_cut"] = True
                STATE["kernel_logs"].append(f"[PolicyStore] PERMANENT HARD-CUT data rule: {app_obj['package']}")
                STATE["kernel_logs"].append(f"[iptables] iptables -I OUTPUT -m owner --uid-owner {app_obj['package']} -j DROP")
        names = [STATE["app_shields"][t]["name"] for t in targets if t in STATE["app_shields"]]
        return jsonify({
            "success": True,
            "message": f"⚡ Internet severed permanently for: {', '.join(names)}. App will remain offline (0 B/s) even in foreground.",
            "state": STATE
        })

    # RESTORE DATA FOR APPS
    if has_data_word and any(w in lower for w in ["restore", "allow", "unblock", "turn on", "enable"]):
        if "social" in lower:
            targets = SOCIAL_MEDIA_APPS
        elif "all" in lower or "everywhere" in lower:
            targets = ALL_SHIELD_APPS
        else:
            targets = [k for k in STATE["app_shields"].keys() if k in lower] or ["instagram", "tiktok"]
        for t in targets:
            if t in STATE["app_shields"]:
                app_obj = STATE["app_shields"][t]
                app_obj["data_cut"] = False
                app_obj["data_hard_cut"] = False
                STATE["kernel_logs"].append(f"[iptables] iptables -D OUTPUT -m owner --uid-owner {app_obj['package']} -j DROP")
        names = [STATE["app_shields"][t]["name"] for t in targets if t in STATE["app_shields"]]
        return jsonify({
            "success": True,
            "message": f"⚡ Mobile data restored for: {', '.join(names)}.",
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

    shield = STATE["app_shields"].get(app_key, {})
    is_mic_hard_muted = shield.get("mic_hard_muted", False) or shield.get("mic_muted", False)
    is_data_hard_cut = shield.get("data_hard_cut", False) or shield.get("data_cut", False)

    # 1. Data check
    if is_data_hard_cut:
        STATE["kernel_logs"].append(f"[AutoAirGap] Policy Check: Mobile data is HARD-CUT for 'com.{app_key}'. Netfilter iptables DROP preserved in foreground!")
    else:
        STATE["kernel_logs"].append(f"[AutoAirGap] '{app_name}' entering FOREGROUND: Restored network sockets")

    # 2. Mic / Sensor check (Respect user permanent command)
    if is_mic_hard_muted:
        STATE["kernel_logs"].append(f"[SingleSessionPerm] Policy Check: Microphone is HARD-MUTED for 'com.{app_key}'. Hardware register locked to silence even during active session!")
        STATE["kernel_logs"].append(f"[AppOps] cmd appops set com.{app_key} RECORD_AUDIO deny")
    else:
        STATE["kernel_logs"].append(f"[SingleSessionPerm] Ephemeral session active for 'com.{app_key}'. Auto-revoked on exit.")

    # 3. Response message
    if is_mic_hard_muted and is_data_hard_cut:
        msg = f"Opened {app_name}. (Data is CUT & Mic is MUTED per your command)."
    elif is_mic_hard_muted:
        msg = f"Opened {app_name}. (Microphone is HARD-MUTED per your command - 0 audio access)."
    elif is_data_hard_cut:
        msg = f"Opened {app_name}. (Data is HARD-CUT per your command - 0 B/s)."
    elif is_ephemeral:
        STATE["kernel_logs"].append(f"[EphemeralSandbox] Mounted tmpfs RAM overlay on /data/data/{app_key}.")
        msg = f"🛡️ Opened {app_name} in Ephemeral RAM Sandbox."
    else:
        msg = f"Opened {app_name}."

    return jsonify({"success": True, "message": msg, "state": STATE})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5077))
    print(f"ZeroOS Simple Android UI Simulator running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
