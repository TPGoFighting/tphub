# TPvibe 内容站点

本目录是 TP Hub 的教程内容站，纯静态 HTML，直接部署（1:1 目录映射，无构建步骤）。
任意静态托管（腾讯云 VPS / EdgeOne Pages / Vercel / GitHub Pages）均可直接发布。

## 目录结构

```
tpvibe/
├── index.html              # 站点首页
├── 404.html
├── Basic/                  # 基础篇（lecture-1~5 + appendix-a/b/c + conclusion）
├── Advanced/               # 进阶篇（ch01~ch16 + index + next-level）
├── Articles/               # 文章篇（architecture/business/core-concepts/engineering/security/tools）
├── Practice/               # 实践案例篇
├── images/                 # 内容图片，按章节目录组织
├── style.css               # 主样式表
├── ch01-labs.css/js        # Ch01 实验室交互
├── animation-labs.css/js   # 动画实验室交互
└── toc-sheet.js            # 目录/侧边栏交互
```

### 链接约定

- 所有内部链接使用**绝对路径**（`/tpvibe/xxx.html`），图片同理（`/tpvibe/images/...`）
- 页面骨架为章节卡片 + `.content.reveal` 正文容器

## 内容生成管线

正文内容由 `../scripts/crawl_tpvibe.py`（爬取）和 `../scripts/fill_tpvibe.py`（填入骨架）生成，
中间产物在 `_crawl/`（不进入版本库）。详见仓库根 `README.md`。

## 质量检查

```bash
python3 ../scripts/check_site.py   # 断链 + sitemap + 符号链接 + 未引用图片
```

## 历史说明

早期版本曾使用 `text-content/` 与 `media-assets/` 符号链接目录做本地内容索引，
其指向本机绝对路径，对协作者无效，已在仓库中移除；相关内容源即为本目录本身。