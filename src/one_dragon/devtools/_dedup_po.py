#!/usr/bin/env python
# -*- coding: utf-8 -*-
import polib, os

os.chdir(os.getcwd())
po = polib.pofile('assets/text/ui/en.po')

first_seen = {}
kept = []
for e in po:
    if e.msgid in first_seen:
        continue
    first_seen[e.msgid] = e.linenum
    kept.append(e)

print(f"before: {len(list(po))} entries, after dedup: {len(kept)} (removed {len(list(po))-len(kept)})")

newpo = polib.POFile()
for e in kept:
    newpo.append(e)
newpo.save('assets/text/ui/en.po')

# verify
final = polib.pofile('assets/text/ui/en.po')
ids = [e.msgid for e in final]
from collections import Counter
dups = {k: v for k, v in Counter(ids).items() if v > 1}
print(f"final entries: {len(ids)}, remaining duplicates: {len(dups)}")
