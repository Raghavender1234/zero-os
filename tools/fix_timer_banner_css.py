import os
import shutil

root = r"C:\Users\brred\.gemini\antigravity\scratch\zero_os"
app_py_path = os.path.join(root, 'simulator', 'app.py')

with open(app_py_path, 'r', encoding='utf-8') as f:
    text = f.read()

timer_css = """
    /* ZEROOS ACTIVE LIVE TIMER BANNER */
    .active-timer-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.4);
      border-radius: 14px;
      padding: 8px 14px;
      margin: 0 16px 8px 16px;
      backdrop-filter: blur(16px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.4);
      z-index: 10;
    }
    .active-timer-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .timer-pulse-icon {
      font-size: 1.25rem;
      animation: timerPulse 1.5s infinite ease-in-out;
    }
    @keyframes timerPulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.15); opacity: 0.85; }
    }
    .active-timer-digits {
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.15rem;
      font-weight: 800;
      color: #fbbf24;
      line-height: 1.1;
    }
    .active-timer-sub {
      font-size: 0.72rem;
      color: #94a3b8;
      margin-top: 2px;
    }
    .active-timer-stop-btn {
      background: rgba(239, 68, 68, 0.2);
      border: 1px solid rgba(239, 68, 68, 0.45);
      color: #fca5a5;
      padding: 5px 12px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.75rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .active-timer-stop-btn:hover {
      background: rgba(239, 68, 68, 0.4);
      color: #fff;
    }
"""

if '/* ZEROOS ACTIVE LIVE TIMER BANNER */' not in text:
    text = text.replace('</style>', timer_css + '\n  </style>')

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Injected active timer CSS into simulator/app.py!")
