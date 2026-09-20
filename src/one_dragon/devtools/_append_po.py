#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, os, re

# run from the project folder; assets/ resolves relative to cwd
report_path = os.path.join(os.environ["TEMP"], "i18n_review", "i18n_po_entries.json")
d = json.load(open(report_path, encoding="utf-8"))
new_literals = [x["msgid"] for x in d["unique_literals"]]

txt = open("assets/text/ui/en.po", encoding="utf-8").read()
existing = set()
for line in txt.splitlines():
    m = re.match(r'mmsgid "((?:[^"\\]|\\.)*)"', line)
    if m:
        existing.add(m.group(1))
to_add = [s for s in new_literals if s not in existing]
print(f"new literals: {len(new_literals)}, already in en.po: {len(new_literals)-len(to_add)}, to add: {len(to_add)}")

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

block = ["\n",
         "# ====== NEW ENTRIES — NEED MANUAL TRANSLATION (added by i18n_wrap, 2025) ======",
         "# 这些是代码中硬编码的中文 UI 字符串，msgstr 留空，请手动填入英文。",
         "# These are hardcoded Chinese UI strings; msgstr is empty. Please fill in English."]
for s in to_add:
    block.append(f'msgid "{esc(s)}"')
    block.append('msgstr ""')
    block.append('# type: interface')
    block.append("")

with open("assets/text/ui/en.po", "w", encoding="utf-8") as fh:
    fh.write(txt + "\n".join(block))
print(f"appended {len(to_add)} entries")
