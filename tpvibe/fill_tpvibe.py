#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TPvibe 填入+改造脚本 v1
读取 _crawl/<slug>/content.html，清洗为正文，填入现有 TPvibe 章节骨架的
<div class="content reveal"> 区域，并做 TP 视角改造。

改造规则:
  - 剥掉外层 <h1>（骨架已有 .page-title）
  - 清理 header-anchor 锚点链接（保留标题文字）
  - 图片相对路径 images/x.png -> ../images/<slug>/x.png
  - 把内部小节链接 ./x.html 转为纯文本（子小节未单独爬取）
  - TP 视角术语替换（去掉 vibevibe 品牌语气 / 工具名泛化）
  - 副本图片到正式 images/<slug>/

用法:
  python3 fill_tpvibe.py --only Basic/lecture-2.html
  python3 fill_tpvibe.py            # 全部
"""
import os, re, json, argparse, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
CRAWL = os.path.join(ROOT, "_crawl")
IMG_DEST = os.path.join(ROOT, "images")

SLUG_FOR = {
    "index.html": "index",
    "Advanced/ch06.html": "Advanced_ch06",
    "Advanced/ch10.html": "Advanced_ch10",
    "Advanced/index.html": "Advanced_index",
    "Advanced/ch11.html": "Advanced_ch11",
    "Advanced/ch07.html": "Advanced_ch07",
    "Advanced/ch16.html": "Advanced_ch16",
    "Advanced/ch01.html": "Advanced_ch01",
    "Advanced/ch14.html": "Advanced_ch14",
    "Advanced/next-level.html": "Advanced_next-level",
    "Advanced/ch02.html": "Advanced_ch02",
    "Advanced/ch03.html": "Advanced_ch03",
    "Advanced/ch15.html": "Advanced_ch15",
    "Advanced/ch12.html": "Advanced_ch12",
    "Advanced/ch04.html": "Advanced_ch04",
    "Advanced/ch08.html": "Advanced_ch08",
    "Advanced/ch09.html": "Advanced_ch09",
    "Advanced/ch05.html": "Advanced_ch05",
    "Advanced/ch13.html": "Advanced_ch13",
    "Articles/index.html": "Articles_index",
    "Articles/architecture.html": "Articles_architecture",
    "Articles/core-concepts.html": "Articles_core-concepts",
    "Articles/engineering.html": "Articles_engineering",
    "Articles/security.html": "Articles_security",
    "Articles/tools.html": "Articles_tools",
    "Articles/business.html": "Articles_business",
    "Basic/conclusion.html": "Basic_conclusion",
    "Basic/lecture-1.html": "Basic_lecture-1",
    "Basic/index.html": "Basic_index",
    "Basic/appendix-a.html": "Basic_appendix-a",
    "Basic/lecture-4.html": "Basic_lecture-4",
    "Basic/appendix-c.html": "Basic_appendix-c",
    "Basic/appendix-b.html": "Basic_appendix-b",
    "Basic/lecture-5.html": "Basic_lecture-5",
    "Basic/lecture-2.html": "Basic_lecture-2",
    "Basic/lecture-3.html": "Basic_lecture-3",
    "Practice/index.html": "Practice_index",
}

# 线上章节 slug -> 本地文件名，用于把章节总览里的绝对路径转本地相对
INNER_SLUG_MAP = {
    ("advanced", "01-environment-setup"): "ch01.html",
    ("advanced", "02-ai-tuning-guide"): "ch02.html",
    ("advanced", "03-prd-doc-driven"): "ch03.html",
    ("advanced", "04-dev-fundamentals"): "ch04.html",
    ("advanced", "05-ui-ux"): "ch05.html",
    ("advanced", "06-data-persistence-database"): "ch06.html",
    ("advanced", "07-backend-api"): "ch07.html",
    ("advanced", "08-auth-security"): "ch08.html",
    ("advanced", "09-testing-automation"): "ch09.html",
    ("advanced", "10-localhost-public-access"): "ch10.html",
    ("advanced", "11-git-collaboration"): "ch11.html",
    ("advanced", "12-serverless-deploy-cicd"): "ch12.html",
    ("advanced", "13-domain-dns"): "ch13.html",
    ("advanced", "14-vps-ops-deploy"): "ch14.html",
    ("advanced", "15-seo-analytics"): "ch15.html",
    ("advanced", "16-user-feedback-iteration"): "ch16.html",
    ("advanced", "99-next-level"): "next-level.html",
    ("basic", "00-preface"): "lecture-1.html",
    ("basic", "01-awakening"): "lecture-2.html",
    ("basic", "02-mindset"): "lecture-3.html",
    ("basic", "03-technique"): "lecture-4.html",
    ("basic", "04-practice-0-to-1"): "lecture-5.html",
    ("basic", "05-advanced"): "appendix-a.html",
    ("basic", "06-launch"): "appendix-b.html",
    ("basic", "99-appendix"): "appendix-c.html",
    ("basic", "100-epilogue"): "conclusion.html",
    ("articles", "01-core-concepts"): "core-concepts.html",
    ("articles", "02-technical-architecture"): "architecture.html",
    ("articles", "03-toolchain-frameworks"): "tools.html",
    ("articles", "04-engineering-practices"): "engineering.html",
    ("articles", "05-security-compliance"): "security.html",
    ("articles", "06-business-trends"): "business.html",
}

# 站点目录结构（篇 -> 章节本地文件）。子页在 fill 时从爬取 meta 动态附加。
TOC = [
    ("基础篇", "Basic/index.html", [
        ("Basic/lecture-1.html", "00 序言"),
        ("Basic/lecture-2.html", "01 觉醒"),
        ("Basic/lecture-3.html", "02 心智"),
        ("Basic/lecture-4.html", "03 技法"),
        ("Basic/lecture-5.html", "04 从0到1"),
        ("Basic/appendix-a.html", "05 进阶"),
        ("Basic/appendix-b.html", "06 上线"),
        ("Basic/appendix-c.html", "99 附录"),
        ("Basic/conclusion.html", "100 结语"),
    ]),
    ("进阶篇", "Advanced/index.html", [
        ("Advanced/ch01.html", "01 环境搭建"),
        ("Advanced/ch02.html", "02 AI怎么用"),
        ("Advanced/ch03.html", "03 从需求到文档"),
        ("Advanced/ch04.html", "04 开发常识"),
        ("Advanced/ch05.html", "05 好看好用的界面"),
        ("Advanced/ch06.html", "06 数据存哪里"),
        ("Advanced/ch07.html", "07 连接前后端"),
        ("Advanced/ch08.html", "08 谁能访问数据"),
        ("Advanced/ch09.html", "09 功能测试"),
        ("Advanced/ch10.html", "10 公网访问"),
        ("Advanced/ch11.html", "11 协作开发"),
        ("Advanced/ch12.html", "12 无服务器部署"),
        ("Advanced/ch13.html", "13 域名解析"),
        ("Advanced/ch14.html", "14 部署到服务器"),
        ("Advanced/ch15.html", "15 SEO与统计"),
        ("Advanced/ch16.html", "16 反馈与迭代"),
        ("Advanced/next-level.html", "Next Level"),
    ]),
    ("文章", "Articles/index.html", [
        ("Articles/core-concepts.html", "核心概念"),
        ("Articles/architecture.html", "技术架构"),
        ("Articles/tools.html", "工具链"),
        ("Articles/engineering.html", "工程实践"),
        ("Articles/security.html", "安全合规"),
        ("Articles/business.html", "商业趋势"),
    ]),
    ("实践案例", "Practice/index.html", [
    ]),
]

def load_subs(slug):
    """从爬取 meta 读子页 slug 列表（按源站顺序）。"""
    meta_path = os.path.join(CRAWL, slug, "meta.json")
    if not os.path.exists(meta_path):
        return []
    try:
        meta = json.load(open(meta_path, encoding="utf-8"))
        return [s["slug"] for s in meta.get("subs", [])]
    except Exception:
        return []

def build_sidebar(current_file):
    """生成可收缩左侧 TOC。current_file 用于高亮与深度前缀。"""
    # 前缀：根页 ''，章节页 '../'，子页 '../../'
    depth = current_file.count('/')
    prefix = '../' * depth
    parts = []
    parts.append('<aside class="toc" id="toc">')
    parts.append('<button class="toc-toggle" id="tocToggle" aria-label="收起目录">«</button>')
    parts.append('<div class="toc-inner">')
    # 首页入口
    parts.append(f'<a class="toc-home" href="{prefix}index.html">TPvibe 首页</a>')
    for sect_name, sect_idx, chapters in TOC:
        parts.append('<details class="toc-sec" open>')
        parts.append(f'<summary>{sect_name}</summary>')
        parts.append('<ul>')
        for ch_file, ch_label in chapters:
            active = ' class="active"' if ch_file == current_file else ''
            parts.append(f'<li><a href="{prefix}{ch_file}"{active}>{ch_label}</a></li>')
            # 子页（子页文件相对当前页深两级）
            pslug = SLUG_FOR.get(ch_file)
            if pslug:
                for sub in load_subs(pslug):
                    # 子页路径：章节目录/子slug.html
                    sub_path = f'{ch_file.rsplit(".",1)[0]}/{sub}.html'
                    active_sub = ' class="active"' if sub_path == current_file else ''
                    parts.append(f'<li class="toc-sub"><a href="{prefix}{sub_path}"{active_sub}>{sub}</a></li>')
        parts.append('</ul>')
        parts.append('</details>')
    parts.append('</div>')
    parts.append('</aside>')
    parts.append('<script>'
                 'document.getElementById("tocToggle")'
                 '&&document.getElementById("tocToggle").addEventListener("click",function(){'
                 'var t=document.getElementById("toc");t.classList.toggle("collapsed");'
                 'this.textContent=t.classList.contains("collapsed")?"»":"«";});'
                 'document.querySelector(".toc-scrim")'
                 '&&document.querySelector(".toc-scrim").addEventListener("click",function(){'
                 'document.getElementById("tocToggleMobile").checked=false;});'
                 '</script>')
    return '\n'.join(parts)

# 子页 slug -> 章节本地文件 的反查（供 clean_body 改写 ./x.html 链接）
def chapter_slug_for_sub(parent_slug, sub_slug):
    return sub_slug

# TP 视角术语替换 (vibevibe 原声 -> TP 语境)
TERM_REPL = [
    ("VibeVibe", "TPvibe"),
    ("Vibe Vibe", "TPvibe"),
    ("vibevibe", "TPvibe"),
    ("秒哒", "AI 原型工具"),
    ("通义", "AI 助手"),
    ("夸克", "AI 助手"),
    ("coze", "AI Agent 平台"),
    ("扣子", "AI Agent 平台"),
]

def fix_head_chapter_links(head, depth):
    """外壳 <head> 里骨架自带的 <nav class="subnav"> 含裸章节文件名链接
    (ch01.html / lecture-1.html / next-level.html ...)，按深度改写成
    本地相对路径，避免死链。"""
    fname_to_local = {os.path.basename(lf): lf for lf in SLUG_FOR}
    up = "../" * depth

    def repl(mt):
        fn = mt.group(1)
        local = fname_to_local.get(fn)
        if local:
            return f'href="{up}{local}"'
        return mt.group(0)

    return re.sub(r'href="([^"./][^"]*\.html)"', repl, head)


def clean_body(html, slug, sub_dir="", depth=1, valid_subs=None):
    # 取 vp-doc 内层
    m = re.search(r'vp-doc[^>]*>(.*)', html, re.S)
    body = m.group(1) if m else html
    # 剥掉开头多余的包裹 <div>
    body = re.sub(r'^\s*<div>', '', body, count=1)
    # 剥掉结尾多余的 </div>
    body = re.sub(r'</div>\s*$', '', body, count=1)
    # 剥掉第一个 <h1>...</h1>（骨架已有标题）
    body = re.sub(r'<h1[^>]*>.*?</h1>', '', body, count=1, flags=re.S)
    # 清理 header-anchor 锚点（保留标题文字）
    body = re.sub(r'<a class="header-anchor"[^>]*>.*?</a>', '', body, flags=re.S)
    # VitePress 标题上的 tabindex 属性清理
    body = re.sub(r'<h([1-4])[^>]*>', r'<h\1>', body)
    # VitePress custom-block -> 转普通 div（保留内容）
    body = re.sub(r'<div class="tip custom-block">', '<div class="callout">', body)
    body = re.sub(r'<p class="custom-block-title">', '<p><strong>', body)
    # 内部小节链接 ./x.html -> 指向子页（可点击，深度感知）
    # depth=1(章节页): 子页在 ./<sub_dir>/<sub>.html
    # depth=2(子页):   兄弟子页在 ./<sub>.html
    # 仅当 sub 实际存在(valid_subs)才转链接，否则保留纯文本
    def sub_link_repl(mt):
        tag = mt.group(0)
        href = re.search(r'href="(\./[^"#?]+)"', tag)
        if not href:
            return tag
        path = href.group(1)
        if '../' in path:
            return tag
        sub = re.sub(r'\.html?$', '', path[2:], flags=re.I)
        if valid_subs is not None and sub not in valid_subs:
            # 子页未爬取，转纯文本
            txt = re.search(r'>(.*?)</a>', tag, re.S)
            return txt.group(1) if txt else tag
        if depth >= 2:
            return tag.replace(href.group(1), f"./{sub}.html")
        prefix = f"./{sub_dir}/" if sub_dir else "./"
        return tag.replace(href.group(1), f"{prefix}{sub}.html")
    body = re.sub(r'<a href="\./[^"#?]+">.*?</a>', sub_link_repl, body, flags=re.S)
    # 跨章相对链接 ./../<slug>/ -> 本地章节（深度感知）
    # depth=1: ../<Sect>/<file>.html ; depth=2: ../../<Sect>/<file>.html
    slug_to_local = {slug: local for (sect, slug), local in INNER_SLUG_MAP.items()}
    up = "../" * depth
    def cross_link_repl(mt):
        tag = mt.group(0)
        href = re.search(r'href="\./\.\./([^"/]+)/?', tag)
        if not href:
            return tag
        slug = href.group(1)
        local = slug_to_local.get(slug)
        if local:
            return tag.replace(href.group(0), f'{up}{local}')
        return tag
    body = re.sub(r'<a href="\./\.\./[^"]*">.*?</a>', cross_link_repl, body, flags=re.S)
    # 裸章节文件名链接 ch01.html / lecture-1.html 等（源站章节总览表）
    # -> 深度感知本地路径
    fname_to_local = {os.path.basename(lf): lf for lf in SLUG_FOR}
    up = "../" * depth
    def bare_href_repl(mt):
        fn = mt.group(1)
        local = fname_to_local.get(fn)
        if local:
            return f'href="{up}{local}"'
        return mt.group(0)
    body = re.sub(r'href="([^"./][^"]*\.html)"', bare_href_repl, body)
    # 修正源站内容里的拼写错误 hhttps:// -> https://
    body = re.sub(r'href="hhttps://', 'href="https://', body)
    # 绝对目录链接 /Basic/ -> 本地相对（深度感知）
    body = re.sub(r'href="/([A-Za-z]+)/"',
                  lambda mt: f'href="{up}{mt.group(1)}/index.html"', body)
    # 外链 https://www.vibevibe.cn/... -> 删除（避免死链/品牌）
    body = re.sub(r'<a href="https://www\.(?:vibe|tp)vibe\.cn[^"]*">(.*?)</a>', r'\1', body, flags=re.S)
    # 章节总览表的内部绝对路径 /Advanced/01-environment-setup/ -> 本地相对 ch01.html
    # 同目录章节直接写文件名；跨目录用 ../Xxx/yy.html
    def inner_link_repl(mt):
        tag = mt.group(0)
        href = re.search(r'href="([^"]+)"', tag)
        if not href:
            return tag
        u = href.group(1).strip("/")
        # u 形如 Advanced/01-environment-setup 或 Basic/lecture-1
        parts = u.split("/")
        if len(parts) == 2:
            sect, slugpart = parts
            # 找本地文件
            local = INNER_SLUG_MAP.get((sect.lower(), slugpart))
            if local:
                # 目标页相对当前文件目录
                # 当前页可能在同一 sect 目录或根目录，统一用 ../sect/file 形式
                new = f"../{sect}/{local}"
                return tag.replace(href.group(1), new)
        return tag
    body = re.sub(r'<a href="/[^"]*">.*?</a>', inner_link_repl, body, flags=re.S)
    # 图片路径改写：本地化已下载图片；下载失败的保留外链（避免 404）
    def crawl_img_dir(sl):
        if "__" in sl:
            s, sub = sl.split("__", 1)
            return os.path.join(CRAWL, s, "subs", sub, "images")
        return os.path.join(CRAWL, sl, "images")
    cdir = crawl_img_dir(slug)
    def img_repl(mt):
        tag = mt.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src: return tag
        surl = src.group(1)
        # 绝对路径 /images/... 或外链：尝试按源站域名定位；下载失败的保留外链
        if surl.startswith("/"):
            ext = "https://www.vibevibe.cn" + surl
            fname = re.sub(r'[^\w\.-]', '_', surl.split("/")[-1].split('?')[0]) or "img.png"
            local_abs = os.path.join(cdir, fname)
            if os.path.exists(local_abs):
                return tag.replace(surl, f"../images/{slug}/{fname}")
            return tag.replace(surl, ext)   # 保留外链，源站在线可加载
        if surl.startswith("http"):
            fname = re.sub(r'[^\w\.-]', '_', surl.split("/")[-1].split('?')[0]) or "img.png"
            local_abs = os.path.join(cdir, fname)
            if os.path.exists(local_abs):
                return tag.replace(surl, f"../images/{slug}/{fname}")
            return tag   # 保留外链
        # 相对路径本地图片
        fname = surl.split("/")[-1].split('?')[0]
        local_abs = os.path.join(cdir, fname)
        if os.path.exists(local_abs):
            return tag.replace(surl, f"../images/{slug}/{fname}")
        return tag
    body = re.sub(r'<img[^>]*>', img_repl, body)
    # TP 视角术语替换
    for a, b in TERM_REPL:
        body = body.replace(a, b)
    # 清理多余空白行
    body = re.sub(r'\n\s*\n\s*\n+', '\n\n', body)
    body = body.strip()
    # 配平 div：统计开合差，末尾补齐/开头削减
    opens = body.count('<div'); closes = body.count('</div>')
    diff = opens - closes
    if diff > 0:
        body = body + '</div>' * diff
    elif diff < 0:
        # 从末尾移除多余 </div>
        for _ in range(-diff):
            body = body[:-len('</div>')] if body.endswith('</div>') else body
    return body

def copy_images(slug):
    src = os.path.join(CRAWL, slug, "images")
    if not os.path.isdir(src): return 0
    dst = os.path.join(IMG_DEST, slug)
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in os.listdir(src):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg')):
            shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
            n += 1
    return n

def fill_one(local_file):
    slug = SLUG_FOR.get(local_file)
    if not slug:
        print(f"  ✗ 无 slug 映射: {local_file}")
        return False
    crawl_html = os.path.join(CRAWL, slug, "content.html")
    if not os.path.exists(crawl_html):
        print(f"  ✗ 无爬取结果: {local_file} (slug={slug})")
        return False

    raw = open(crawl_html, encoding="utf-8").read()
    # 骨架文件（用于外壳与首页内容）
    bak = os.path.join(ROOT, "..", "archive", "pre-fill-html", local_file)
    if not os.path.exists(bak):
        print(f"  ✗ 无备份骨架: {bak}")
        return False
    # 首页：保留骨架自带的手写 landing 内容（不覆盖为爬取的部署文档）
    if local_file == "index.html":
        sk = open(bak, encoding="utf-8").read()
        mb = re.search(r'<main class="container">(.*?)</main>', sk, re.S)
        body = mb.group(1) if mb else raw
        body = body.replace('href="https://www.tpvibe.cn/deployment/"', 'href="Advanced/index.html"')
        body = body.replace('https://www.tpvibe.cn/deployment', 'Advanced/index.html')
        nimg = 0
    else:
        ch_base = os.path.basename(local_file).rsplit('.', 1)[0]
        valid = set(load_subs(slug))
        body = clean_body(raw, slug, sub_dir=ch_base, depth=1, valid_subs=valid)
        if len(body) < 200:
            print(f"  ⚠ 正文过短: {local_file} ({len(body)})")
        nimg = copy_images(slug)

    # 从备份骨架取外壳（源骨架 main 区有损坏嵌套，这里重建 main）
    page = open(bak, encoding="utf-8").read()

    # 外壳头部：到 <main class="container"> 之前（含 nav/breadcrumbs/subnav）
    head = page.split('<main class="container">')[0]
    # 注入可收缩左侧 TOC 侧栏（在 <body> 之后、header 之前）
    sidebar = build_sidebar(local_file)
    head = head.replace('<body>', '<body>\n' + sidebar, 1)
    # 移动端侧栏遮罩 + 汉堡按钮
    head = head.replace('<div id="progress"></div>',
                        '<div id="progress"></div>\n<label for="tocToggleMobile" class="toc-burger" aria-label="目录">☰</label>\n<input type="checkbox" id="tocToggleMobile" class="toc-toggle-cb" aria-hidden="true">\n<div class="toc-scrim"></div>', 1)
    head = fix_head_chapter_links(head, 1)
    # 根首页(depth 0)外壳导航里的 ../Section/ -> Section/（避免死链）
    if local_file == "index.html":
        head = re.sub(r'href="\.\./(Advanced|Basic|Articles|Practice)/',
                      r'href="\1/', head)
    # 外壳尾部：优先从 pager 的 </nav> 之后；无 pager 则从 content 区后的 </main> 之后
    pm = re.search(r'<nav class="pager">.*?</nav>', page, re.S)
    if pm:
        tail_start = pm.end()
    else:
        # 无 pager（首页/汇总页）：取第一个 </main> 之后作为 tail
        main_end = page.find('</main>')
        if main_end == -1:
            print(f"  ✗ 无 pager 且无 main: {local_file}")
            return False
        tail_start = main_end + len('</main>')
    tail = page[tail_start:]
    # 中间重建干净 main 区
    tm = re.search(r'<h1 class="page-title">(.*?)</h1>', page, re.S)
    ptitle = re.sub(r'<[^>]+>', '', tm.group(1)).strip() if tm else ""
    cover_txt = re.sub(r'[\\/:*?"<>|]', '', ptitle)[:40] if ptitle else slug

    if local_file == "index.html":
        # 首页用骨架自带完整 main 内容（已含标题/封面/正文），不再包裹
        main_block = '<main class="container">\n' + body + '\n</main>'
    else:
        main_block = (
            '<main class="container">\n'
            f'<h1 class="page-title">{ptitle}</h1>\n'
            '<div class="page-cover reveal">\n'
            f'<div style="background:var(--soft);border:1px solid var(--line);border-radius:var(--radius);padding:2rem;text-align:center;color:var(--muted);font-style:italic;">{cover_txt}</div>\n'
            '</div>\n\n'
            f'<div class="content reveal">\n{body}\n</div>\n'
            '</main>'
        )

    new_page = head + main_block + "\n" + tail
    # 清洗损坏嵌套：</main> 只保留最后 1 个
    parts = new_page.split('</main>')
    new_page = ''.join(parts[:-1]) + '</main>' + parts[-1]
    # favicon/og 图片路径深度修正：子目录页用 ../images，根页用 images
    if '/' in local_file:
        new_page = new_page.replace('href="images/tp_logo.jpg"', 'href="../images/tp_logo.jpg"')
        new_page = new_page.replace('content="https://tphub.tpgofighting.top/tpvibe/images/tp_logo.jpg"',
                                    'content="https://tphub.tpgofighting.top/tpvibe/images/tp_logo.jpg"')
    # 结语页“下部预告”硬链接 -> 进阶篇本地入口（避免死链/外部品牌）
    if local_file == "Basic/conclusion.html":
        new_page = new_page.replace(
            '<a href="/Basic/101-next-part/">进入下部预告：Vibe Coding 全栈实战教程 →</a>',
            '<a href="../Advanced/index.html">进入下部预告：TPvibe 全栈实战教程 →</a>')
    # 全局 div 配平：只删尾部连续多余的 </div>（浏览器容错，但保持整洁）
    opens = new_page.count('<div'); closes = new_page.count('</div>')
    diff = closes - opens
    if diff > 0:
        # 移除尾部 diff 个 </div>
        for _ in range(diff):
            if new_page.rstrip().endswith('</div>'):
                new_page = new_page.rstrip()[:-6].rstrip()
            else:
                break
        new_page = new_page + '\n'
    path = os.path.join(ROOT, local_file)
    open(path, "w", encoding="utf-8").write(new_page)
    print(f"  ✓ {local_file}: 正文 {len(body)} 字符, 复制图片 {nimg} 张")
    return True

def fill_subs(local_file):
    """为某章节生成其子页 <chapter_dir>/<sub>.html（深度两级，链接用 ../../）。"""
    slug = SLUG_FOR.get(local_file)
    if not slug:
        return 0
    subs = load_subs(slug)
    if not subs:
        return 0
    ch_dir = os.path.dirname(local_file)          # Advanced
    ch_base = os.path.basename(local_file).rsplit('.',1)[0]  # ch01
    sub_parent = os.path.join(ROOT, ch_dir, ch_base)
    os.makedirs(sub_parent, exist_ok=True)
    # 复制子页图片到 images/<slug>/subs/<sub>/
    copy_sub_images(slug)
    bak = os.path.join(ROOT, "..", "archive", "pre-fill-html", local_file)
    if not os.path.exists(bak):
        return 0
    page = open(bak, encoding="utf-8").read()
    head = page.split('<main class="container">')[0]
    head = fix_head_chapter_links(head, 2)
    pm = re.search(r'<nav class="pager">.*?</nav>', page, re.S)
    if pm:
        tail_start = pm.end()
    else:
        main_end = page.find('</main>')
        if main_end == -1:
            return 0
        tail_start = main_end + len('</main>')
    tail = page[tail_start:]
    tm = re.search(r'<h1 class="page-title">(.*?)</h1>', page, re.S)
    ptitle = re.sub(r'<[^>]+>', '', tm.group(1)).strip() if tm else ""
    n = 0
    for sub in subs:
        sub_html = os.path.join(CRAWL, slug, "subs", sub, "content.html")
        if not os.path.exists(sub_html):
            continue
        raw = open(sub_html, encoding="utf-8").read()
        sub_body = clean_body(raw, f"{slug}__{sub}", sub_dir=sub, depth=2, valid_subs=set(subs))
        # 子页内图片路径：../../images/<slug>/subs/<sub>/
        # clean_body 把 images/x.png 写成 ../images/<slug>__<sub>/x.png
        sub_body = sub_body.replace(f'../images/{slug}__{sub}/',
                                    f'../../images/{slug}/subs/{sub}/')
        # 子页内部 ./x.html 链接仍指向同目录子页
        sub_title = sub
        breadcrumb = (f'<nav class="breadcrumbs"><a href="../../index.html">首页</a>'
                      f'<span class="sep">›</span><a href="../../{local_file}">{ptitle or ch_base}</a>'
                      f'<span class="sep">›</span><span>{sub}</span></nav>')
        sidebar = build_sidebar(f"{ch_dir}/{ch_base}/{sub}.html")
        main_block = (
            '<main class="container">\n'
            f'<h1 class="page-title">{sub}</h1>\n'
            '<div class="page-cover reveal">\n'
            f'<div style="background:var(--soft);border:1px solid var(--line);border-radius:var(--radius);padding:2rem;text-align:center;color:var(--muted);font-style:italic;">{sub}</div>\n'
            '</div>\n\n'
            f'<div class="content reveal">\n{sub_body}\n</div>\n'
            '</main>'
        )
        new_page = head.replace('<body>', '<body>\n' + sidebar, 1) + main_block + "\n" + tail
        parts = new_page.split('</main>')
        new_page = ''.join(parts[:-1]) + '</main>' + parts[-1]
        # 深度两级资源路径修正
        new_page = new_page.replace('href="images/tp_logo.jpg"', 'href="../../images/tp_logo.jpg"')
        new_page = new_page.replace('href="../style.css"', 'href="../../style.css"')
        new_page = new_page.replace('src="../images/tp_logo.jpg"', 'src="../../images/tp_logo.jpg"')
        # 子页头部链接（logo/nav）需 ../../
        new_page = new_page.replace('href="../index.html"', 'href="../../index.html"')
        new_page = new_page.replace('href="../Basic/', 'href="../../Basic/')
        new_page = new_page.replace('href="../Advanced/', 'href="../../Advanced/')
        new_page = new_page.replace('href="../Articles/', 'href="../../Articles/')
        new_page = new_page.replace('href="../Practice/', 'href="../../Practice/')
        out_path = os.path.join(sub_parent, f"{sub}.html")
        # 原版 vibevibe 演示动画组件 (me-*) 的交互逻辑复刻
        if "me-root" in sub_body:
            me_js = (
                '<script>'
                '(function(){'
                'var root=document.querySelector(".me-root");if(!root)return;'
                'var items=["登录页","首页列表","详情页","设置页","关于页"];'
                'var playBtn=root.querySelector(".me-btn:not(.me-btn-outline)");'
                'var resetBtn=root.querySelector(".me-btn-outline");'
                'var listDemo=root.querySelector(".me-list-demo");'
                'var cards=root.querySelectorAll(".me-scroll-card");'
                'function play(){'
                '  if(!listDemo)return;'
                '  listDemo.innerHTML=\'<div class="me-list">\'+'
                '    items.map(function(t,i){return \'<div class="me-list-item" style="animation-delay:\'+(i*0.12)+\'s">\'+t+\'</div>\';}).join("")+\'</div>\';'
                '  if(playBtn)playBtn.disabled=true;'
                '}'
                'function setupScroll(){'
                '  if(!("IntersectionObserver"in window)||!cards.length)return;'
                '  var io=new IntersectionObserver(function(es){'
                '    es.forEach(function(e){if(e.isIntersecting)e.target.classList.add("visible");});'
                '  },{root:root.querySelector(".me-scroll-container"),threshold:0.3});'
                '  cards.forEach(function(c){io.observe(c);});'
                '}'
                'function reset(){'
                '  cards.forEach(function(c){c.classList.remove("visible");});'
                '  var sc=root.querySelector(".me-scroll-container");if(sc)sc.scrollTop=0;'
                '  if(playBtn)playBtn.disabled=false;'
                '  if(listDemo)listDemo.innerHTML=\'<div class="me-list-placeholder"> 点击「播放」查看效果 </div>\';'
                '}'
                'if(playBtn)playBtn.addEventListener("click",play);'
                'if(resetBtn)resetBtn.addEventListener("click",reset);'
                'setupScroll();'
                '})();'
                '</script>'
            )
            new_page = new_page.replace('</main>', me_js + '\n</main>', 1)
        open(out_path, "w", encoding="utf-8").write(new_page)
        n += 1
    print(f"  ✓ {local_file} 子页 {n} 个 -> {ch_dir}/{ch_base}/")
    return n

def copy_sub_images(slug):
    src = os.path.join(CRAWL, slug, "subs")
    if not os.path.isdir(src):
        return 0
    dst_root = os.path.join(IMG_DEST, slug, "subs")
    n = 0
    for sub in os.listdir(src):
        sdir = os.path.join(src, sub, "images")
        if not os.path.isdir(sdir):
            continue
        ddir = os.path.join(dst_root, sub)
        os.makedirs(ddir, exist_ok=True)
        for f in os.listdir(sdir):
            if f.lower().endswith(('.png','.jpg','.jpeg','.webp','.gif','.svg')):
                shutil.copy2(os.path.join(sdir, f), os.path.join(ddir, f))
                n += 1
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    targets = [lf for lf in SLUG_FOR if (only is None or lf in only)]
    print(f"待填入: {len(targets)} 章")
    ok = 0
    for lf in targets:
        print(f"[ {lf} ]")
        if fill_one(lf): ok += 1
        fill_subs(lf)
    print(f"\n完成: {ok}/{len(targets)} 章 (+子页)")

if __name__ == "__main__":
    main()
