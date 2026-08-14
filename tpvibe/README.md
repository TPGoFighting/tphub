# TP Hub 资源索引

本目录通过**符号链接（symlink）**组织项目的所有文本内容和媒体资源，避免文件冗余，保持单一数据源。

---

## 资源统计概览

| 类别 | 数量 | 说明 |
|------|------|------|
| HTML 页面 | ~178 个 | 包含主页面、基础篇、进阶篇、文章、实践案例 |
| JavaScript 文件 | 3 个 | ch01-labs.js, animation-labs.js, toc-sheet.js |
| CSS 样式文件 | 3 个 | style.css, ch01-labs.css, animation-labs.css |
| Markdown 审查报告 | 12 个 | 各类审查、审计、验证报告文档 |
| 内容图片 | ~254 个 | tpvibe/images/ 下的所有图片资源 |
| 设计稿 | 9 个 | archive/design-drafts/ 下的设计草稿 |
| 截图 | 10 个 | screenshots/ 下的页面截图 |

---

## 目录结构

```
source/
├── README.md                         # 本文件（资源索引说明）
├── text-content/                     # 文本内容
│   ├── pages/                        # 主界面 HTML 页面
│   │   ├── root/                     # 根页面（首页、404）
│   │   │   ├── index.html        →   tpvibe/index.html
│   │   │   └── 404.html          →   tpvibe/404.html
│   │   ├── Basic/                →   tpvibe/Basic/（基础篇）
│   │   ├── Advanced/             →   tpvibe/Advanced/（进阶篇）
│   │   ├── Articles/             →   tpvibe/Articles/（文章篇）
│   │   └── Practice/             →   tpvibe/Practice/（实践案例篇）
│   ├── scripts/                      # JavaScript 脚本
│   │   ├── ch01-labs.js          →   tpvibe/ch01-labs.js
│   │   ├── animation-labs.js     →   tpvibe/animation-labs.js
│   │   └── toc-sheet.js          →   tpvibe/toc-sheet.js
│   ├── styles/                       # CSS 样式表
│   │   ├── style.css             →   tpvibe/style.css
│   │   ├── ch01-labs.css         →   tpvibe/ch01-labs.css
│   │   └── animation-labs.css    →   tpvibe/animation-labs.css
│   └── docs/                         # 审查报告文档（.md）
│       ├── P0修复验证报告.md      →   根目录/P0修复验证报告.md
│       ├── SVG封面图审查报告.md    →   根目录/SVG封面图审查报告.md
│       ├── TPvibe-SEO审计报告-Phase6.md → 根目录/...
│       ├── TPvibe基础篇审查报告.md →   根目录/...
│       ├── lint_tpvibe_review.md  →   根目录/...
│       ├── 侧边栏Ch05修复审查报告.md → 根目录/...
│       ├── 进阶篇审查报告_Ch05-Ch10.md → 根目录/...
│       ├── tpvibe-web-enhancement-plan.md → 根目录/...
│       ├── 文章板块审查报告.md     →   根目录/...
│       ├── 实践案例板块审查报告.md →   根目录/...
│       ├── tpvibe-advanced-review-report.md → 根目录/...
│       └── tpvibe-review-report.md →  根目录/...
└── media-assets/                     # 媒体资源
    ├── images/                   →   tpvibe/images/（内容图片）
    ├── design-drafts/            →   archive/design-drafts/（设计草稿）
    └── screenshots/              →   screenshots/（页面截图）
```

---

## 子目录内容简介

### text-content/pages/ — HTML 页面
- **root/**: 项目首页 (`index.html`) 和 404 错误页 (`404.html`)
- **Basic/**: 基础篇教程页面，包含 10 个根级章节页 + 8 个子目录（lecture-1~5、appendix-a~c、conclusion），覆盖入门到上线的完整路径
- **Advanced/**: 进阶篇教程页面，包含 18 个根级章节页（ch01~ch16 + index + next-level）+ 15 个子目录，涵盖环境搭建、AI 调优、PRD 驱动、前后端开发、部署运维等
- **Articles/**: 文章板块，包含 7 个根级页面（index + 6 个分类页）+ 6 个子目录（architecture、business、core-concepts、engineering、security、tools），收录深度技术文章
- **Practice/**: 实践案例篇，包含 index 页面和 index/ 子目录，收录完整实战项目案例

### text-content/scripts/ — JavaScript
- `ch01-labs.js`: Ch01 实验室交互脚本
- `animation-labs.js`: 动画实验室交互脚本
- `toc-sheet.js`: 目录/侧边栏表格交互脚本

### text-content/styles/ — CSS 样式
- `style.css`: 主样式表
- `ch01-labs.css`: Ch01 实验室专用样式
- `animation-labs.css`: 动画实验室专用样式

### text-content/docs/ — 审查报告
包含项目各阶段的审查、审计和验证报告，涵盖：
- SEO 审计报告（Phase 6）
- 基础篇、进阶篇、文章板块、实践案例板块审查报告
- SVG 封面图审查报告
- P0 修复验证报告
- 侧边栏修复审查报告
- Lint 代码审查报告
- Web 增强计划文档

### media-assets/images/ — 内容图片
tpvibe 项目的所有内容图片，按章节分类存放（Advanced、Basic、Articles、Practice 等子目录），包含教程截图、示意图、GIF 动图等。

### media-assets/design-drafts/ — 设计草稿
项目设计阶段的视觉稿，包含 logo、hero 图、卡片设计、账号页设计等版本迭代草稿。

### media-assets/screenshots/ — 页面截图
开发和审查过程中的页面截图，包含桌面端/移动端视图、SEO 审计截图、章节审查截图等。

---

## 注意事项

1. **符号链接机制**: 本目录下所有文件/目录均为符号链接（symlink），指向源文件的绝对路径。不占用额外磁盘空间。
2. **同步更新**: 修改源文件（如 `tpvibe/style.css`）会立即反映到本目录的链接中；反之亦然。所有修改都是对同一文件的操作。
3. **删除安全**: 删除本目录下的符号链接不会影响源文件。但**请勿通过符号链接删除源文件内容**。
4. **源文件位置**:
   - HTML/JS/CSS 源文件位于 `tpvibe/` 目录
   - 内容图片源位于 `tpvibe/images/`
   - 设计稿源位于 `archive/design-drafts/`
   - 截图源位于 `screenshots/`
   - 审查报告源位于项目根目录 `*.md`
5. **新增文件**: 若在源目录新增文件，需要手动在本目录对应位置创建新的符号链接。
6. **链接验证**: 可通过 `ls -la` 命令查看符号链接指向，箭头 `→` 后即为源文件路径。
