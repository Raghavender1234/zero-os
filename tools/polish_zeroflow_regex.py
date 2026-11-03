import os
import re

root = r"C:\Users\brred\.gemini\antigravity\scratch\zero_os"
app_py_path = os.path.join(root, 'simulator', 'app.py')

with open(app_py_path, 'r', encoding='utf-8') as f:
    text = f.read()

polished_fn = r"""    function parseZeroFlowInput(raw) {
      const clean = raw.replace(/^(auto:|routine:|when|if)\s*/i, '').trim();
      let trigger = "Smart Context";
      let actions = [];

      if (/\bthen\b/i.test(clean)) {
        const parts = clean.split(/\bthen\b/i);
        trigger = parts[0].trim();
        actions = parts[1].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
      } else if (/^(?:daily\s+)?at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?/i.test(clean)) {
        const m = clean.match(/^((?:daily\s+)?at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(.*)$/i);
        if (m) {
          trigger = m[1].replace(/^at/i, 'Daily at');
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else if (/^battery/i.test(clean)) {
        const m = clean.match(/^(battery\s*(?:<|<=|below)\s*\d+%?)\s+(.*)$/i);
        if (m) {
          trigger = m[1].replace(/</, 'below ');
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else if (/^wifi/i.test(clean)) {
        const m = clean.match(/^(wifi\s+[a-zA-Z0-9_-]+)\s+(.*)$/i);
        if (m) {
          trigger = "Connected to " + m[1];
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else if (/^bluetooth/i.test(clean)) {
        const m = clean.match(/^(bluetooth\s+[a-zA-Z0-9_-]+)\s+(.*)$/i);
        if (m) {
          trigger = "Connected to " + m[1];
          actions = m[2].split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
        }
      } else {
        trigger = "Smart Trigger";
        actions = clean.split(/[,&]|\band\b/i).map(s => s.trim()).filter(Boolean);
      }

      if (actions.length === 0) actions = ["Execute Action"];

      // Capitalize actions nicely
      const cleanActions = actions.map(a => {
        let low = a.toLowerCase();
        if (low.includes('grayscale')) return 'Grayscale ON';
        if (low.includes('silent')) return 'Sound: Silent';
        if (low.includes('vibrate')) return 'Sound: Vibrate';
        if (low.includes('dia')) return 'DIA Mode (1Hz OLED)';
        if (low.includes('maps')) return 'Launch ZeroMaps';
        if (low.includes('dnd')) return 'DND Active';
        if (low.includes('airgap')) return 'AirGap Social Telemetry';
        return a.charAt(0).toUpperCase() + a.slice(1);
      });

      return { trigger, actions: cleanActions, name: `⚡ Routine: ${trigger}` };
    }"""

text = re.sub(r'function parseZeroFlowInput\(raw\)\s*\{[\s\S]*?return\s*\{\s*trigger,\s*actions,\s*name:\s*`⚡ Routine:\s*\$\{trigger\}`\s*\};\s*\}', lambda m: polished_fn, text)

with open(app_py_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Polished parseZeroFlowInput regex successfully!")
