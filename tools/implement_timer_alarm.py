import os
import re
import shutil

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_py_path = os.path.join(root, 'simulator', 'app.py')

# 1. UPDATE simulator/app.py
with open(app_py_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add helper functions for Timer and Alarm
timer_alarm_helpers = """
    function startEverythingTimer(totalSec, label) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      showToast(`⏱️ Timer started for ${label} (DeskClock countdown running)`);
    }

    function setEverythingAlarm(timeStr) {
      document.getElementById('everythingResultsTray').style.display = 'none';
      document.getElementById('androidSearchInput').value = '';
      showToast(`⏰ Alarm SET for ${timeStr} with Gentle Chime`);
    }
"""

if 'function startEverythingTimer' not in text:
    text = text.replace('function copyEverythingResult(val) {', timer_alarm_helpers + '\n    function copyEverythingResult(val) {')

# Add Timer & Alarm checks in onEverythingBarInput()
timer_alarm_detection = """
      // 0a. TIMER DETECTION (e.g. timer 10 mins, timer 5m, timer 30s, set timer 15 minutes)
      const timerMatch = lower.match(/^(?:set\\s+)?timer(?:\\s+for)?\\s+(\\d+)\\s*(m|min|mins|minute|minutes|s|sec|secs|second|seconds|h|hr|hrs|hour|hours)?$/i);
      if (timerMatch) {
        const qty = parseInt(timerMatch[1], 10);
        const unit = (timerMatch[2] || 'm').toLowerCase();
        let label = `${qty} minute${qty > 1 ? 's' : ''}`;
        let totalSec = qty * 60;
        if (unit.startsWith('s')) {
          label = `${qty} second${qty > 1 ? 's' : ''}`;
          totalSec = qty;
        } else if (unit.startsWith('h')) {
          label = `${qty} hour${qty > 1 ? 's' : ''}`;
          totalSec = qty * 3600;
        }
        cardsHtml += `
          <div class="tray-card">
            <div class="tray-card-left" onclick="startEverythingTimer(${totalSec}, '${label}')">
              <span class="tray-icon" style="background:#f59e0b; color:#fff;">⏱️</span>
              <div>
                <div class="tray-title" style="color:#fbbf24; font-size:1.05rem; font-weight:700;">Timer · ${label}</div>
                <div class="tray-sub">DeskClock Countdown · Tap to start</div>
              </div>
            </div>
            <div class="tray-actions">
              <button class="tray-btn primary" onclick="startEverythingTimer(${totalSec}, '${label}')">▶ Start Timer</button>
            </div>
          </div>
        `;
      }

      // 0b. ALARM DETECTION (e.g. alarm 7am, alarm 6:30 am, alarm 8:00 pm, alarm 7:00)
      const alarmMatch = lower.match(/^(?:set\\s+)?alarm(?:\\s+for)?\\s+(\\d{1,2}(?::\\d{2})?\\s*(?:am|pm)?|\\d{1,2}:\\d{2})$/i);
      if (alarmMatch) {
        const timeStr = alarmMatch[1].toUpperCase();
        cardsHtml += `
          <div class="tray-card">
            <div class="tray-card-left" onclick="setEverythingAlarm('${timeStr}')">
              <span class="tray-icon" style="background:#ef4444; color:#fff;">⏰</span>
              <div>
                <div class="tray-title" style="color:#f87171; font-size:1.05rem; font-weight:700;">Alarm · ${timeStr}</div>
                <div class="tray-sub">DeskClock · Gentle Chime · Tap to set</div>
              </div>
            </div>
            <div class="tray-actions">
              <button class="tray-btn primary" onclick="setEverythingAlarm('${timeStr}')">⏰ Set Alarm</button>
            </div>
          </div>
        `;
      }
"""

if '// 0a. TIMER DETECTION' not in text:
    text = text.replace('// 1. MATH CALCULATION ENGINE', timer_alarm_detection + '\n      // 1. MATH CALCULATION ENGINE')

# Add execution on Enter in executeSearchCommand()
exec_enter_code = """
      // Check direct "timer <duration>"
      const execTimerMatch = lower.match(/^(?:set\\s+)?timer(?:\\s+for)?\\s+(\\d+)\\s*(m|min|mins|minute|minutes|s|sec|secs|second|seconds|h|hr|hrs|hour|hours)?$/i);
      if (execTimerMatch) {
        const qty = parseInt(execTimerMatch[1], 10);
        const unit = (execTimerMatch[2] || 'm').toLowerCase();
        let label = `${qty} minute${qty > 1 ? 's' : ''}`;
        let totalSec = qty * 60;
        if (unit.startsWith('s')) {
          label = `${qty} second${qty > 1 ? 's' : ''}`;
          totalSec = qty;
        } else if (unit.startsWith('h')) {
          label = `${qty} hour${qty > 1 ? 's' : ''}`;
          totalSec = qty * 3600;
        }
        startEverythingTimer(totalSec, label);
        return;
      }

      // Check direct "alarm <time>"
      const execAlarmMatch = lower.match(/^(?:set\\s+)?alarm(?:\\s+for)?\\s+(\\d{1,2}(?::\\d{2})?\\s*(?:am|pm)?|\\d{1,2}:\\d{2})$/i);
      if (execAlarmMatch) {
        const timeStr = execAlarmMatch[1].toUpperCase();
        setEverythingAlarm(timeStr);
        return;
      }
"""

if 'Check direct "timer <duration>"' not in text:
    text = text.replace('// Check direct "call <contact>"', exec_enter_code + '\n      // Check direct "call <contact>"')

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated simulator/app.py with Timer & Alarm in Everything Bar!")
