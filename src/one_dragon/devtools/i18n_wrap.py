#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
i18n_wrap.py
Wrap hardcoded Chinese UI string literals with gt(...), preserving exact text
(f-strings, concatenations, interpolations). Also emits the list of literals to
add to assets/text/ui/en.po (msgstr left empty for manual translation).

WRAP_SCOPE: list of file paths to process (use "" = all .py under one_dragon_qt)
DRY_RUN:     if True, do not modify files (writes modified copies + report only)
OUT_DIR:     where modified copies go (for review)
REPORT:      json report of unique literals + per-file counts
"""
import ast, json, os, sys, re

UI_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "..", "..", "..", "src", "one_dragon_qt"))
IMPORT_LINE = "from one_dragon.utils.i18_utils import gt"
IMPORT_FROM = "from one_dragon.utils.i18_utils import gt"

def collect_files():
    scope = os.environ.get("WRAP_SCOPE", "").strip()
    if scope:
        return [scope]
    out = []
    for dp, _, fns in os.walk(UI_ROOT):
        for fn in fns:
            if fn.endswith(".py"):
                out.append(os.path.join(dp, fn))
    return sorted(out)

def docstring_lineno(tree, source):
    """Line numbers of docstring Expr statements (detected from source text, since
    ast strips the triple-quote delimiters from the parsed string value)."""
    lines = source.splitlines()
    ds = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            # a docstring is a bare string statement delimited by triple quotes
            lo, hi = node.value.lineno - 1, node.value.end_lineno
            block = "\n".join(lines[lo:hi]) if hi else lines[lo]
            if '"""' in block or "'''" in block:
                ds.add(node.value.lineno)
    return ds

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

def plan(source, tree):
    """Return list of (lineno, segment, literal) to wrap, skipping gt-args/docstrings/comments."""
    skip_gt = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'gt':
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    skip_gt.add(a)
    ds = docstring_lineno(tree, source)
    lines = source.splitlines()
    to_wrap = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        val = node.value
        if not val or len(val) < 2 or not CJK_RE.search(val):
            continue
        if node.lineno in ds:
            continue
        if node in skip_gt:
            continue
        # skip comment lines
        lno = node.lineno - 1
        if 0 <= lno < len(lines) and lines[lno].strip().startswith(("#", "//")):
            continue
        seg = ast.get_source_segment(source, node)
        if seg is None:
            continue
        to_wrap.append((node.lineno, seg, val))
    to_wrap.sort(reverse=True)
    return to_wrap

def ensure_import(text, tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'one_dragon.utils.i18_utils' \
                and any((isinstance(a, ast.alias) and a.name == 'gt') for a in node.names):
            return text
    lines = text.splitlines(keepends=True)
    # skip leading coding / shebang lines
    i = 0
    while i < len(lines):
        s = lines[i].rstrip("\n")
        if s.startswith("#") or s.startswith("﻿"):
            i += 1
            continue
        break
    # find first import/from to insert before, but always AFTER any __future__ import
    insert_at = i
    for j in range(i, len(lines)):
        st = lines[j].strip()
        if st.startswith("from __future__") or st.startswith("import __future__"):
            continue
        if st.startswith("import ") or st.startswith("from "):
            insert_at = j
            break
    lines.insert(insert_at, IMPORT_FROM + "\n")
    return "".join(lines)

def wrap_source(text, to_wrap):
    src = text
    for lineno, seg, val in to_wrap:
        # replace the segment text with gt(<seg>)
        src = src.replace(seg, "gt(" + seg + ")", 1)
    return src

def main():
    dry = os.environ.get("DRY_RUN", "false").lower() == "true"
    out_dir = os.environ.get("OUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    files = collect_files()
    report = {"files": [], "unique_literals": []}
    all_literals = {}
    for f in files:
        orig = open(f, encoding="utf-8").read()
        tree = ast.parse(orig)
        to_wrap = plan(orig, tree)
        if not to_wrap:
            continue
        newtext = wrap_source(orig, to_wrap)
        newtext = ensure_import(newtext, tree)
        # collect unique literals (dedupe)
        for _, seg, val in to_wrap:
            all_literals[val] = (f, seg)
        if not dry:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(newtext)
        else:
            with open(os.path.join(out_dir, os.path.basename(f)), "w", encoding="utf-8") as fh:
                fh.write(newtext)
        report["files"].append({"file": f, "wrapped_count": len(to_wrap)})
    # build po entries
    po_entries = []
    for lit, (f, seg) in all_literals.items():
        # escape for po msgid
        import re
        lit_esc = re.escape(lit)
        po_entries.append({"msgid": lit, "file": f, "line_in_file": seg.count("\n") + 1})
    report["unique_literals"] = po_entries
    with open(os.path.join(out_dir, "i18n_po_entries.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f"[i18n_wrap] files with CJK literals: {len(report['files'])}")
    print(f"[i18n_wrap] total wrapped (with dups): {sum(x['wrapped_count'] for x in report['files'])}")
    print(f"[i18n_wrap] unique literals for en.po: {len(report['unique_literals'])}")
    print(f"[i18n_wrap] DRY_RUN={'yes' if dry else 'NO - files modified'}; OUT_DIR={out_dir}")
    print(f"[i18n_wrap] report -> {os.path.join(out_dir, 'i18n_po_entries.json')}")

if __name__ == "__main__":
    main()
