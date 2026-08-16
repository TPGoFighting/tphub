# TP Hub

TP Hub 工具导航与教程内容聚合站。生产域名：<https://tphub.tpgofighting.top>

- **根目录**：工具深度解读页（`*_intro.html`）+ 导航枢纽页 `tp.html`
- **`tpvibe/`**：TPvibe 教程内容站（基础篇 / 进阶篇 / 文章 / 实践案例），纯静态 HTML，见 [tpvibe/README.md](tpvibe/README.md)

## 仓库结构

```
tphub/
├── tp.html / index.html      # 导航枢纽（index 为元刷新跳转）
├── *_intro.html              # 工具解读页（自包含，无外部依赖）
├── tpvibe/                   # 教程内容站（部署单元）
├── scripts/                  # 生成管线 + 质量检查
│   ├── crawl_tpvibe.py       # 抓取内容（vibevibe.cn → _crawl/）
│   ├── fill_tpvibe.py        # 填入章节骨架 + TP 视角改造
│   └── check_site.py         # 断链 / sitemap / 符号链接 / 未引用图片检查
├── sitemap.xml / robots.txt  # SEO
├── BingSiteAuth.xml          # Bing 站点验证
├── googleac20c70d0a17e0b5.html  # Google 站点验证
└── .github/workflows/        # CI：仓库卫生检查
```

## 部署

`tpvibe/` 是完整部署单元（内部链接为绝对路径 `1:1` 映射，无需构建）。
生产部署脚本 `deploy.sh`（rsync 到腾讯云 VPS）位于本地工作区，不随本仓库分发。

## 本地开发

### 质量检查（提交前必跑）

```bash
python3 scripts/check_site.py
```

检查项：内部链接断链、sitemap URL 与文件一致性、仓库内符号链接、未被引用的图片资源。
CI 也会在每次 push/PR 时运行同一脚本。

### 重新生成 TPvibe 内容

```bash
python3 scripts/crawl_tpvibe.py --only Basic/lecture-1.html   # 爬取单章
python3 scripts/fill_tpvibe.py                                 # 填入全部章节
```

两者均以 `tpvibe/` 为站点根，中间产物在 `tpvibe/_crawl/`（不入库）。

## 内容更新流程

1. 修改 `tpvibe/` 下页面 / `images/`
2. 本地跑 `python3 scripts/check_site.py` 直到通过
3. 提交 → push（CI 复核）→ 本地 `deploy.sh` 发布

## 仓库卫生约定

- **禁止提交符号链接**：历史遗留的绝对路径符号链接（`text-content/`、`media-assets/`）已被移除
- **图片**：未引用图片会被 CI 报告，及时清理；大体积图片建议先压缩再入库
- **SEO 文件**（sitemap.xml / robots.txt / 站点验证文件）与站点内容同库维护，sitemap 必须与文件系统一致（CI 强制）