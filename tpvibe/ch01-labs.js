/* TPvibe Chapter 01: accessible progressive enhancement for embedded demos. */
(function () {
  'use strict';

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (character) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character];
    });
  }

  function formatTime(seconds) {
    var minutes = Math.floor(seconds / 60);
    var remaining = seconds % 60;
    return String(minutes).padStart(2, '0') + ':' + String(remaining).padStart(2, '0');
  }

  function counterPanel(value, history) {
    return '<p class="lab-kicker">数值状态</p>' +
      '<div class="counter-display"><strong class="counter-value" aria-live="polite">' + value + '</strong><span class="counter-label">当前数值</span></div>' +
      '<div class="counter-controls"><button type="button" data-counter-action="decrement">− 减一</button><button type="button" data-counter-action="reset">重置</button><button type="button" data-counter-action="increment">+ 加一</button></div>' +
      '<div class="quick-set"><input class="quick-input" type="number" inputmode="numeric" aria-label="设置计数器数值" placeholder="输入数值"><button class="quick-btn" type="button">设置数值</button></div>' +
      '<section class="lab-history" aria-label="操作历史"><h4>操作历史</h4><ul>' + history.map(function (entry) { return '<li>' + escapeHtml(entry) + '</li>'; }).join('') + '</ul></section>' +
      '<p class="shortcuts">快捷键：<span class="shortcut">↑</span>加一 <span class="shortcut">↓</span>减一 <span class="shortcut">R</span>重置</p>';
  }

  function timerPanel(seconds, running) {
    return '<p class="lab-kicker">专注计时</p>' +
      '<div class="timer-display"><strong class="timer-value" aria-live="polite">' + formatTime(seconds) + '</strong><span class="timer-label">' + (running ? '计时中' : '准备开始') + '</span></div>' +
      '<div class="timer-controls"><button type="button" data-timer-action="toggle">' + (running ? '暂停计时' : '开始计时') + '</button><button type="button" data-timer-action="reset">清零</button></div>' +
      '<p class="shortcuts">每秒自动更新；切换标签不会丢失进度。</p>';
  }

  function conversionPanel(value) {
    var number = Number.isFinite(value) ? Math.max(0, Math.min(65535, Math.floor(value))) : 42;
    return '<p class="lab-kicker">十进制 → 开发者常用表示</p>' +
      '<div class="lab-input-row"><input class="base-input" type="number" min="0" max="65535" inputmode="numeric" aria-label="十进制数值" value="' + number + '"><button type="button" class="base-update">转换</button></div>' +
      '<div class="conversion-grid" aria-live="polite"><div><span>十进制</span><strong>' + number + '</strong></div><div><span>十六进制</span><strong>0x' + number.toString(16).toUpperCase() + '</strong></div><div><span>二进制</span><strong>' + number.toString(2) + '</strong></div></div>' +
      '<p class="shortcuts">输入 0–65535 的整数，观察同一数值的不同表示。</p>';
  }

  function initInteractiveDemo(demo) {
    var tabs = Array.prototype.slice.call(demo.querySelectorAll('.tab-button'));
    var panel = demo.querySelector('.panel');
    if (!tabs.length || !panel) return;

    var state = { tab: 0, counter: 0, history: [], seconds: 0, running: false, base: 42, timerId: null };
    demo.dataset.ch01LabsReady = 'true';
    demo.setAttribute('aria-label', '环境搭建交互实验室');
    tabs.forEach(function (tab, index) {
      tab.setAttribute('type', 'button');
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-selected', index === 0 ? 'true' : 'false');
      tab.addEventListener('click', function () { render(index); });
    });

    function syncTabs() {
      tabs.forEach(function (tab, index) {
        var active = index === state.tab;
        tab.classList.toggle('active', active);
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
      });
    }

    function render(nextTab) {
      state.tab = nextTab;
      syncTabs();
      if (nextTab === 0) panel.innerHTML = counterPanel(state.counter, state.history);
      if (nextTab === 1) panel.innerHTML = timerPanel(state.seconds, state.running);
      if (nextTab === 2) panel.innerHTML = conversionPanel(state.base);
      bindPanel();
    }

    function bindPanel() {
      var decrement = panel.querySelector('[data-counter-action="decrement"]');
      var increment = panel.querySelector('[data-counter-action="increment"]');
      var reset = panel.querySelector('[data-counter-action="reset"]');
      var quickButton = panel.querySelector('.quick-btn');
      var quickInput = panel.querySelector('.quick-input');
      var timerToggle = panel.querySelector('[data-timer-action="toggle"]');
      var timerReset = panel.querySelector('[data-timer-action="reset"]');
      var baseInput = panel.querySelector('.base-input');
      var baseUpdate = panel.querySelector('.base-update');

      function updateCounter(next, description) {
        state.counter = next;
        state.history.unshift(description + ' → ' + next);
        state.history = state.history.slice(0, 5);
        render(0);
        var counter = panel.querySelector('.counter-value');
        if (counter) counter.classList.add('is-changing');
      }

      if (decrement) decrement.addEventListener('click', function () { updateCounter(state.counter - 1, '减一'); });
      if (increment) increment.addEventListener('click', function () { updateCounter(state.counter + 1, '加一'); });
      if (reset) reset.addEventListener('click', function () { updateCounter(0, '重置'); });
      if (quickButton) quickButton.addEventListener('click', function () {
        var next = Number(quickInput.value);
        if (Number.isFinite(next)) updateCounter(Math.floor(next), '设置数值');
        else quickInput.focus();
      });
      if (quickInput) quickInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') quickButton.click();
      });

      if (timerToggle) timerToggle.addEventListener('click', function () {
        state.running = !state.running;
        if (state.running && !state.timerId) {
          state.timerId = window.setInterval(function () {
            state.seconds += 1;
            if (state.tab === 1) render(1);
          }, 1000);
        }
        if (!state.running && state.timerId) {
          window.clearInterval(state.timerId);
          state.timerId = null;
        }
        render(1);
      });
      if (timerReset) timerReset.addEventListener('click', function () { state.seconds = 0; render(1); });

      function updateBase() {
        var next = Number(baseInput.value);
        if (Number.isFinite(next)) { state.base = next; render(2); }
        else baseInput.focus();
      }
      if (baseUpdate) baseUpdate.addEventListener('click', updateBase);
      if (baseInput) baseInput.addEventListener('keydown', function (event) { if (event.key === 'Enter') updateBase(); });
    }

    demo.addEventListener('keydown', function (event) {
      if (state.tab !== 0 || event.target.matches('input, button')) return;
      if (event.key === 'ArrowUp') { event.preventDefault(); state.counter += 1; state.history.unshift('快捷键加一 → ' + state.counter); render(0); }
      if (event.key === 'ArrowDown') { event.preventDefault(); state.counter -= 1; state.history.unshift('快捷键减一 → ' + state.counter); render(0); }
      if (event.key.toLowerCase() === 'r') { state.counter = 0; state.history.unshift('快捷键重置 → 0'); render(0); }
    });
    render(0);
  }

  function initTerminal(terminal) {
    var input = terminal.querySelector('input');
    var output = terminal.querySelector('.terminal-output, .output, pre');
    if (!input || !output) return;
    input.setAttribute('aria-label', 'Terminal 命令输入');
    input.addEventListener('keydown', function (event) {
      if (event.key !== 'Enter') return;
      var command = input.value.trim();
      if (!command) return;
      var reply = { help: '可用命令：help、pwd、ls、clear', pwd: '/Users/learner/tpvibe', ls: 'package.json  src/  public/' }[command] || 'command not found: ' + command;
      output.textContent = command === 'clear' ? '' : output.textContent + '\n$ ' + command + '\n' + reply;
      input.value = '';
      output.scrollTop = output.scrollHeight;
    });
  }

  function initInstallSimulator(simulator) {
    var button = simulator.querySelector('button');
    var fill = simulator.querySelector('.progress-fill');
    if (!button || !fill) return;
    button.addEventListener('click', function () {
      if (button.disabled) return;
      button.disabled = true;
      var progress = 0;
      var timer = window.setInterval(function () {
        progress += 20;
        fill.style.setProperty('--ch01-progress', progress + '%');
        if (progress >= 100) { window.clearInterval(timer); button.disabled = false; button.textContent = '安装完成 · 再来一次'; }
      }, 260);
    });
  }

  function labShell(kicker, title, description, body) {
    return '<div class="lab-shell"><div class="lab-heading"><p class="lab-kicker">' + kicker + '</p><h4>' + title + '</h4><p>' + description + '</p></div>' + body + '</div>';
  }

  function initNvmDemo(demo) {
    var state = {
      current: 'v24.12.0',
      installed: ['v24.12.0', 'v22.21.1'],
      output: ['Node Version Manager · 输入 nvm list、nvm use 22 或 nvm install 20']
    };

    function versionFor(value) {
      var cleaned = value.replace(/^v/, '');
      return state.installed.filter(function (version) { return version.replace(/^v/, '').indexOf(cleaned) === 0; })[0];
    }

    function addOutput(message) {
      state.output.unshift(message);
      state.output = state.output.slice(0, 5);
    }

    function runCommand(value) {
      var command = value.trim().replace(/\s+/g, ' ');
      if (!command) return;
      if (command === 'nvm list') addOutput('已安装：' + state.installed.join('  ') + '    当前：' + state.current);
      else if (command === 'nvm current') addOutput('当前 Node.js 版本：' + state.current);
      else if (/^nvm use /i.test(command)) {
        var requested = versionFor(command.replace(/^nvm use\s+/i, ''));
        if (requested) { state.current = requested; addOutput('已切换到 ' + requested + '。'); }
        else addOutput('未找到该版本；先试试 nvm install ' + command.replace(/^nvm use\s+/i, '') + '。');
      } else if (/^nvm install /i.test(command)) {
        var installed = 'v' + command.replace(/^nvm install\s+/i, '').replace(/^v/, '');
        if (/^v\d+(\.\d+){0,2}$/.test(installed)) {
          if (state.installed.indexOf(installed) === -1) state.installed.push(installed);
          state.current = installed;
          addOutput(installed + ' 已安装并设为当前版本。');
        } else addOutput('请输入版本号，例如：nvm install 22.21.1');
      } else if (command === 'clear') state.output = [];
      else addOutput('无法识别：' + command + '。可用：nvm list / nvm use / nvm install / nvm current');
      render();
    }

    function render() {
      var versions = state.installed.map(function (version) {
        var current = version === state.current;
        return '<button type="button" class="lab-version' + (current ? ' active' : '') + '" data-nvm-command="nvm use ' + version + '" aria-pressed="' + current + '"><span>' + version + '</span><small>' + (current ? '正在使用' : '点击切换') + '</small></button>';
      }).join('');
      var body = '<div class="lab-stat-row"><div><span>当前运行时</span><strong class="lab-current-version">' + state.current + '</strong></div><span class="lab-badge">LTS</span></div>' +
        '<div class="lab-version-grid">' + versions + '<button type="button" class="lab-version lab-version-add" data-nvm-command="nvm install 20.19.6"><span>+ v20.19.6</span><small>安装并切换</small></button></div>' +
        '<pre class="lab-command-output" aria-live="polite">' + escapeHtml(state.output.join('\n')) + '</pre>' +
        '<div class="lab-command-row"><span aria-hidden="true">$</span><input class="lab-command-input" aria-label="输入 nvm 命令" placeholder="例如：nvm use 22" autocomplete="off"><button type="button" data-nvm-run>执行</button></div>';
      demo.innerHTML = labShell('Node 版本管理', '一个项目，一套可切换的运行时', '点击版本立即切换，或在命令栏中体验常见 nvm 指令。', body);
    }

    demo.addEventListener('click', function (event) {
      var commandButton = event.target.closest('[data-nvm-command]');
      if (commandButton) runCommand(commandButton.getAttribute('data-nvm-command'));
      if (event.target.closest('[data-nvm-run]')) {
        var input = demo.querySelector('.lab-command-input');
        runCommand(input.value);
      }
    });
    demo.addEventListener('keydown', function (event) {
      if (event.target.classList.contains('lab-command-input') && event.key === 'Enter') {
        event.preventDefault();
        runCommand(event.target.value);
      }
    });
    demo.dataset.ch01LabsReady = 'true';
    render();
  }

  function initTerminalDemo(terminal) {
    var state = { lines: ['欢迎来到 Terminal Pro。输入 help 查看可运行的命令。'], history: [], cursor: 0 };
    var replies = {
      help: '可用命令：help、pwd、ls、node -v、npm -v、clear',
      pwd: '/Users/learner/tpvibe',
      ls: 'package.json   src/   public/   README.md',
      'node -v': 'v24.12.0',
      'npm -v': '11.6.2'
    };

    function render() {
      var body = '<pre class="lab-command-output lab-terminal-output" aria-live="polite">' + escapeHtml(state.lines.join('\n')) + '</pre>' +
        '<div class="lab-command-row"><span aria-hidden="true">learner@tpvibe:~ $</span><input class="lab-command-input lab-terminal-input" aria-label="Terminal 命令输入" placeholder="输入 help、pwd、ls…" autocomplete="off"><button type="button" data-terminal-run>运行</button><button type="button" class="lab-quiet-button" data-terminal-clear>清屏</button></div>' +
        '<p class="shortcuts">提示：按 <span class="shortcut">↑</span>/<span class="shortcut">↓</span> 浏览历史；<span class="shortcut">Ctrl</span> + <span class="shortcut">L</span> 清屏。</p>';
      terminal.innerHTML = labShell('命令行练习', '小范围、可预期地试验命令', '这是安全的教学终端：只回应本页列出的本地示例命令，不会执行系统操作。', body);
    }

    function runCommand(value) {
      var command = value.trim();
      if (!command) return;
      if (command === 'clear') { state.lines = []; render(); return; }
      state.history.push(command);
      state.cursor = state.history.length;
      state.lines.push('$ ' + command, replies[command] || 'command not found: ' + command + '（试试输入 help）');
      state.lines = state.lines.slice(-12);
      render();
    }

    terminal.addEventListener('click', function (event) {
      if (event.target.closest('[data-terminal-clear]')) { state.lines = []; render(); return; }
      if (event.target.closest('[data-terminal-run]')) runCommand(terminal.querySelector('.lab-terminal-input').value);
    });
    terminal.addEventListener('keydown', function (event) {
      if (!event.target.classList.contains('lab-terminal-input')) return;
      if (event.ctrlKey && event.key.toLowerCase() === 'l') { event.preventDefault(); state.lines = []; render(); return; }
      if (event.key === 'Enter') { event.preventDefault(); runCommand(event.target.value); return; }
      if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
        event.preventDefault();
        state.cursor += event.key === 'ArrowUp' ? -1 : 1;
        state.cursor = Math.max(0, Math.min(state.history.length, state.cursor));
        event.target.value = state.history[state.cursor] || '';
      }
    });
    terminal.dataset.ch01LabsReady = 'true';
    render();
  }

  function initPackageExplorer(list) {
    var packages = [
      ['react', 'UI 框架', '用组件构建可组合的用户界面'], ['vue', 'UI 框架', '渐进式前端框架'],
      ['next', '全栈框架', 'React 的全栈框架，支持服务端渲染'], ['express', '后端框架', '简洁的 Node.js Web 服务框架'],
      ['axios', 'HTTP 请求', '浏览器与 Node.js 的请求客户端'], ['zod', '工具库', 'TypeScript 优先的数据校验'],
      ['tailwindcss', 'CSS 框架', '原子化 CSS 工具集'], ['zustand', '状态管理', '小而直接的状态管理库']
    ];
    var categories = ['全部', 'UI 框架', '全栈框架', '后端框架', 'HTTP 请求', '工具库', 'CSS 框架', '状态管理'];
    var selected = '全部';

    function render() {
      var filtered = packages.filter(function (item) { return selected === '全部' || item[1] === selected; });
      var tabs = categories.map(function (category) { return '<button type="button" class="lab-filter' + (category === selected ? ' active' : '') + '" data-package-category="' + category + '" aria-pressed="' + (category === selected) + '">' + category + '</button>'; }).join('');
      var cards = filtered.map(function (item) { return '<article class="lab-package-card"><div><code>' + item[0] + '</code><span>' + item[1] + '</span></div><p>' + item[2] + '</p></article>'; }).join('');
      var body = '<div class="lab-filter-row" role="toolbar" aria-label="按分类筛选代码包">' + tabs + '</div><p class="lab-result-count" aria-live="polite">显示 ' + filtered.length + ' 个「' + selected + '」常用包</p><div class="lab-package-grid">' + cards + '</div>';
      list.innerHTML = labShell('开源生态', '从用途开始挑选依赖，而不是盲目安装', '筛选后可以快速看到每类工具解决的核心问题。', body);
    }

    list.addEventListener('click', function (event) {
      var button = event.target.closest('[data-package-category]');
      if (!button) return;
      selected = button.getAttribute('data-package-category');
      render();
    });
    list.dataset.ch01LabsReady = 'true';
    render();
  }

  function initPnpmInstall(simulator) {
    var steps = ['读取 package.json', '解析依赖图', '复用全局内容仓库', '链接 node_modules'];
    var state = { progress: 0, running: false, completed: false, timer: null };

    function render() {
      var activeStep = Math.min(steps.length - 1, Math.floor(state.progress / 25));
      var stepMarkup = steps.map(function (step, index) {
        var status = state.completed || index < activeStep ? '完成' : index === activeStep && state.running ? '进行中' : '等待中';
        return '<li class="lab-step ' + (status === '完成' ? 'is-complete' : status === '进行中' ? 'is-active' : '') + '"><span>' + (status === '完成' ? '✓' : index + 1) + '</span><div><strong>' + step + '</strong><small>' + status + '</small></div></li>';
      }).join('');
      var action = state.running ? '安装中…' : state.completed ? '再次演示' : '开始安装';
      var body = '<div class="lab-progress-meta"><strong aria-live="polite">' + state.progress + '%</strong><span>' + (state.completed ? '依赖已就绪，可以启动开发服务器。' : 'pnpm 通过内容寻址仓库减少重复下载。') + '</span></div><div class="lab-progress" aria-label="安装进度"><span class="lab-progress-fill" style="width:' + state.progress + '%"></span></div><ol class="lab-step-list">' + stepMarkup + '</ol><button type="button" data-pnpm-run ' + (state.running ? 'disabled' : '') + '>' + action + '</button>';
      simulator.innerHTML = labShell('pnpm 安装过程', '把等待过程拆成可理解的四步', '点击开始，观察解析、复用与链接如何依次完成。', body);
    }

    function run() {
      if (state.running) return;
      if (state.completed) { state.progress = 0; state.completed = false; }
      state.running = true;
      render();
      state.timer = window.setInterval(function () {
        state.progress = Math.min(100, state.progress + 10);
        if (state.progress === 100) { window.clearInterval(state.timer); state.running = false; state.completed = true; }
        render();
      }, 180);
    }

    simulator.addEventListener('click', function (event) { if (event.target.closest('[data-pnpm-run]')) run(); });
    simulator.dataset.ch01LabsReady = 'true';
    render();
  }

  function initFileTree(tree) {
    var state = { src: true, public: false, validated: false };
    function folder(key, label, description, children) {
      var expanded = state[key];
      return '<li><button type="button" class="lab-tree-node" data-tree-folder="' + key + '" aria-expanded="' + expanded + '"><span>' + (expanded ? '▾' : '▸') + '</span><strong>📁 ' + label + '</strong><small>' + description + '</small></button>' + (expanded ? '<ul>' + children + '</ul>' : '') + '</li>';
    }
    function render() {
      var source = '<li class="lab-tree-leaf">📄 <code>main.ts</code><small>应用入口</small></li><li class="lab-tree-leaf">📄 <code>App.tsx</code><small>页面组件</small></li>';
      var publicFiles = '<li class="lab-tree-leaf">📄 <code>favicon.svg</code><small>静态资源</small></li>';
      var body = '<ul class="lab-tree">' + folder('src', 'src', '你手写的业务代码', source) + folder('public', 'public', '不经打包直接输出的资源', publicFiles) + '<li class="lab-tree-leaf">⚙️ <code>package.json</code><small>依赖和脚本</small></li></ul><div class="lab-inline-actions"><button type="button" data-tree-validate>检查命名</button><p class="lab-notice" aria-live="polite">' + (state.validated ? '✓ 路径检查通过：仅使用英文、小写、连字符或下划线。' : '建议：项目根路径避免中文、空格与特殊符号。') + '</p></div>';
      tree.innerHTML = labShell('项目结构', '文件夹名称也是运行环境的一部分', '展开目录，了解源码、静态资源和项目配置各自放在哪里。', body);
    }
    tree.addEventListener('click', function (event) {
      var folderButton = event.target.closest('[data-tree-folder]');
      if (folderButton) { var key = folderButton.getAttribute('data-tree-folder'); state[key] = !state[key]; render(); return; }
      if (event.target.closest('[data-tree-validate]')) { state.validated = true; render(); }
    });
    tree.dataset.ch01LabsReady = 'true';
    render();
  }

  function initNetworkPorts(network) {
    var state = { port: null, connected: false };
    var ports = [['3000', 'Next.js 开发服务器'], ['5173', 'Vite 开发服务器'], ['5432', 'PostgreSQL 数据库']];
    function render() {
      var cards = ports.map(function (item) {
        var selected = state.port === item[0];
        return '<button type="button" class="lab-port-card' + (selected ? ' active' : '') + '" data-port="' + item[0] + '" aria-pressed="' + selected + '"><code>:' + item[0] + '</code><span>' + item[1] + '</span></button>';
      }).join('');
      var address = state.connected ? 'http://localhost:' + state.port : 'http://localhost:????';
      var message = state.connected ? '已连接到本地服务；浏览器正访问 ' + address : state.port ? '已选择 ' + state.port + '，现在可以发起连接。' : '先选一个端口，再连接到本地服务。';
      var body = '<div class="lab-browser-preview"><span class="lab-browser-dots" aria-hidden="true">● ● ●</span><code>' + address + '</code><strong class="lab-connection-state' + (state.connected ? ' is-connected' : '') + '">' + (state.connected ? '服务响应 200 OK' : '等待连接') + '</strong></div><div class="lab-port-grid">' + cards + '</div><div class="lab-inline-actions"><button type="button" data-network-connect ' + (state.port ? '' : 'disabled') + '>连接 localhost</button><button type="button" class="lab-quiet-button" data-network-reset>重置</button><p class="lab-notice" aria-live="polite">' + message + '</p></div>';
      network.innerHTML = labShell('Localhost 与端口', '端口像一栋楼中的房间号', '同一台电脑可以运行多个服务，只要它们分别监听不同端口。', body);
    }
    network.addEventListener('click', function (event) {
      var portButton = event.target.closest('[data-port]');
      if (portButton) { state.port = portButton.getAttribute('data-port'); state.connected = false; render(); return; }
      if (event.target.closest('[data-network-connect]') && state.port) { state.connected = true; render(); return; }
      if (event.target.closest('[data-network-reset]')) { state.port = null; state.connected = false; render(); }
    });
    network.dataset.ch01LabsReady = 'true';
    render();
  }

  function initTroubleshoot(lab) {
    var steps = [
      { icon: '🔤', title: '拼写检查', description: '先确认命令没有多余空格或拼写错误。', expected: 'pnpm dev', hint: '试试：pnpm dev' },
      { icon: '✅', title: '工具已安装', description: '确认 Node.js 等运行环境已经安装并可被终端找到。', expected: 'node -v', hint: '试试：node -v' },
      { icon: '📁', title: '正确目录', description: '检查自己是否真的在项目根目录中执行命令。', expected: 'pwd', hint: '试试：pwd' },
      { icon: '🔄', title: '重新加载', description: '配置修改后，重新载入终端配置再试一次。', expected: 'source ~/.zshrc', hint: '试试：source ~/.zshrc' }
    ];
    var state = { current: 0, checked: [], feedback: '从第一步开始，输入建议命令后按回车验证。' };

    function normalise(value) { return value.trim().replace(/\s+/g, ' '); }
    function render() {
      var active = steps[state.current];
      var stepButtons = steps.map(function (step, index) {
        var complete = state.checked.indexOf(index) > -1;
        return '<button type="button" class="lab-troubleshoot-step' + (index === state.current ? ' active' : '') + (complete ? ' is-complete' : '') + '" data-troubleshoot-step="' + index + '" aria-current="' + (index === state.current ? 'step' : 'false') + '"><span>' + (complete ? '✓' : step.icon) + '</span><strong>' + step.title + '</strong></button>';
      }).join('');
      var completed = state.checked.length === steps.length;
      var body = '<div class="lab-troubleshoot-steps" aria-label="命令排查步骤">' + stepButtons + '</div>' +
        '<div class="lab-troubleshoot-current"><p class="lab-kicker">第 ' + (state.current + 1) + ' 步</p><h4>' + active.icon + ' ' + active.title + '</h4><p>' + active.description + '</p><p class="lab-command-hint">' + active.hint + '</p></div>' +
        '<div class="lab-command-row"><span aria-hidden="true">$</span><input class="lab-command-input lab-troubleshoot-input" aria-label="输入排查命令" placeholder="' + active.expected + '" autocomplete="off"><button type="button" data-troubleshoot-run>验证</button><button type="button" class="lab-quiet-button" data-troubleshoot-reset>重新开始</button></div>' +
        '<p class="lab-notice" aria-live="polite">' + (completed ? '✓ 排查完成：现在你有一条可重复使用的终端排错路径。' : state.feedback) + '</p>';
      lab.innerHTML = labShell('终端排错', '把报错拆成四个可执行的检查', '每一步都有明确目的；回答不匹配时会给出下一步提示，而不是留在空白界面。', body);
    }

    function validate(value) {
      var expected = steps[state.current].expected;
      if (normalise(value) === expected) {
        if (state.checked.indexOf(state.current) === -1) state.checked.push(state.current);
        if (state.current < steps.length - 1) { state.current += 1; state.feedback = '✓ 这一项没问题，继续下一步。'; }
        else state.feedback = '✓ 所有基础检查都已完成。';
      } else state.feedback = '还不完全匹配。' + steps[state.current].hint;
      render();
    }

    lab.addEventListener('click', function (event) {
      var stepButton = event.target.closest('[data-troubleshoot-step]');
      if (stepButton) { state.current = Number(stepButton.getAttribute('data-troubleshoot-step')); render(); return; }
      if (event.target.closest('[data-troubleshoot-run]')) validate(lab.querySelector('.lab-troubleshoot-input').value);
      if (event.target.closest('[data-troubleshoot-reset]')) { state = { current: 0, checked: [], feedback: '已重新开始；从拼写检查开始。' }; render(); }
    });
    lab.addEventListener('keydown', function (event) {
      if (event.target.classList.contains('lab-troubleshoot-input') && event.key === 'Enter') { event.preventDefault(); validate(event.target.value); }
    });
    lab.dataset.ch01LabsReady = 'true';
    render();
  }

  function initChapterLabs() {
    document.querySelectorAll('.interactive-demo').forEach(initInteractiveDemo);
    document.querySelectorAll('.nvm-demo').forEach(initNvmDemo);
    document.querySelectorAll('.terminal-pro').forEach(initTerminalDemo);
    document.querySelectorAll('.package-list').forEach(initPackageExplorer);
    document.querySelectorAll('.pnpm-install').forEach(initPnpmInstall);
    document.querySelectorAll('.fs-tree').forEach(initFileTree);
    document.querySelectorAll('.network-ports').forEach(initNetworkPorts);
    document.querySelectorAll('.terminal-troubleshoot').forEach(initTroubleshoot);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initChapterLabs);
  else initChapterLabs();
}());
