#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TPvibe 爬取脚本 v1
从 vibevibe.cn 抓取各章节正文 + 图片，输出为易移植的中间格式（JSON + 本地图片）。

输出结构:
  tpvibe/_crawl/<slug>/
    meta.json          # {title, source_url, local_file, images:[...]}
    content.html       # 清洗后的正文 HTML（图片已改为相对路径）
    images/            # 下载到本地的真图片

用法:
  python3 crawl_tpvibe.py            # 爬全部 37 章
  python3 crawl_tpvibe.py --only Basic/lecture-1.html,Advanced/ch01.html
"""
import os, re, json, sys, argparse, urllib.request, urllib.parse, time

ROOT = os.path.dirname(os.path.abspath(__file__))          # .../scripts
SITE = os.path.normpath(os.path.join(ROOT, "..", "tpvibe"))
OUT  = os.path.join(SITE, "_crawl")
UA   = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# 本地文件 -> 源 URL 映射（域名已统一用 vibevibe.cn，运行期替换为 vibevibe.cn）
MAPPING = [
    ("index.html", "https://www.vibevibe.cn/deployment"),
    ("Advanced/ch06.html", "https://www.vibevibe.cn/Advanced/06-data-persistence-database"),
    ("Advanced/ch10.html", "https://www.vibevibe.cn/Advanced/10-localhost-public-access"),
    ("Advanced/index.html", "https://www.vibevibe.cn/Advanced"),
    ("Advanced/ch11.html", "https://www.vibevibe.cn/Advanced/11-git-collaboration"),
    ("Advanced/ch07.html", "https://www.vibevibe.cn/Advanced/07-backend-api"),
    ("Advanced/ch16.html", "https://www.vibevibe.cn/Advanced/16-user-feedback-iteration"),
    ("Advanced/ch01.html", "https://www.vibevibe.cn/Advanced/01-environment-setup"),
    ("Advanced/ch14.html", "https://www.vibevibe.cn/Advanced/14-vps-ops-deploy"),
    ("Advanced/next-level.html", "https://www.vibevibe.cn/Advanced/99-next-level"),
    ("Advanced/ch02.html", "https://www.vibevibe.cn/Advanced/02-ai-tuning-guide"),
    ("Advanced/ch03.html", "https://www.vibevibe.cn/Advanced/03-prd-doc-driven"),
    ("Advanced/ch15.html", "https://www.vibevibe.cn/Advanced/15-seo-analytics"),
    ("Advanced/ch12.html", "https://www.vibevibe.cn/Advanced/12-serverless-deploy-cicd"),
    ("Advanced/ch04.html", "https://www.vibevibe.cn/Advanced/04-dev-fundamentals"),
    ("Advanced/ch08.html", "https://www.vibevibe.cn/Advanced/08-auth-security"),
    ("Advanced/ch09.html", "https://www.vibevibe.cn/Advanced/09-testing-automation"),
    ("Advanced/ch05.html", "https://www.vibevibe.cn/Advanced/05-ui-ux"),
    ("Advanced/ch13.html", "https://www.vibevibe.cn/Advanced/13-domain-dns"),
    ("Articles/index.html", "https://www.vibevibe.cn/Articles"),
    ("Articles/architecture.html", "https://www.vibevibe.cn/Articles/02-technical-architecture"),
    ("Articles/core-concepts.html", "https://www.vibevibe.cn/Articles/01-core-concepts"),
    ("Articles/engineering.html", "https://www.vibevibe.cn/Articles/04-engineering-practices"),
    ("Articles/security.html", "https://www.vibevibe.cn/Articles/05-security-compliance"),
    ("Articles/tools.html", "https://www.vibevibe.cn/Articles/03-toolchain-frameworks"),
    ("Articles/business.html", "https://www.vibevibe.cn/Articles/06-business-trends"),
    ("Basic/conclusion.html", "https://www.vibevibe.cn/Basic/100-epilogue"),
    ("Basic/lecture-1.html", "https://www.vibevibe.cn/Basic/00-preface"),
    ("Basic/index.html", "https://www.vibevibe.cn/Basic"),
    ("Basic/appendix-a.html", "https://www.vibevibe.cn/Basic/05-advanced"),
    ("Basic/lecture-4.html", "https://www.vibevibe.cn/Basic/03-technique"),
    ("Basic/appendix-c.html", "https://www.vibevibe.cn/Basic/99-appendix"),
    ("Basic/appendix-b.html", "https://www.vibevibe.cn/Basic/06-launch"),
    ("Basic/lecture-5.html", "https://www.vibevibe.cn/Basic/04-practice-0-to-1"),
    ("Basic/lecture-2.html", "https://www.vibevibe.cn/Basic/01-awakening"),
    ("Basic/lecture-3.html", "https://www.vibevibe.cn/Basic/02-mindset"),
    ("Practice/index.html", "https://www.vibevibe.cn/Practice"),
]

def fix_domain(u):
    return u.replace("tpvibe.cn", "vibevibe.cn")

def slug_of(local_file):
    # Advanced/ch01.html -> Advanced_ch01
    base = local_file.replace("/", "_").replace(".html", "")
    return base

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)

def clean_main(html):
    """提取 <main class="main"> 正文，去掉导航/侧栏/埋点/品牌脚本。"""
    m = re.search(r'<main class="main".*?</main>', html, re.S)
    if not m:
        # 贪婪退路：取第一个 <main 到文档最后一个 </main>
        s = html.find('<main class="main"')
        e = html.rfind('</main>')
        if s != -1 and e != -1:
            m = type('M', (), {'group': lambda self: html[s:e+7]})()
        else:
            m = re.search(r'<article.*?</article>', html, re.S)
    if not m:
        return None
    body = m.group(0)
    # 去掉内联脚本/样式
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
    # 去掉侧栏目录树（class 含 tree/aside）
    body = re.sub(r'<aside.*?</aside>', '', body, flags=re.S)
    # 去掉空白零宽字符
    body = body.replace('\u200b', '').replace('\u00a0', ' ')
    return body

def extract_title(html):
    m = re.search(r'<title>([^<]*?)\s*\|\s*VibeVibe\s*</title>', html)
    if m: return m.group(1).strip()
    m = re.search(r'<title>([^<]*)</title>', html)
    return m.group(1).strip() if m else ""

def crawl_one(local_file, source_url):
    slug = slug_of(local_file)
    out_dir = os.path.join(OUT, slug)
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    url = fix_domain(source_url).rstrip("/")
    print(f"  ↳ 抓取 {url}")
    try:
        raw = fetch(url)
    except Exception as e:
        print(f"    ✗ 失败: {e}")
        return None

    title = extract_title(raw)
    body = clean_main(raw)
    if not body:
        print(f"    ✗ 未找到正文容器")
        return None

    # 下载图片并改写路径
    images = []
    base_url = url
    def repl(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src: return tag
        src_url = src.group(1)
        if src_url.startswith("//"):
            src_url = "https:" + src_url
        elif src_url.startswith("/"):
            src_url = "https://www.vibevibe.cn" + src_url
        elif not src_url.startswith("http"):
            src_url = urllib.parse.urljoin(base_url + "/", src_url)
        # 跳过 logo 等品牌图
        if "logo" in src_url.lower() or "badge" in src_url.lower():
            return ""  # 直接移除品牌图
        fname = re.sub(r'[^\w\.-]', '_', src_url.split("/")[-1]) or "img.png"
        if not re.search(r'\.(png|jpe?g|webp|gif|svg)$', fname, re.I):
            fname += ".png"
        try:
            sz = download(src_url, os.path.join(img_dir, fname))
            images.append({"src": src_url, "file": f"images/{fname}", "bytes": sz})
            return tag.replace(src.group(1), f"images/{fname}")
        except Exception as e:
            print(f"    ⚠ 图下载失败 {src_url}: {e}")
            return tag  # 保留原标签但外链，后续人工处理
    body = re.sub(r'<img[^>]*>', repl, body)

    # 写出中间格式
    meta = {
        "title": title,
        "source_url": url,
        "local_file": local_file,
        "images": images,
        "body_len": len(body),
    }
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "content.html"), "w", encoding="utf-8") as f:
        f.write(body)

    print(f"    ✓ 标题:{title[:30]} | 正文 {len(body)} 字符 | 图片 {len(images)} 张")

    # 发现并爬取子页 ./xx.html（源站每章拆成多个子页）
    subs = discover_subs(raw, url)
    sub_meta = []
    for sub_url, sub_slug in subs:
        sm = crawl_sub(sub_url, sub_slug, out_dir, url)
        if sm:
            sub_meta.append(sm)
            time.sleep(0.3)
    meta["subs"] = sub_meta
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return meta


def discover_subs(html, base_url):
    """从章节页找出 ./xx.html 子页链接（排除 ./# 锚点）。"""
    found = []
    seen = set()
    for href in re.findall(r'href="(\./[^"#?]+)"', html):
        # 去掉可能的尾部 /
        h = href[2:].lstrip("/")
        if not re.search(r'\.html?$', h, re.I):
            continue
        full = urllib.parse.urljoin(base_url + "/", h)
        key = h
        if key in seen:
            continue
        seen.add(key)
        # slug = 文件名去扩展
        sub_slug = re.sub(r'\.html?$', '', h, flags=re.I)
        found.append((full, sub_slug))
    return found


