import os
import shutil

parser_path = 'app/src/main/java/com/zeroos/launcher/core/CommandParser.kt'
aosp_parser_path = 'aosp/packages/apps/ZeroLauncher/src/main/java/com/zeroos/launcher/core/CommandParser.kt'
activity_path = 'app/src/main/java/com/zeroos/launcher/ui/ZeroLauncherActivity.kt'
aosp_activity_path = 'aosp/packages/apps/ZeroLauncher/src/main/java/com/zeroos/launcher/ui/ZeroLauncherActivity.kt'

# 1. Update CommandParser.kt
with open(parser_path, 'r', encoding='utf-8') as f:
    text = f.read()

data_classes = """    data class SetTimer(val durationMinutes: Int, val raw: String) : ZeroCommand()
    data class SetAlarm(val timeString: String) : ZeroCommand()
"""

if 'data class SetTimer' not in text:
    text = text.replace('    data class SearchWeb(val query: String) : ZeroCommand()\n',
                        '    data class SearchWeb(val query: String) : ZeroCommand()\n' + data_classes)

parsing_rules = """
        // EVERYTHING BAR: TIMER
        if (lower.startsWith("timer ") || lower.startsWith("set timer ")) {
            val query = text.replace(Regex("^(set\\\\s+)?timer(\\\\s+for)?\\\\s*", RegexOption.IGNORE_CASE), "").trim()
            val numMatch = Regex("(\\\\d+)").find(query)
            val minutes = numMatch?.value?.toIntOrNull() ?: 5
            return ZeroCommand.SetTimer(minutes, query)
        }

        // EVERYTHING BAR: ALARM
        if (lower.startsWith("alarm ") || lower.startsWith("set alarm ")) {
            val query = text.replace(Regex("^(set\\\\s+)?alarm(\\\\s+for)?\\\\s*", RegexOption.IGNORE_CASE), "").trim()
            return ZeroCommand.SetAlarm(query)
        }
"""

if '// EVERYTHING BAR: TIMER' not in text:
    text = text.replace('        // EVERYTHING BAR: CALL / DIAL', parsing_rules + '\n        // EVERYTHING BAR: CALL / DIAL')

with open(parser_path, 'w', encoding='utf-8') as f:
    f.write(text)

shutil.copyfile(parser_path, aosp_parser_path)
print("Updated CommandParser.kt in both app and AOSP!")

# 2. Update ZeroLauncherActivity.kt
with open(activity_path, 'r', encoding='utf-8') as f:
    act_text = f.read()

activity_branches = """            is ZeroCommand.SetTimer -> {
                systemLog = "⏱️ Timer set for ${cmd.durationMinutes} minutes (DeskClock)."
            }
            is ZeroCommand.SetAlarm -> {
                systemLog = "⏰ Alarm set for ${cmd.timeString} (DeskClock)."
            }
"""

if 'is ZeroCommand.SetTimer ->' not in act_text:
    act_text = act_text.replace('            is ZeroCommand.SearchWeb -> {',
                                activity_branches + '            is ZeroCommand.SearchWeb -> {')

with open(activity_path, 'w', encoding='utf-8') as f:
    f.write(act_text)

shutil.copyfile(activity_path, aosp_activity_path)
print("Updated ZeroLauncherActivity.kt in both app and AOSP!")
