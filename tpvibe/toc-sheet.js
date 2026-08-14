/**
 * TPvibe Mobile TOC Bottom Sheet
 * 
 * 在移动端（≤1024px）将侧边栏目录转换为底部 Sheet 展现形式。
 * 解决两个问题：
 * 1. 原侧边栏抽屉因 HTML 顺序问题（.toc 在 .toc-toggle-cb 之前）导致 CSS ~ 选择器失效，打不开
 * 2. 侧边栏目录在移动端窄屏体验差，底部 Sheet 更符合移动端操作习惯
 * 
 * 工作原理：
 * - 自动检测页面是否有 .toc 侧边栏
 * - 在移动端动态创建 FAB 按钮 + 底部 Sheet
 * - 将 .toc-inner 的内容克隆到 Sheet body 中
 * - 支持下滑关闭手势、遮罩点击关闭、ESC 关闭
 * - 在桌面端（>1024px）自动隐藏，不影响原有侧边栏
 */
(function () {
  'use strict';

  var MOBILE_BREAKPOINT = 1024;
  var sheetCreated = false;
  var sheetEl = null;
  var fabEl = null;
  var cbEl = null;
  var scrimEl = null;
  var closeBtn = null;
  var bodyEl = null;
  var dragHandle = null;

  function isMobile() {
    return window.innerWidth <= MOBILE_BREAKPOINT;
  }

  function hasToc() {
    return !!document.querySelector('aside.toc');
  }

  /**
   * 构建底部 Sheet DOM 结构
   * 结构（顺序很重要，~ 选择器要求 cb 在 sheet 之前）：
   * <input class="toc-sheet-cb" id="tocSheetCb" type="checkbox">
   * <div class="toc-sheet-scrim"></div>
   * <div class="toc-sheet">
   *   <div class="toc-sheet-handle"></div>
   *   <div class="toc-sheet-header">
   *     <div class="toc-sheet-title">目录</div>
   *     <button class="toc-sheet-close" aria-label="关闭目录">×</button>
   *   </div>
   *   <div class="toc-sheet-body"></div>
   * </div>
   * <label for="tocSheetCb" class="toc-fab">...</label>
   */
  function buildSheet() {
    if (sheetCreated) return;
    sheetCreated = true;

    // 1. Hidden checkbox (state controller) — must be BEFORE .toc-sheet for ~ selector
    cbEl = document.createElement('input');
    cbEl.type = 'checkbox';
    cbEl.id = 'tocSheetCb';
    cbEl.className = 'toc-sheet-cb';
    cbEl.setAttribute('aria-hidden', 'true');

    // 2. Scrim (overlay behind sheet)
    scrimEl = document.createElement('div');
    scrimEl.className = 'toc-sheet-scrim';

    // 3. Sheet panel
    sheetEl = document.createElement('div');
    sheetEl.className = 'toc-sheet';
    sheetEl.setAttribute('role', 'dialog');
    sheetEl.setAttribute('aria-modal', 'true');
    sheetEl.setAttribute('aria-label', '目录');

    // 3a. Drag handle
    dragHandle = document.createElement('div');
    dragHandle.className = 'toc-sheet-handle';
    dragHandle.setAttribute('aria-hidden', 'true');
    sheetEl.appendChild(dragHandle);

    // 3b. Header (title + close button)
    var header = document.createElement('div');
    header.className = 'toc-sheet-header';
    var title = document.createElement('div');
    title.className = 'toc-sheet-title';
    title.textContent = '目录';
    header.appendChild(title);
    closeBtn = document.createElement('button');
    closeBtn.className = 'toc-sheet-close';
    closeBtn.setAttribute('aria-label', '关闭目录');
    closeBtn.innerHTML = '&times;';
    header.appendChild(closeBtn);
    sheetEl.appendChild(header);

    // 3c. Body (scrollable, will hold cloned TOC content)
    bodyEl = document.createElement('div');
    bodyEl.className = 'toc-sheet-body';
    sheetEl.appendChild(bodyEl);

    // 4. FAB (floating action button) — placed AFTER sheet in DOM, that's fine
    fabEl = document.createElement('label');
    fabEl.className = 'toc-fab';
    fabEl.setAttribute('for', 'tocSheetCb');
    fabEl.setAttribute('aria-label', '打开目录');
    fabEl.innerHTML = '<svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></svg>';

    // Insert into body in correct order
    document.body.appendChild(cbEl);
    document.body.appendChild(scrimEl);
    document.body.appendChild(sheetEl);
    document.body.appendChild(fabEl);

    // Wire up interactions
    setupInteractions();
  }

  /**
   * 将 .toc-inner 的内容克隆到 sheet body 中
   * 每次打开时刷新，确保 active 状态正确
   */
  function refreshSheetContent() {
    if (!bodyEl) return;
    var tocInner = document.querySelector('aside.toc .toc-inner');
    if (!tocInner) return;

    // 清空旧的
    bodyEl.innerHTML = '';

    // 添加当前章节标签
    var activeSec = document.querySelector('aside.toc details.toc-sec[open] > summary');
    if (activeSec) {
      var label = document.createElement('div');
      label.className = 'toc-sheet-active-sec';
      label.textContent = activeSec.textContent.trim();
      bodyEl.appendChild(label);
    }

    // 克隆目录内容
    var clone = tocInner.cloneNode(true);
    // 移除 home link（已经在 header 有标题）
    var home = clone.querySelector('.toc-home');
    if (home) home.remove();
    bodyEl.appendChild(clone);

    // 重新绑定章节展开/收起按钮（克隆后事件丢失）
    bodyEl.querySelectorAll('.toc-chapter-toggle').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var li = this.closest('.toc-chapter');
        if (li) li.classList.toggle('expanded');
      });
    });

    // 点击目录链接后自动关闭 sheet
    bodyEl.querySelectorAll('a[href]').forEach(function (a) {
      a.addEventListener('click', function () {
        closeSheet();
      });
    });
  }

  function openSheet() {
    if (!sheetEl) return;
    refreshSheetContent();
    sheetEl.classList.add('open');
    if (scrimEl) scrimEl.classList.add('open');
    if (fabEl) fabEl.classList.add('opened');
    if (fabEl) fabEl.setAttribute('aria-label', '目录已打开');
    // 锁定 body 滚动
    document.body.style.overflow = 'hidden';
  }

  function closeSheet() {
    if (!sheetEl) return;
    sheetEl.classList.remove('open');
    if (scrimEl) scrimEl.classList.remove('open');
    if (fabEl) fabEl.classList.remove('opened');
    if (fabEl) fabEl.setAttribute('aria-label', '打开目录');
    document.body.style.overflow = '';
  }

  /**
   * 下滑关闭手势支持
   */
  function setupDragToClose() {
    if (!dragHandle || !sheetEl) return;
    var startY = 0;
    var currentY = 0;
    var dragging = false;

    dragHandle.addEventListener('touchstart', function (e) {
      if (!cbEl || !cbEl.checked) return;
      startY = e.touches[0].clientY;
      dragging = true;
      sheetEl.style.transition = 'none';
    }, { passive: true });

    dragHandle.addEventListener('touchmove', function (e) {
      if (!dragging) return;
      currentY = e.touches[0].clientY;
      var delta = currentY - startY;
      if (delta > 0) {
        sheetEl.style.transform = 'translateY(' + delta + 'px)';
      }
    }, { passive: true });

    dragHandle.addEventListener('touchend', function () {
      if (!dragging) return;
      dragging = false;
      sheetEl.style.transition = '';
      sheetEl.style.transform = '';
      var delta = currentY - startY;
      if (delta > 80) {
        closeSheet();
      }
    }, { passive: true });
  }

  function setupInteractions() {
    // Close button
    if (closeBtn) {
      closeBtn.addEventListener('click', closeSheet);
    }
    // Scrim click to close
    if (scrimEl) {
      scrimEl.addEventListener('click', closeSheet);
    }
    // FAB click → toggle
    if (fabEl) {
      fabEl.addEventListener('click', function (e) {
        e.preventDefault();
        if (sheetEl && sheetEl.classList.contains('open')) {
          closeSheet();
        } else {
          openSheet();
        }
      });
    }
    // ESC to close
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && cbEl && cbEl.checked) {
        closeSheet();
      }
    });
    // Drag to close
    setupDragToClose();
  }

  /**
   * 根据屏幕尺寸切换：移动端显示 FAB + Sheet，桌面端隐藏
   */
  function updateVisibility() {
    if (!sheetCreated) return;
    var mobile = isMobile();
    if (mobile) {
      fabEl.style.display = 'flex';
      // 隐藏原有的侧边栏
      var toc = document.querySelector('aside.toc');
      if (toc) toc.style.display = 'none';
    } else {
      fabEl.style.display = 'none';
      closeSheet();
      // 显示原有的侧边栏
      var toc = document.querySelector('aside.toc');
      if (toc) toc.style.display = '';
    }
  }

  function init() {
    if (!hasToc()) return;
    buildSheet();
    updateVisibility();

    // 监听窗口尺寸变化
    var resizeTimer = null;
    window.addEventListener('resize', function () {
      if (resizeTimer) clearTimeout(resizeTimer);
      resizeTimer = setTimeout(updateVisibility, 150);
    });

    // 监听 orientationchange
    window.addEventListener('orientationchange', function () {
      setTimeout(updateVisibility, 300);
    });
  }

  // DOMContentLoaded 或立即执行
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
