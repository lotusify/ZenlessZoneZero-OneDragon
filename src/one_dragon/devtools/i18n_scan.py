#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
i18n_scan.py  --  CJK scan of the Qt UI layer.
Emit string literals that contain Chinese characters and are used in real
code (NOT comments, NOT docstrings). Writes JSON + prints a summary.
"""
import os, re, ast, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", ".."))
UI_ROOT = os.path.join(ROOT, "src", "one_dragon_qt")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

def scan_file(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    tree = ast.parse(text)
    hits = {}
    # build lineno -> source line
    lines = text.splitlines()
    # find docstring line numbers (Expr statement whose value is a triple-quoted string)
    docstring_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) \
                and node.value.value.startswith(('"""', "'''")):
            docstring_lines.add(node.value.lineno)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        val = node.value
        if not CJK.search(val) or len(val) < 2:
            continue
        if node.lineno in docstring_lines:
            continue
        hits[node.lineno] = val
    return hits

def main():
    files = []
    for dp, _, fns in os.walk(UI_ROOT):
        for fn in fns:
            if fn.endswith(".py"):
                files.append(os.path.join(dp, fn))
    files.sort()
    all_hits = []
    for f in files:
        for ln, val in scan_file(f).items():
            all_hits.append({"file": f.replace("\\", "/"), "line": ln, "literal": val})
    all_hits.sort(key=lambda x: (x["file"], x["line"]))
    # dedupe identical (file,line,literal)
    seen = set()
    uniq = []
    for h in all_hits:
        k = (h["file"], h["line"], h["literal"])
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    with open(os.path.join(ROOT, "i18n_candidates.json"), "w", encoding="utf-8") as fh:
        json.dump({"count": len(uniq), "items": uniq}, fh, ensure_ascii=False, indent=2)
    print(f"=== real CJK string literals in UI layer: {len(uniq)} ===")
    print("file | line | literal")
    print("-" * 110)
    for h in uniq:
        print(f"{h['file']} | {h['line']} | {h['literal']}")
    print(f"\n[written] i18n_candidates.json")

if __name__ == "__main__":
    main()
