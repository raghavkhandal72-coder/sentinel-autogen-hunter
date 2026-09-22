"""Interactive Web Download & Installation Hub for Sentinel-AutoGen-Hunter.

Modeled after the OpenClaw.ai installation portal with modern dark-mode aesthetics,
interactive platform switchers, 1-click copy codeblocks, and direct desktop downloads.
"""

INSTALL_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Install Sentinel-AutoGen-Hunter | OpenClaw Gateway & Zero-Trust Defense</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700;800&family=Orbitron:wght@600;800;900&family=Inter:wght@400;500;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background-color: #080c14;
            color: #d1d5db;
        }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .orbitron { font-family: 'Orbitron', sans-serif; }
        .cyber-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.90) 0%, rgba(10, 15, 26, 0.98) 100%);
            border: 1px solid rgba(0, 255, 136, 0.2);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(16px);
        }
        .cyber-card:hover {
            border-color: rgba(0, 216, 255, 0.45);
            box-shadow: 0 0 25px rgba(0, 216, 255, 0.2);
        }
        .glow-emerald { text-shadow: 0 0 12px rgba(0, 255, 136, 0.6); }
        .glow-cyan { text-shadow: 0 0 12px rgba(0, 216, 255, 0.6); }
        .active-tab {
            background: linear-gradient(90deg, rgba(0,255,136,0.15), rgba(0,216,255,0.15));
            border-color: #00ff88;
            color: #00ff88;
        }
        pre, code { font-family: 'JetBrains Mono', monospace; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #080c14; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #00ff88; }
    </style>
</head>
<body class="min-h-screen flex flex-col p-4 md:p-8">

    <!-- Top Navigation Bar -->
    <header class="flex flex-col md:flex-row items-center justify-between pb-6 mb-8 border-b border-emerald-500/20 gap-4">
        <div class="flex items-center space-x-4">
            <a href="/" class="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-400/40 flex items-center justify-center text-emerald-400 text-2xl shadow-[0_0_15px_rgba(0,255,136,0.3)] hover:scale-105 transition-transform">
                🛡️
            </a>
            <div>
                <a href="/" class="text-2xl md:text-3xl font-black orbitron tracking-wider text-white hover:text-emerald-400 transition-colors">
                    SENTINEL-<span class="text-emerald-400">AUTOGEN</span>-HUNTER
                </a>
                <p class="text-xs text-gray-400 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    Powered by OpenClaw Multi-Channel Gateway Engine · v1.4.0
                </p>
            </div>
        </div>

        <nav class="flex items-center gap-2 md:gap-4 text-xs md:text-sm font-medium">
            <a href="/install" class="px-4 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 flex items-center gap-2 font-bold shadow-[0_0_10px_rgba(0,255,136,0.2)]">
                <i class="fa-solid fa-download"></i> Install
            </a>
            <a href="/dashboard" class="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-gray-300 hover:text-emerald-400 hover:border-emerald-500/30 transition-all flex items-center gap-2">
                <i class="fa-solid fa-gauge-high"></i> Cyber SOC
            </a>
            <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter" target="_blank" class="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-gray-300 hover:text-white hover:border-slate-500 transition-all flex items-center gap-2">
                <i class="fa-brands fa-github"></i> GitHub
            </a>
        </nav>
    </header>

    <!-- Main Content Container -->
    <main class="max-w-5xl mx-auto w-full flex-1">

        <!-- Hero Section -->
        <div class="text-center mb-10">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4">
                <i class="fa-solid fa-bolt"></i> Open-Source · Runs on your machine · Zero-Trust Secured
            </div>
            <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight mb-4 orbitron">
                The Autonomous Agent & Defense Suite That <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 glow-emerald">Really Protects</span>.
            </h1>
            <p class="text-gray-300 text-base md:text-lg max-w-2xl mx-auto">
                Connects across WhatsApp, Telegram, Discord, Slack, and your desktop companion — while shielding your system from prompt injections, destructive tools, and secret leakage.
            </p>
        </div>

        <!-- Installation Terminal & Tab Box -->
        <div class="cyber-card rounded-2xl p-6 md:p-8 mb-10">
            <!-- Mode Switcher Tabs -->
            <div class="flex flex-wrap items-center justify-between pb-4 mb-6 border-b border-slate-800 gap-3">
                <div class="flex items-center gap-2" id="modeTabs">
                    <button onclick="setMode('apps')" id="tab-apps" class="px-4 py-2 rounded-lg text-sm font-semibold border border-transparent text-gray-400 hover:text-white transition-all active-tab">
                        <i class="fa-solid fa-desktop mr-1.5"></i> Desktop Apps
                    </button>
                    <button onclick="setMode('oneliner')" id="tab-oneliner" class="px-4 py-2 rounded-lg text-sm font-semibold border border-transparent text-gray-400 hover:text-white transition-all">
                        <i class="fa-solid fa-terminal mr-1.5"></i> One-Liner
                    </button>
                    <button onclick="setMode('pip')" id="tab-pip" class="px-4 py-2 rounded-lg text-sm font-semibold border border-transparent text-gray-400 hover:text-white transition-all">
                        <i class="fa-brands fa-python mr-1.5"></i> pip
                    </button>
                    <button onclick="setMode('hackable')" id="tab-hackable" class="px-4 py-2 rounded-lg text-sm font-semibold border border-transparent text-gray-400 hover:text-white transition-all">
                        <i class="fa-solid fa-code mr-1.5"></i> Source / Git
                    </button>
                </div>

                <!-- Sub OS Switcher (Only visible for one-liner) -->
                <div id="osSwitcher" class="hidden flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
                    <button onclick="setOs('windows')" id="os-windows" class="px-3 py-1.5 rounded-md text-emerald-400 font-bold bg-slate-800">Windows</button>
                    <button onclick="setModeOs('unix')" id="os-unix" class="px-3 py-1.5 rounded-md text-gray-400 hover:text-white">macOS & Linux</button>
                </div>
            </div>

            <!-- MODE 1: Desktop Apps Grid (Default) -->
            <div id="content-apps" class="space-y-6">
                <div class="text-sm text-gray-400 mb-4">
                    Full desktop apps and instant launchers that set up everything for you — Gateway, Agent Shield, Multi-Channel Bot, and Companion GUI.
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Windows App Card -->
                    <div class="bg-slate-900/80 border border-emerald-500/30 rounded-xl p-6 relative overflow-hidden flex flex-col justify-between hover:border-emerald-400 transition-all shadow-[0_0_15px_rgba(0,255,136,0.1)]">
                        <div class="absolute -top-3 -right-3 w-16 h-16 bg-emerald-500/10 rounded-full blur-xl"></div>
                        <div>
                            <div class="flex items-center justify-between mb-3">
                                <span class="font-bold text-lg text-white flex items-center gap-2">
                                    <i class="fa-brands fa-windows text-cyan-400"></i> Windows
                                </span>
                                <span class="text-xs bg-emerald-500/20 text-emerald-400 font-bold px-2 py-0.5 rounded">Featured</span>
                            </div>
                            <p class="text-xs text-gray-400 mb-6">Windows 10 / 11 · x64 & ARM64 · Companion App v1.4.0</p>
                        </div>
                        <div class="space-y-2">
                            <a href="https://raw.githubusercontent.com/raghavkhandal72-coder/sentinel-autogen-hunter/main/SentinelCompanion-Setup.bat" download class="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 hover:opacity-95 transition-opacity shadow-lg">
                                <i class="fa-solid fa-download"></i> Download Windows Launcher (.bat)
                            </a>
                            <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/tags/v1.4.0.zip" class="w-full py-2 px-4 rounded-lg bg-slate-800 text-gray-300 hover:text-white font-medium text-xs flex items-center justify-center gap-2 border border-slate-700 transition-colors">
                                <i class="fa-solid fa-file-zipper"></i> Source Release (.zip)
                            </a>
                        </div>
                    </div>

                    <!-- macOS App Card -->
                    <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all">
                        <div>
                            <div class="flex items-center justify-between mb-3">
                                <span class="font-bold text-lg text-white flex items-center gap-2">
                                    <i class="fa-brands fa-apple text-gray-200"></i> macOS
                                </span>
                            </div>
                            <p class="text-xs text-gray-400 mb-6">macOS 12+ · Apple Silicon (M1/M2/M3) & Intel · v1.4.0</p>
                        </div>
                        <div class="space-y-2">
                            <button onclick="setMode('oneliner'); setModeOs('unix');" class="w-full py-2.5 px-4 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/40 font-bold text-xs flex items-center justify-center gap-2 transition-colors">
                                <i class="fa-solid fa-terminal"></i> Run 1-Liner Script
                            </button>
                            <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/tags/v1.4.0.tar.gz" class="w-full py-2 px-4 rounded-lg bg-slate-800 text-gray-300 hover:text-white font-medium text-xs flex items-center justify-center gap-2 border border-slate-700 transition-colors">
                                <i class="fa-solid fa-file-zipper"></i> Tarball (.tar.gz)
                            </a>
                        </div>
                    </div>

                    <!-- Linux App Card -->
                    <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all">
                        <div>
                            <div class="flex items-center justify-between mb-3">
                                <span class="font-bold text-lg text-white flex items-center gap-2">
                                    <i class="fa-brands fa-linux text-yellow-400"></i> Linux
                                </span>
                            </div>
                            <p class="text-xs text-gray-400 mb-6">Ubuntu, Debian, Fedora, Arch · x64 & aarch64 · v1.4.0</p>
                        </div>
                        <div class="space-y-2">
                            <button onclick="setMode('oneliner'); setModeOs('unix');" class="w-full py-2.5 px-4 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/40 font-bold text-xs flex items-center justify-center gap-2 transition-colors">
                                <i class="fa-solid fa-terminal"></i> Run 1-Liner Script
                            </button>
                            <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/tags/v1.4.0.tar.gz" class="w-full py-2 px-4 rounded-lg bg-slate-800 text-gray-300 hover:text-white font-medium text-xs flex items-center justify-center gap-2 border border-slate-700 transition-colors">
                                <i class="fa-solid fa-file-zipper"></i> Tarball (.tar.gz)
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODE 2: One-Liner Content -->
            <div id="content-oneliner" class="hidden space-y-4">
                <div class="text-sm text-gray-400">
                    Paste this command into your terminal. Sets up Python virtual environment, dependencies, runs test verification, and launches the app automatically.
                </div>

                <!-- Windows Command Block -->
                <div id="cmd-block-windows" class="bg-slate-950 rounded-xl p-4 border border-slate-800 relative group">
                    <div class="text-xs text-gray-500 mb-2 font-mono"># Windows PowerShell (Run as regular user):</div>
                    <div class="flex items-center justify-between">
                        <code class="text-emerald-400 font-mono text-sm break-all" id="win-code">irm https://raw.githubusercontent.com/raghavkhandal72-coder/sentinel-autogen-hunter/main/install.ps1 | iex</code>
                        <button onclick="copyCode('win-code')" class="ml-4 p-2 bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-xs font-mono">
                            <i class="fa-regular fa-copy"></i> <span class="copy-text">Copy</span>
                        </button>
                    </div>
                </div>

                <!-- Unix Command Block -->
                <div id="cmd-block-unix" class="hidden bg-slate-950 rounded-xl p-4 border border-slate-800 relative group">
                    <div class="text-xs text-gray-500 mb-2 font-mono"># macOS & Linux Terminal:</div>
                    <div class="flex items-center justify-between">
                        <code class="text-cyan-400 font-mono text-sm break-all" id="unix-code">curl -fsSL https://raw.githubusercontent.com/raghavkhandal72-coder/sentinel-autogen-hunter/main/install.sh | bash</code>
                        <button onclick="copyCode('unix-code')" class="ml-4 p-2 bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-xs font-mono">
                            <i class="fa-regular fa-copy"></i> <span class="copy-text">Copy</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- MODE 3: pip Content -->
            <div id="content-pip" class="hidden space-y-4">
                <div class="text-sm text-gray-400">
                    Install or update directly via Python's package manager:
                </div>

                <div class="bg-slate-950 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
                    <div>
                        <div class="text-xs text-gray-500 mb-1 font-mono"># 1. Install Sentinel package:</div>
                        <code class="text-emerald-400 font-mono text-sm" id="pip-code">pip install -U git+https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git</code>
                    </div>
                    <button onclick="copyCode('pip-code')" class="p-2 bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-xs font-mono">
                        <i class="fa-regular fa-copy"></i> <span class="copy-text">Copy</span>
                    </button>
                </div>

                <div class="bg-slate-950 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
                    <div>
                        <div class="text-xs text-gray-500 mb-1 font-mono"># 2. Launch the desktop companion or CLI:</div>
                        <code class="text-cyan-400 font-mono text-sm" id="pip-launch-code">python -m cli.main companion</code>
                    </div>
                    <button onclick="copyCode('pip-launch-code')" class="p-2 bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-xs font-mono">
                        <i class="fa-regular fa-copy"></i> <span class="copy-text">Copy</span>
                    </button>
                </div>
            </div>

            <!-- MODE 4: Source (Hackable) Content -->
            <div id="content-hackable" class="hidden space-y-4">
                <div class="text-sm text-gray-400">
                    For developers and contributors who want full source control and local hacking:
                </div>

                <div class="bg-slate-950 rounded-xl p-4 border border-slate-800 relative">
                    <button onclick="copyCode('git-code')" class="absolute top-3 right-3 p-2 bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-xs font-mono">
                        <i class="fa-regular fa-copy"></i> <span class="copy-text">Copy</span>
                    </button>
                    <pre class="text-gray-300 font-mono text-sm leading-relaxed" id="git-code"><span class="text-emerald-400">git</span> clone https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git
<span class="text-emerald-400">cd</span> sentinel-autogen-hunter
<span class="text-emerald-400">pip</span> install -e .
<span class="text-cyan-400">python</span> companion.py</pre>
                </div>
            </div>
        </div>

        <!-- Zero-Trust Architecture Highlights Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div class="cyber-card p-5 rounded-xl">
                <div class="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl mb-3">
                    🦅
                </div>
                <h3 class="text-white font-bold text-sm mb-1.5">OpenClaw Gateway Core</h3>
                <p class="text-xs text-gray-400 leading-relaxed">
                    Native multi-channel messaging across WhatsApp, Telegram, Discord, Slack, and Companion with OpenAI-compatible REST endpoints.
                </p>
            </div>

            <div class="cyber-card p-5 rounded-xl">
                <div class="w-10 h-10 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center text-xl mb-3">
                    🛡️
                </div>
                <h3 class="text-white font-bold text-sm mb-1.5">Sub-3ms Agent Shield</h3>
                <p class="text-xs text-gray-400 leading-relaxed">
                    Zero-trust gatekeeper blocking prompt injections, jailbreaks, destructive shell calls (<code class="text-rose-400">rm -rf /</code>), and credential dumping.
                </p>
            </div>

            <div class="cyber-card p-5 rounded-xl">
                <div class="w-10 h-10 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center text-xl mb-3">
                    🪤
                </div>
                <h3 class="text-white font-bold text-sm mb-1.5">Active Canary Deception</h3>
                <p class="text-xs text-gray-400 leading-relaxed">
                    Deploys fake AWS keys and GitHub decoy tokens in agent workspaces. Triggers instant Netfilter kernel containment upon touch.
                </p>
            </div>
        </div>

        <!-- Footer -->
        <footer class="pt-8 border-t border-slate-800/80 text-center text-xs text-gray-500 pb-8">
            <p>Architected by <span class="text-gray-300 font-semibold">Raghav Khandal</span> (@raghavkhandal72-coder)</p>
            <p class="mt-1">Released under the MIT License · GitHub Repository: <a href="https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter" target="_blank" class="text-emerald-400 hover:underline">sentinel-autogen-hunter</a></p>
        </footer>

    </main>

    <!-- Client-side tab & copy handler -->
    <script>
        function setMode(mode) {
            ['apps', 'oneliner', 'pip', 'hackable'].forEach(m => {
                const tab = document.getElementById('tab-' + m);
                const content = document.getElementById('content-' + m);
                if (m === mode) {
                    tab.classList.add('active-tab');
                    content.classList.remove('hidden');
                } else {
                    tab.classList.remove('active-tab');
                    content.classList.add('hidden');
                }
            });

            const osSwitcher = document.getElementById('osSwitcher');
            if (mode === 'oneliner') {
                osSwitcher.classList.remove('hidden');
            } else {
                osSwitcher.classList.add('hidden');
            }
        }

        function setModeOs(os) {
            const winBtn = document.getElementById('os-windows');
            const unixBtn = document.getElementById('os-unix');
            const winBlock = document.getElementById('cmd-block-windows');
            const unixBlock = document.getElementById('cmd-block-unix');

            if (os === 'windows') {
                winBtn.className = 'px-3 py-1.5 rounded-md text-emerald-400 font-bold bg-slate-800';
                unixBtn.className = 'px-3 py-1.5 rounded-md text-gray-400 hover:text-white';
                winBlock.classList.remove('hidden');
                unixBlock.classList.add('hidden');
            } else {
                unixBtn.className = 'px-3 py-1.5 rounded-md text-emerald-400 font-bold bg-slate-800';
                winBtn.className = 'px-3 py-1.5 rounded-md text-gray-400 hover:text-white';
                unixBlock.classList.remove('hidden');
                winBlock.classList.add('hidden');
            }
        }

        function setOs(os) {
            setModeOs(os);
        }

        function copyCode(elementId) {
            const el = document.getElementById(elementId);
            const text = el.innerText || el.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const btn = event.currentTarget;
                const copyText = btn.querySelector('.copy-text');
                const icon = btn.querySelector('i');
                if (copyText) copyText.innerText = 'Copied!';
                if (icon) icon.className = 'fa-solid fa-check text-emerald-400';
                setTimeout(() => {
                    if (copyText) copyText.innerText = 'Copy';
                    if (icon) icon.className = 'fa-regular fa-copy';
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""