def crawl_sub(sub_url, sub_slug, parent_dir, base_url):
    """爬取单个子页，存到 parent_dir/subs/<sub_slug>/。"""
    out_dir = os.path.join(parent_dir, "subs", sub_slug)
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    try:
        raw = fetch(sub_url)
    except Exception as e:
        print(f"      ✗ 子页失败 {sub_url}: {e}")
        return None
    title = extract_title(raw)
    body = clean_main(raw)
    if not body:
        return None
    images = []
    def repl(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src: return tag
        src_url = src.group(1)
        if src_url.startswith("//"):
            src_url = "https:" + src_url
        elif src_url.startswith("/"):
            src_url = "https://www.vibevibe.cn" + src_url
        elif not src_url.startswith("http"):
            src_url = urllib.parse.urljoin(sub_url + "/", src_url)
        if "logo" in src_url.lower() or "badge" in src_url.lower():
            return ""
        fname = re.sub(r'[^\w\.-]', '_', src_url.split("/")[-1]) or "img.png"
        if not re.search(r'\.(png|jpe?g|webp|gif|svg)$', fname, re.I):
            fname += ".png"
        try:
            sz = download(src_url, os.path.join(img_dir, fname))
            images.append({"file": f"images/{fname}", "bytes": sz})
            return tag.replace(src.group(1), f"images/{fname}")
        except Exception:
            return tag
    body = re.sub(r'<img[^>]*>', repl, body)
    meta = {"title": title, "source_url": sub_url, "slug": sub_slug,
            "images": images, "body_len": len(body)}
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "content.html"), "w", encoding="utf-8") as f:
        f.write(body)
    print(f"      ↳ 子页 {sub_slug}: 正文 {len(body)} 字, 图 {len(images)}")
    return meta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="逗号分隔的本地文件白名单，如 Basic/lecture-1.html")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    os.makedirs(OUT, exist_ok=True)
    targets = [(lf, u) for lf, u in MAPPING if (only is None or lf in only)]
    print(f"待爬章节: {len(targets)}")
    ok = 0
    for lf, u in targets:
        print(f"[ {lf} ]")
        if crawl_one(lf, u):
            ok += 1
        time.sleep(0.15)  # 礼貌限速
    print(f"\n完成: {ok}/{len(targets)} 成功。中间结果在 {OUT}")

if __name__ == "__main__":
    main()
