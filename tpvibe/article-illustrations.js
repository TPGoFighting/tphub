(function () {
  'use strict';

  var path = window.location.pathname;
  var articleRoot = '/tpvibe/Articles/';
  if (path.indexOf(articleRoot) === -1) return;

  var cover = document.querySelector('.page-cover');
  var title = document.querySelector('.page-title');
  if (cover && title && title.parentElement !== cover) {
    title.classList.add('cover-title');
    cover.prepend(title);
  }

  var relativePath = path.slice(path.indexOf(articleRoot) + articleRoot.length);
  var indexPages = /^(index|core-concepts|architecture|business|engineering|security|tools)\.html$/;
  if (!relativePath || indexPages.test(relativePath)) return;

  var content = document.querySelector('.content');
  var article = document.querySelector('main.container');
  if (!content || !article || article.querySelector('.article-illustration-tail')) return;

  var illustrations = [
    {
      src: '/tpvibe/images/articles/ai-code-proof/idea-to-launch.png',
      alt: '从一个想法经过 AI 协作、原型制作到正式上线的创作流程',
      caption: '把想法变成作品，关键是让每一步都能被看见、验证和继续推进。',
      width: 1254,
      height: 1254
    },
    {
      src: '/tpvibe/images/articles/ai-code-proof/spec-from-idea.png',
      alt: '把模糊想法拆成规格和产品蓝图',
      caption: '先把问题拆清楚，再让 AI 帮你把方案落地。',
      width: 1448,
      height: 1086
    },
    {
      src: '/tpvibe/images/articles/ai-code-proof/evidence-loop.png',
      alt: '通过测试清单、浏览器预览和部署形成证据链',
      caption: '测试、预览和部署，组成一条可以复查的证据链。',
      width: 1448,
      height: 1086
    },
    {
      src: '/tpvibe/images/articles/ai-code-proof/human-review.png',
      alt: '人类使用红色铅笔审查 AI 生成的工作',
      caption: 'AI 加速执行，人类负责判断、取舍和最终确认。',
      width: 1448,
      height: 1086
    }
  ];

  function stableIndex(value) {
    var hash = 0;
    for (var i = 0; i < value.length; i += 1) {
      hash = ((hash << 5) - hash) + value.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash) % illustrations.length;
  }

  var selected = illustrations[stableIndex(path)];
  var figure = document.createElement('figure');
  figure.className = 'article-illustration-tail';
  figure.setAttribute('aria-label', '文章配图');

  var image = document.createElement('img');
  image.src = selected.src;
  image.alt = selected.alt;
  image.width = selected.width;
  image.height = selected.height;
  image.loading = 'lazy';
  figure.appendChild(image);

  var caption = document.createElement('figcaption');
  caption.textContent = selected.caption;
  figure.appendChild(caption);
  article.appendChild(figure);
})();
