import os
import shutil

parser_path = 'app/src/main/java/com/zeroos/launcher/core/CommandParser.kt'
aosp_parser_path = 'aosp/packages/apps/ZeroLauncher/src/main/java/com/zeroos/launcher/core/CommandParser.kt'

with open(parser_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize line breaks for matching
crlf = '\r\n' in text
lines = text.splitlines()

# 1. Update ZeroCommand data classes
idx_ephemeral = -1
for i, line in enumerate(lines):
    if 'data class LaunchEphemeralApp' in line:
        idx_ephemeral = i
        break

if idx_ephemeral != -1 and not any('data class CallContact' in l for l in lines):
    new_classes = [
        '    data class CallContact(val target: String) : ZeroCommand()',
        '    data class MessageContact(val target: String, val body: String? = null) : ZeroCommand()',
        '    data class ChatContact(val target: String) : ZeroCommand()',
        '    data class SaveContact(val number: String) : ZeroCommand()',
        '    data class CalculateMath(val expression: String) : ZeroCommand()',
        '    data class SearchWeb(val query: String) : ZeroCommand()',
    ]
    for j, nc in enumerate(new_classes):
        lines.insert(idx_ephemeral + 1 + j, nc)

# 2. Add Everything Bar parsing rules before FALLBACK
idx_fallback = -1
for i, line in enumerate(lines):
    if '// 12. FALLBACK: APP LAUNCHER' in line:
        idx_fallback = i
        break

if idx_fallback != -1 and not any('EVERYTHING BAR: CALL' in l for l in lines):
    rules = [
        '        // EVERYTHING BAR: CALL / DIAL',
        '        if (lower.startsWith("call ") || lower.startsWith("dial ")) {',
        '            val target = text.replace(Regex("^(call|dial)\\\\s+", RegexOption.IGNORE_CASE), "").trim()',
        '            if (target.isNotEmpty()) return ZeroCommand.CallContact(target)',
        '        }',
        '',
        '        // EVERYTHING BAR: MESSAGE / SMS / TEXT',
        '        if (lower.startsWith("message ") || lower.startsWith("text ") || lower.startsWith("msg ")) {',
        '            val remainder = text.replace(Regex("^(message|text|msg)\\\\s+", RegexOption.IGNORE_CASE), "").trim()',
        '            val spaceIdx = remainder.indexOf(\' \')',
        '            return if (spaceIdx != -1) {',
        '                ZeroCommand.MessageContact(remainder.substring(0, spaceIdx).trim(), remainder.substring(spaceIdx + 1).trim())',
        '            } else {',
        '                ZeroCommand.MessageContact(remainder, null)',
        '            }',
        '        }',
        '',
        '        // EVERYTHING BAR: ENCRYPTED CHAT (ZEROCHAT)',
        '        if (lower.startsWith("chat ")) {',
        '            val target = text.replace(Regex("^chat\\\\s+", RegexOption.IGNORE_CASE), "").trim()',
        '            if (target.isNotEmpty()) return ZeroCommand.ChatContact(target)',
        '        }',
        '',
        '        // EVERYTHING BAR: ADD / SAVE CONTACT',
        '        if (lower.startsWith("add contact ") || lower.startsWith("save contact ") || lower.startsWith("save ")) {',
        '            val num = text.replace(Regex("^(add contact|save contact|save)\\\\s+", RegexOption.IGNORE_CASE), "").trim()',
        '            if (num.isNotEmpty()) return ZeroCommand.SaveContact(num)',
        '        }',
        '',
        '        // EVERYTHING BAR: WEB SEARCH',
        '        if (lower.startsWith("search ") || lower.startsWith("google ") || lower.startsWith("ddg ")) {',
        '            val query = text.replace(Regex("^(search|google|ddg)\\\\s+", RegexOption.IGNORE_CASE), "").trim()',
        '            if (query.isNotEmpty()) return ZeroCommand.SearchWeb(query)',
        '        }',
        '',
        '        // EVERYTHING BAR: DIRECT MATH EXPRESSIONS (e.g. 245 * 18, 15% of 850, 100 / 4)',
        '        if (lower.matches(Regex("^[0-9+\\\\-*/().\\\\s^%]+$")) && lower.any { it in "+-*/%^" }) {',
        '            return ZeroCommand.CalculateMath(text)',
        '        }',
        '        if (lower.matches(Regex("^[0-9.]+\\\\s*%\\\\s*(?:of)?\\\\s*[0-9.]+$"))) {',
        '            return ZeroCommand.CalculateMath(text)',
        '        }',
        '',
    ]
    for j, r in enumerate(rules):
        lines.insert(idx_fallback + j, r)

delim = '\r\n' if crlf else '\n'
new_content = delim.join(lines) + delim

with open(parser_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

if os.path.exists(os.path.dirname(aosp_parser_path)):
    shutil.copyfile(parser_path, aosp_parser_path)
    print("Copied updated CommandParser.kt to AOSP tree!")

print("Successfully updated CommandParser.kt!")
