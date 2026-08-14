/* TPvibe animation chapter: restore the exported decision-tree interaction. */
(function () {
  'use strict';

  function initAnimationDecision(root) {
    var options = [
      { name: '纯 CSS / Tailwind', scene: '按钮悬停、淡入淡出、简单滑入', fit: '界面微交互', reason: '优先使用 CSS：体积最小、维护成本低，足够覆盖大多数界面反馈。' },
      { name: 'Motion', scene: '列表动画、页面切换、拖拽排序', fit: '组件级状态动画', reason: '适合 React 组件中的进入、退出和布局变化；声明式写法和组件状态更贴近。' },
      { name: 'GSAP', scene: '滚动视差、时间线动画、SVG 动画', fit: '精密时间线与滚动', reason: '需要精确编排多段动画或 ScrollTrigger 时，GSAP 的控制粒度更高。' },
      { name: 'Three.js', scene: '3D 产品展示、粒子效果、交互式 3D 场景', fit: '实时 3D 场景', reason: '只有确实需要 3D 空间、相机或大量粒子时再引入，避免为装饰增加复杂度。' }
    ];
    var state = { mode: 'decision', selected: null };

    function optionButton(option, index) {
      var selected = state.selected === index;
      return '<button type="button" class="animation-choice' + (selected ? ' is-selected' : '') + '" data-animation-choice="' + index + '" aria-pressed="' + selected + '"><strong>' + option.name + '</strong><small>' + option.scene + '</small></button>';
    }

    function render() {
      var decision = '<div class="animation-choice-grid" aria-label="选择动画需求">' + options.map(optionButton).join('') + '</div>';
      var recommendation = state.selected === null ? '<p class="animation-decision-description">选择一种需求，获得适合场景与取舍的建议。</p>' : (function () {
        var option = options[state.selected];
        return '<section class="animation-recommendation" aria-live="polite"><span>推荐方向 · ' + option.fit + '</span><strong>' + option.name + '</strong><p>' + option.reason + '</p></section>';
      }());
      var compare = '<div class="animation-compare-grid">' + options.map(function (option) {
        return '<article class="animation-compare-card"><h4>' + option.name + '</h4><p>' + option.scene + '</p><span class="animation-compare-tag">' + option.fit + '</span></article>';
      }).join('') + '</div>';
      var body = state.mode === 'decision' ? decision + recommendation : compare;
      root.innerHTML = '<section class="animation-decision-lab" aria-label="动画库选择器"><p class="animation-decision-kicker">Animation decision helper</p><h3>' + (state.mode === 'decision' ? '你想让哪一类交互动起来？' : '按场景比较动画方案') + '</h3><p class="animation-decision-description">先从用户感受到的效果倒推工具，不用为了“动”而引入复杂依赖。</p><div class="animation-mode-switch" role="toolbar" aria-label="切换动画库选择视图"><button type="button" data-animation-mode="decision" aria-pressed="' + (state.mode === 'decision') + '">决策模式</button><button type="button" data-animation-mode="compare" aria-pressed="' + (state.mode === 'compare') + '">对比模式</button></div>' + body + '</section>';
    }

    root.addEventListener('click', function (event) {
      var mode = event.target.closest('[data-animation-mode]');
      var choice = event.target.closest('[data-animation-choice]');
      if (mode) { state.mode = mode.getAttribute('data-animation-mode'); render(); }
      if (choice) { state.selected = Number(choice.getAttribute('data-animation-choice')); render(); }
    });
    root.dataset.animationLabReady = 'true';
    render();
  }

  function initAnimationLabs() { document.querySelectorAll('.adt-root').forEach(initAnimationDecision); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initAnimationLabs);
  else initAnimationLabs();
}());
