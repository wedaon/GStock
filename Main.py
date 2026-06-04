<!DOCTYPE html>
<html lang="ko" class="dark"> <head>
    <title>School Stock Exchange</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script>
        // 테마 전환 스크립트
        function toggleTheme() {
            const html = document.documentElement;
            if (html.classList.contains('dark')) {
                html.classList.remove('dark');
                localStorage.theme = 'light';
            } else {
                html.classList.add('dark');
                localStorage.theme = 'dark';
            }
        }
    </script>
    <style>
        /* 커스텀 블루 포인트 (검-파 / 화-파 조합용) */
        .theme-blue { color: #3b82f6; }
        .bg-theme-blue { background-color: #3b82f6; }
    </style>
</head>

<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300 p-6">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-center mb-10 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl transition-all">
            <div class="flex items-center gap-4">
                <div class="bg-blue-600 p-3 rounded-2xl text-white shadow-lg shadow-blue-500/30">
                    <i class="fas fa-chart-line text-2xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-black tracking-tight">SCHOOL EXCHANGE</h1>
                    <p class="text-slate-400 dark:text-slate-500 text-xs font-bold uppercase tracking-widest">
                        Welcome, {{ session['user_id'] }}
                    </p>
                </div>
            </div>

            <div class="flex items-center gap-8">
                <button onclick="toggleTheme()" class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-yellow-400 flex items-center justify-center hover:scale-105 transition-all border border-slate-200 dark:border-slate-700">
                    <i class="fas fa-sun dark:hidden"></i>
                    <i class="fas fa-moon hidden dark:block"></i>
                </button>

                <div class="text-right hidden sm:block">
                    <p class="text-slate-400 text-[10px] font-black uppercase">Balance</p>
                    <p class="text-2xl font-mono text-blue-600 dark:text-blue-400 font-black">1,000,000원</p>
                </div>
                
                <a href="/logout" class="text-slate-400 hover:text-rose-500 transition-colors text-xl">
                    <i class="fas fa-sign-out-alt"></i>
                </a>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2 space-y-6">
                <h2 class="text-xl font-black flex items-center gap-3 ml-2">
                    <i class="fas fa-list text-blue-500"></i> Market List
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    {% for stock in stocks %}
                    <div class="bg-white dark:bg-slate-900 p-5 rounded-[2rem] border border-slate-200 dark:border-slate-800 hover:border-blue-500/50 transition-all shadow-md dark:shadow-none group">
                        <div class="flex justify-between items-center mb-5">
                            <div class="flex items-center gap-3">
                                <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center font-black">
                                    {{ stock[0] }}
                                </div>
                                <div>
                                    <h3 class="font-black text-slate-800 dark:text-slate-100">{{ stock }}</h3>
                                    <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                                        +2.45%
                                    </span>
                                </div>
                            </div>
                            <p class="font-mono font-bold text-slate-700 dark:text-slate-300">14,200원</p>
                        </div>
                        
                        <div class="flex gap-2 bg-slate-50 dark:bg-slate-950 p-3 rounded-2xl border border-slate-100 dark:border-slate-800">
                            <input type="number" placeholder="0" class="w-full bg-transparent focus:outline-none text-sm font-bold">
                            <button class="bg-blue-600 text-white px-4 py-2 rounded-xl text-xs font-black shadow-md shadow-blue-500/20 active:scale-95 transition-all">TRADE</button>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div class="space-y-8">
                <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-7 border border-slate-200 dark:border-slate-800 shadow-xl">
                    <h2 class="text-lg font-black mb-6 text-blue-600 dark:text-blue-500 uppercase italic">Leaderboard</h2>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center p-4 bg-slate-50 dark:bg-slate-950 rounded-2xl border border-slate-100 dark:border-white/5">
                            <span class="text-blue-600 font-black italic">#1</span>
                            <span class="font-bold text-slate-700 dark:text-slate-300">포지티브 대장</span>
                            <span class="text-sm font-mono font-bold text-blue-500">2.5M</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
