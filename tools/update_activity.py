import os
import shutil

activity_path = 'app/src/main/java/com/zeroos/launcher/ui/ZeroLauncherActivity.kt'
aosp_activity_path = 'aosp/packages/apps/ZeroLauncher/src/main/java/com/zeroos/launcher/ui/ZeroLauncherActivity.kt'

with open(activity_path, 'r', encoding='utf-8') as f:
    text = f.read()

crlf = '\r\n' in text
lines = text.splitlines()

idx_launch_app = -1
for i, line in enumerate(lines):
    if 'is ZeroCommand.LaunchApp ->' in line:
        idx_launch_app = i
        break

if idx_launch_app != -1 and not any('is ZeroCommand.CallContact' in l for l in lines):
    new_branches = [
        '            is ZeroCommand.CallContact -> {',
        '                systemLog = "📞 Calling ${cmd.target}..."',
        '            }',
        '            is ZeroCommand.MessageContact -> {',
        '                systemLog = "💬 SMS to ${cmd.target}${if (cmd.body != null) ": \\"${cmd.body}\\"" else ""}..."',
        '            }',
        '            is ZeroCommand.ChatContact -> {',
        '                systemLog = "🔒 Opening encrypted ZeroChat with ${cmd.target}..."',
        '            }',
        '            is ZeroCommand.SaveContact -> {',
        '                systemLog = "👤 Contact saved: ${cmd.number}"',
        '            }',
        '            is ZeroCommand.CalculateMath -> {',
        '                systemLog = "🧮 Math: ${cmd.expression}"',
        '            }',
        '            is ZeroCommand.SearchWeb -> {',
        '                systemLog = "🌐 Private search: \\"${cmd.query}\\""',
        '            }',
    ]
    for j, b in enumerate(new_branches):
        lines.insert(idx_launch_app + j, b)

delim = '\r\n' if crlf else '\n'
new_content = delim.join(lines) + delim

with open(activity_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

if os.path.exists(os.path.dirname(aosp_activity_path)):
    shutil.copyfile(activity_path, aosp_activity_path)
    print("Copied updated ZeroLauncherActivity.kt to AOSP tree!")

print("Successfully updated ZeroLauncherActivity.kt!")
