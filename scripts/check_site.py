#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP Hub 站点完整性检查器（本地 CI 共用）
  1. 校验所有 HTML 内部链接（href/src/url()）指向真实存在的本地文件
  2. 校验 sitemap.xml 中每个 <loc> 对应的本地文件存在
  3. 报告未被任何页面引用的图片资源（供清理）
  4. 检测仓库中不应存在的符号链接

用法:
  python3 scripts/check_site.py             # 完整检查
  python3 scripts/check_site.py --unref-images-only
退出码: 0=通过, 1=发现错误
"""
import os
import re
import sys
import argparse
import itertools
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_PREFIXES = ("http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:", "#", "ftp://")
RE_CSS_URL = re.compile(r"url\(\s*([^\"'\)]+)\)")


class RefParser(HTMLParser):
    """只提取真实 HTML 标签里的 href/src，代码块/模板字符串不算数。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = set()
        self._style = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.refs.add(v)
        if tag == "style":
            self._style.append(True)

    def handle_endtag(self, tag):
        if tag == "style" and self._style:
            self._style.pop()

    def handle_data(self, data):
        if self._style:
            for m in RE_CSS_URL.finditer(data):
                self.refs.add(m.group(1).strip())


def extract_refs(path):
    """返回 (真实引用集合, 盲扫引用集合)。html 用标签解析，js/css 用正则。"""
    txt = open(path, encoding="utf-8", errors="ignore").read()
    if path.endswith((".css", ".js")):
        refs = set()
        for m in RE_CSS_URL.finditer(txt):
            refs.add(m.group(1).strip())
        return refs
    p = RefParser()
    p.feed(txt)
    return p.refs


def clean_ref(ref):
    if not ref:
        return None
    ref = ref.strip()
    if not ref or ref.startswith(SKIP_PREFIXES) or "${" in ref:
        return None
    ref = ref.split("?")[0].split("#")[0].strip()
    return ref or None


def walk_files(site_dir, exts):
    for root, dirs, files in os.walk(site_dir):
        for f in sorted(files):
            if f.endswith(exts):
                yield os.path.join(root, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unref-images-only", action="store_true")
    args = parser.parse_args()

    site = os.path.join(ROOT, "tpvibe")
    if not os.path.isdir(site):
        print(f"❌ 找不到站点目录: {site}")
        sys.exit(1)

    # ---- 符号链接检测 ----
    symlinks = []
    if not args.unref_images_only:
        for root, dirs, files in os.walk(ROOT):
            if ".git" in root:
                continue
            for name in files + dirs:
                p = os.path.join(root, name)
                if os.path.islink(p):
                    symlinks.append(p)
        if symlinks:
            print(f"❌ 发现 {len(symlinks)} 个符号链接（不应提交到仓库）:")
            for s in symlinks:
                print("   ", os.path.relpath(s, ROOT))
            print()
            sys.exit(1)

    # ---- 收集页面引用 ----
    referenced = set()
    for p in itertools.chain(walk_files(site, (".html", ".css", ".js", ".xml", ".md")), walk_files(ROOT, (".html", ".xml"))):
        if os.path.basename(p) == "check_site.py":
            continue
        base_dir = os.path.dirname(p)
        for raw in extract_refs(p):
            ref = clean_ref(raw)
            if not ref:
                continue
            cand = None
            if ref.startswith("/"):
                cand = os.path.normpath(os.path.join(ROOT, ref.lstrip("/")))
            else:
                cand = os.path.normpath(os.path.join(base_dir, ref))
            if os.path.isfile(cand):
                referenced.add(os.path.relpath(cand, ROOT).replace(os.sep, "/"))

    # ---- 断链检查 ----
    broken = set()
    if not args.unref_images_only:
        for p in itertools.chain(walk_files(site, (".html", ".css", ".js", ".xml", ".md")), walk_files(ROOT, (".html", ".xml"))):
            if os.path.basename(p) == "check_site.py":
                continue
            base_dir = os.path.dirname(p)
            for raw in extract_refs(p):
                ref = clean_ref(raw)
                if not ref:
                    continue
                cand = os.path.normpath(os.path.join(base_dir, ref)) if not ref.startswith("/") else os.path.normpath(os.path.join(ROOT, ref.lstrip("/")))
                if not os.path.exists(cand):
                    if ref.endswith((".html", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js", ".xml", ".ico", ".json", ".txt")):
                        broken.add((ref, os.path.relpath(p, ROOT)))
        if broken:
            print(f"❌ 发现 {len(broken)} 个断链:")
            for ref, src in sorted(broken):
                print(f"   {ref}  ← {src}")
            print()

    # ---- sitemap 校验 ----
    sitemap_path = os.path.join(ROOT, "sitemap.xml")
    sm_errors = 0
    if not args.unref_images_only and os.path.isfile(sitemap_path):
        sm_txt = open(sitemap_path, encoding="utf-8", errors="ignore").read()
        locs = re.findall(r"<loc>([^<]+)</loc>", sm_txt)
        for loc in locs:
            if not re.match(r"^https?://", loc):
                sm_errors += 1
                print(f"❌ sitemap 含非法 URL: {loc}")
                continue
            path_part = re.sub(r"^https?://[^/]+", "", loc).lstrip("/")
            if not path_part:
                continue
            local = os.path.join(ROOT, path_part)
            exists = os.path.isfile(local) or (
                os.path.isdir(local) and os.path.isfile(os.path.join(local, "index.html"))
            )
            if exists:
                continue
            sm_errors += 1
            print(f"❌ sitemap 指向不存在的文件: {loc}")

    # ---- 未引用图片报告 ----
    unref = []
    for p in walk_files(os.path.join(site, "images"), (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        if rel not in referenced:
            unref.append((os.path.getsize(p), rel))
    unref.sort(reverse=True)
    total = sum(s for s, _ in unref) / 1024 / 1024
    print(f"ℹ️  未引用图片: {len(unref)} 个, 共 {total:.1f} MB")
    for s, r in unref[:20]:
        print(f"   {s / 1024:8.0f}KB  {r}")

    failures = len(broken) + sm_errors + (1 if symlinks else 0)
    print()
    if failures:
        print(f"❌ 检查失败: {failures} 类问题")
        sys.exit(1)
    print("✅ 检查通过")


if __name__ == "__main__":
    main()