import customtkinter as ctk
import sqlite3
import random
import threading
import time
from datetime import datetime

# 데이터베이스 설정 및 초기화
def init_db():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    # 유저 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            cash INTEGER,
            total_assets INTEGER
        )
    """)
    # 주식 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            name TEXT PRIMARY KEY,
            price INTEGER,
            prev_price INTEGER,
            trend REAL,
            is_permanent INTEGER
        )
    """)
    # 포트폴리오 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            username TEXT,
            stock_name TEXT,
            amount INTEGER,
            PRIMARY KEY (username, stock_name)
        )
    """)
    # 게시판 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS board (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    
    # 기본 종목 초기 데이터 삽입 (없을 때만)
    cursor.execute("SELECT COUNT(*) FROM stocks")
    if cursor.fetchone()[0] == 0:
        school_stocks = [
            "포지티브", "척력 사무소", "이성애즘", "노즈디", "아이디드",
            "IoT", "플러터", "앱 개발", "모바일 로보틱스", "사이버 보안",
            "클라우드 컴퓨팅", "IT 네트워크", "백앤드", "프론트앤드", "게임 개발",
            "IOS", "안드로이드", "데브옵스", "디자인"
        ]
        general_stocks = ["개미전자", "잡코인", "버블테크", "유령건설", "부실식품"]
        
        for name in school_stocks:
            price = random.randint(10000, 40000)
            cursor.execute("INSERT INTO stocks VALUES (?, ?, ?, 0.0, 1)", (name, price, price))
        for name in general_stocks:
            price = random.randint(1000, 5000)
            cursor.execute("INSERT INTO stocks VALUES (?, ?, ?, 0.0, 0)", (name, price, price))
            
    conn.commit()
    conn.close()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SCHOOL STOCK EXCHANGE (100% Python GUI)")
        self.geometry("1100x750")
        
        # 테마 기본 설정 (검-파 테마)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # DB 초기화
        init_db()
        
        # 상태 변수
        self.current_user = None
        self.active_frames = {}
        self.news_list = []
        
        # 로그인 화면 띄우기
        self.show_login_screen()
        
        # 주가 변동 및 백그라운드 스레드 가동 플래그
        self.running = True
        self.update_thread = threading.Thread(target=self.background_market_loop, daemon=True)
        self.update_thread.start()

    def show_login_screen(self):
        self.clear_screen()
        
        login_frame = ctk.CTkFrame(self, width=400, height=500, corner_radius=24)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.active_frames["login"] = login_frame
        
        # 헤더
        title_label = ctk.CTkLabel(login_frame, text="SCHOOL EXCHANGE", font=("Arial", 28, "bold"), text_color="#3b82f6")
        title_label.pack(pady=(40, 5))
        sub_label = ctk.CTkLabel(login_frame, text="파이썬 가상 주식 거래소 시스템", font=("Arial", 12))
        sub_label.pack(pady=(0, 30))
        
        # 입력창
        self.username_input = ctk.CTkEntry(login_frame, placeholder_text="아이디 입력", width=260, height=45, corner_radius=12)
        self.username_input.pack(pady=10)
        
        self.password_input = ctk.CTkEntry(login_frame, placeholder_text="비밀번호 입력", show="*", width=260, height=45, corner_radius=12)
        self.password_input.pack(pady=10)
        
        # 알림 라벨
        self.info_label = ctk.CTkLabel(login_frame, text="", text_color="#ef4444", font=("Arial", 11))
        self.info_label.pack(pady=5)
        
        # 버튼들
        login_btn = ctk.CTkButton(login_frame, text="로그인", command=self.process_login, width=260, height=45, corner_radius=12, font=("Arial", 14, "bold"))
        login_btn.pack(pady=5)
        
        register_btn = ctk.CTkButton(login_frame, text="신규 가입", command=self.process_register, fg_color="transparent", hover_color="#1e293b", border_width=1, width=260, height=40, corner_radius=12)
        register_btn.pack(pady=10)
        
        # 하단 테마 변경
        theme_btn = ctk.CTkButton(login_frame, text="🌓 화면 모드 전환", command=self.toggle_theme, width=150, height=30, fg_color="transparent")
        theme_btn.pack(pady=(20, 20))

    def process_login(self):
        username = self.username_input.get().strip()
        password = self.password_input.get().strip()
        
        if not username or not password:
            self.info_label.configure(text="아이디와 비밀번호를 모두 입력하세요.")
            return
            
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = username
            self.show_main_screen()
        else:
            self.info_label.configure(text="아이디 또는 비밀번호가 틀렸습니다.")

    def process_register(self):
        username = self.username_input.get().strip()
        password = self.password_input.get().strip()
        
        if len(username) < 2 or len(password) < 4:
            self.info_label.configure(text="아이디 2자 이상, 비밀번호 4자 이상 필요")
            return
            
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        try:
            # 신규 유저는 1,000,000원 기본 지급
            cursor.execute("INSERT INTO users VALUES (?, ?, 1000000, 1000000)", (username, password))
            conn.commit()
            self.info_label.configure(text="가입 완료! 로그인을 진행해 주세요.", text_color="#10b981")
        except sqlite3.IntegrityError:
            self.info_label.configure(text="이미 존재하는 아이디입니다.", text_color="#ef4444")
        finally:
            conn.close()

    def show_main_screen(self):
        self.clear_screen()
        
        # 최상단 대형 프레임 레이아웃
        self.grid_columnconfigure(0, weight=3) # 주식 리스트
        self.grid_columnconfigure(1, weight=1) # 사이드바
        self.grid_rowconfigure(1, weight=1)
        
        # 1. 헤더 영역 (전체 가로 질러 배치)
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=16)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=15, pady=(15, 5))
        
        logo_label = ctk.CTkLabel(header_frame, text="📊 SCHOOL STOCK EXCHANGE", font=("Arial", 20, "bold"), text_color="#3b82f6")
        logo_label.pack(side="left", padx=20)
        
        user_info = ctk.CTkLabel(header_frame, text=f"접속자: {self.current_user}", font=("Arial", 13, "bold"))
        user_info.pack(side="left", padx=20)
        
        # 보유 자산 실시간 갱신 레이블
        self.cash_label = ctk.CTkLabel(header_frame, text="자산: 로딩중...", font=("Arial", 16, "bold"), text_color="#10b981")
        self.cash_label.pack(side="right", padx=20)
        
        logout_btn = ctk.CTkButton(header_frame, text="로그아웃", command=self.logout, width=80, height=32, fg_color="#ef4444", hover_color="#dc2626")
        logout_btn.pack(side="right", padx=10)
        
        theme_btn = ctk.CTkButton(header_frame, text="🌓 모드 전환", command=self.toggle_theme, width=90, height=32, fg_color="transparent", border_width=1)
        theme_btn.pack(side="right", padx=10)

        # 2. 메인 왼쪽 주식 시장 리스트 (스크롤)
        self.market_scroll = ctk.CTkScrollableFrame(self, label_text="실시간 주식 상장 리스트", label_font=("Arial", 14, "bold"))
        self.market_scroll.grid(row=1, column=0, sticky="nsew", padx=(15, 5), pady=(5, 15))
        
        # 3. 우측 사이드 바 (뉴스 피드, 랭킹, 커뮤니티 게시판)
        sidebar_frame = ctk.CTkFrame(self)
        sidebar_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 15), pady=(5, 15))
        
        sidebar_frame.grid_rowconfigure(0, weight=1) # 랭킹
        sidebar_frame.grid_rowconfigure(1, weight=1) # 뉴스
        sidebar_frame.grid_rowconfigure(2, weight=1) # 게시판
        sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # 3-1. 랭킹 프레임
        rank_frame = ctk.CTkFrame(sidebar_frame, corner_radius=12)
        rank_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        ctk.CTkLabel(rank_frame, text="🏆 실시간 유저 자산 랭킹", font=("Arial", 12, "bold"), text_color="#3b82f6").pack(anchor="w", padx=15, pady=5)
        self.rank_box = ctk.CTkTextbox(rank_frame, height=100, font=("Courier New", 12))
        self.rank_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 3-2. 뉴스 프레임
        news_frame = ctk.CTkFrame(sidebar_frame, corner_radius=12)
        news_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        ctk.CTkLabel(news_frame, text="📰 시장 이슈 실시간 속보", font=("Arial", 12, "bold"), text_color="#f97316").pack(anchor="w", padx=15, pady=5)
        self.news_box = ctk.CTkTextbox(news_frame, height=100, font=("Arial", 11))
        self.news_box.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 3-3. 익명 게시판 프레임
        board_frame = ctk.CTkFrame(sidebar_frame, corner_radius=12)
        board_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        ctk.CTkLabel(board_frame, text="💬 익명 종목 토론방", font=("Arial", 12, "bold"), text_color="#a855f7").pack(anchor="w", padx=15, pady=2)
        
        self.board_box = ctk.CTkTextbox(board_frame, height=110, font=("Arial", 11))
        self.board_box.pack(fill="both", expand=True, padx=10, pady=2)
        
        input_subframe = ctk.CTkFrame(board_frame, height=35, fg_color="transparent")
        input_subframe.pack(fill="x", padx=10, pady=5)
        self.board_input = ctk.CTkEntry(input_subframe, placeholder_text="선동성 멘트나 잡담 입력...", font=("Arial", 11))
        self.board_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        write_btn = ctk.CTkButton(input_subframe, text="전송", width=50, command=self.post_to_board)
        write_btn.pack(side="right")
        
        # 화면 정기 업데이트 시작
        self.refresh_ui()

    def refresh_ui(self):
        """메인 화면 실시간 자산 및 컴포넌트 갱신"""
        if not self.current_user:
            return
            
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        
        # 1. 유저 보유 자금 갱신
        cursor.execute("SELECT cash FROM users WHERE username=?", (self.current_user,))
        cash = cursor.fetchone()[0]
        self.cash_label.configure(text=f"내 현금: {cash:,}원")
        
        # 2. 주식 목록 UI 파괴 후 재생성 (갱신)
        for widget in self.market_scroll.winfo_children():
            widget.destroy()
            
        cursor.execute("SELECT name, price, prev_price, is_permanent FROM stocks ORDER BY is_permanent DESC, name ASC")
        stocks_data = cursor.fetchall()
        
        for name, price, prev_price, is_perm in stocks_data:
            # 내 보유량 파악
            cursor.execute("SELECT amount FROM portfolio WHERE username=? AND stock_name=?", (self.current_user, name))
            holding_res = cursor.fetchone()
            holding_count = holding_res[0] if holding_res else 0
            
            # 전일비 변동률 계산
            change_ratio = 0.0
            if prev_price > 0:
                change_ratio = ((price - prev_price) / prev_price) * 100
                
            is_up = change_ratio >= 0
            change_color = "#10b981" if is_up else "#f43f5e" # 에메랄드(초록) vs 로즈(빨강)
            sign = "+" if is_up else ""
            
            # 종목 카드 프레임
            card = ctk.CTkFrame(self.market_scroll, height=90, corner_radius=12)
            card.pack(fill="x", padx=10, pady=6)
            
            # 종목명 및 유형
            label_text = f"{name}"
            if is_perm:
                label_text += " [🔒학교우량]"
            title_lbl = ctk.CTkLabel(card, text=label_text, font=("Arial", 14, "bold"), width=150, anchor="w")
            title_lbl.pack(side="left", padx=15)
            
            # 주가 및 변동률
            price_subframe = ctk.CTkFrame(card, fg_color="transparent")
            price_subframe.pack(side="left", padx=10)
            
            price_lbl = ctk.CTkLabel(price_subframe, text=f"{price:,}원", font=("Arial", 13, "bold"))
            price_lbl.pack(anchor="w")
            
            ratio_lbl = ctk.CTkLabel(price_subframe, text=f"{sign}{change_ratio:.2f}%", font=("Arial", 11, "bold"), text_color=change_color)
            ratio_lbl.pack(anchor="w")
            
            if holding_count > 0:
                holding_lbl = ctk.CTkLabel(card, text=f"보유: {holding_count}주", font=("Arial", 11, "bold"), text_color="#3b82f6")
                holding_lbl.pack(side="left", padx=15)
                
            # 조작 버튼 프레임 (수량, MAX 버튼, 매매)
            control_frame = ctk.CTkFrame(card, fg_color="transparent")
            control_frame.pack(side="right", padx=15)
            
            qty_entry = ctk.CTkEntry(control_frame, placeholder_text="수량", width=50, height=28, font=("Arial", 11))
            qty_entry.pack(side="left", padx=4)
            
            # MAX 매수/매도 도우미 버튼
            max_buy_btn = ctk.CTkButton(control_frame, text="買MAX", width=45, height=28, fg_color="#1e293b", text_color="#3b82f6", font=("Arial", 9, "bold"),
                                        command=lambda n=name, p=price, q=qty_entry, c=cash: self.set_max_buy_qty(p, q, c))
            max_buy_btn.pack(side="left", padx=2)
            
            max_sell_btn = ctk.CTkButton(control_frame, text="賣MAX", width=45, height=28, fg_color="#1e293b", text_color="#ef4444", font=("Arial", 9, "bold"),
                                         command=lambda n=name, q=qty_entry, h=holding_count: self.set_max_sell_qty(h, q))
            max_sell_btn.pack(side="left", padx=2)
            
            buy_btn = ctk.CTkButton(control_frame, text="매수", width=55, height=28, fg_color="#10b981", hover_color="#059669", font=("Arial", 12, "bold"),
                                    command=lambda n=name, p=price, q=qty_entry: self.buy_stock(n, p, q))
            buy_btn.pack(side="left", padx=3)
            
            sell_btn = ctk.CTkButton(control_frame, text="매도", width=55, height=28, fg_color="#f43f5e", hover_color="#e11d48", font=("Arial", 12, "bold"),
                                     command=lambda n=name, p=price, q=qty_entry: self.sell_stock(n, p, q))
            sell_btn.pack(side="left", padx=3)
            
        # 3. 랭킹 시스템 정보 로드
        self.update_leaderboard_ui(cursor)
        
        # 4. 뉴스 및 토론방 목록 로드
        self.update_news_ui()
        self.update_board_ui(cursor)
        
        conn.close()
        
        # 3초마다 지속적으로 UI 업데이트
        self.after(3000, self.refresh_ui)

    def set_max_buy_qty(self, price, qty_entry, cash):
        max_qty = cash // price
        qty_entry.delete(0, "end")
        qty_entry.insert(0, str(max_qty))
        
    def set_max_sell_qty(self, holding, qty_entry):
        qty_entry.delete(0, "end")
        qty_entry.insert(0, str(holding))

    def buy_stock(self, stock_name, price, qty_entry):
        try:
            qty = int(qty_entry.get().strip())
        except ValueError:
            return
        if qty <= 0: return
        
        cost = price * qty
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT cash FROM users WHERE username=?", (self.current_user,))
        cash = cursor.fetchone()[0]
        
        if cash >= cost:
            # 캐시 차감
            cursor.execute("UPDATE users SET cash = cash - ? WHERE username=?", (cost, self.current_user))
            # 포트폴리오 추가
            cursor.execute("SELECT amount FROM portfolio WHERE username=? AND stock_name=?", (self.current_user, stock_name))
            res = cursor.fetchone()
            if res:
                cursor.execute("UPDATE portfolio SET amount = amount + ? WHERE username=? AND stock_name=?", (qty, self.current_user, stock_name))
            else:
                cursor.execute("INSERT INTO portfolio VALUES (?, ?, ?)", (self.current_user, stock_name, qty))
            conn.commit()
            qty_entry.delete(0, "end")
        conn.close()

    def sell_stock(self, stock_name, price, qty_entry):
        try:
            qty = int(qty_entry.get().strip())
        except ValueError:
            return
        if qty <= 0: return
        
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM portfolio WHERE username=? AND stock_name=?", (self.current_user, stock_name))
        res = cursor.fetchone()
        holding = res[0] if res else 0
        
        if holding >= qty:
            # 캐시 환급
            cursor.execute("UPDATE users SET cash = cash + ? WHERE username=?", (price * qty, self.current_user))
            # 포트폴리오 차감
            if holding == qty:
                cursor.execute("DELETE FROM portfolio WHERE username=? AND stock_name=?", (self.current_user, stock_name))
            else:
                cursor.execute("UPDATE portfolio SET amount = amount - ? WHERE username=? AND stock_name=?", (qty, self.current_user, stock_name))
            conn.commit()
            qty_entry.delete(0, "end")
        conn.close()

    def post_to_board(self):
        content = self.board_input.get().strip()
        if not content: return
        
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        time_str = datetime.now().strftime("%H:%M")
        cursor.execute("INSERT INTO board (author, content, timestamp) VALUES (?, ?, ?)", ("익명", content, time_str))
        conn.commit()
        conn.close()
        
        self.board_input.delete(0, "end")

    def update_leaderboard_ui(self, cursor):
        """랭킹 계산 및 텍스트 박스에 수치 반영"""
        # 자산 가치 총합 계산 후 유저별 갱신
        cursor.execute("SELECT username, cash FROM users")
        users = cursor.fetchall()
        for user, cash in users:
            # 보유한 주식 시가 계산
            cursor.execute("""
                SELECT p.amount, s.price 
                FROM portfolio p 
                JOIN stocks s ON p.stock_name = s.name 
                WHERE p.username = ?
            """, (user,))
            holdings = cursor.fetchall()
            stock_value = sum(amt * prc for amt, prc in holdings)
            total = cash + stock_value
            cursor.execute("UPDATE users SET total_assets = ? WHERE username = ?", (total, user))
            
        # 상위 랭킹 불러오기
        cursor.execute("SELECT username, total_assets FROM users ORDER BY total_assets DESC LIMIT 5")
        top_users = cursor.fetchall()
        
        self.rank_box.configure(state="normal")
        self.rank_box.delete("1.0", "end")
        for idx, (user, total) in enumerate(top_users, 1):
            self.rank_box.insert("end", f"[{idx}등] {user:<10} | 자산: {total:,}원\n")
        self.rank_box.configure(state="disabled")

    def update_news_ui(self):
        self.news_box.configure(state="normal")
        self.news_box.delete("1.0", "end")
        for item in self.news_list[-5:]:  # 최신 뉴스 5개 출력
            self.news_box.insert("1.0", f" • {item}\n")
        self.news_box.configure(state="disabled")

    def update_board_ui(self, cursor):
        cursor.execute("SELECT author, content, timestamp FROM board ORDER BY id DESC LIMIT 10")
        posts = cursor.fetchall()
        
        self.board_box.configure(state="normal")
        self.board_box.delete("1.0", "end")
        for author, content, t in reversed(posts):
            self.board_box.insert("end", f"[{t}] {author}: {content}\n")
        self.board_box.configure(state="disabled")

    # 🌓 테마 전환
    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.active_frames.clear()

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    # 백그라운드 주가 변동 연산 (주기적)
    def background_market_loop(self):
        while self.running:
            time.sleep(4.0) # 4초마다 시장 시뮬레이션
            
            conn = sqlite3.connect("game.db")
            cursor = conn.cursor()
            
            # 1. 뉴스 발생 제어 (25% 확률)
            if random.random() < 0.25:
                cursor.execute("SELECT name FROM stocks")
                all_stocks = [r[0] for r in cursor.fetchall()]
                if all_stocks:
                    target_stock = random.choice(all_stocks)
                    events = [
                        ("대형 프로젝트 수주 소식! 시세 대폭 상승 예고", 2.0),
                        ("실적 발표 호조! 투자 증가 기대", 1.0),
                        ("부정적 소문 유포로 심리가 악화되었습니다.", -1.0),
                        ("내부 감사 중대 결함 발표, 가격 폭락 예고", -2.5)
                    ]
                    content, trend_val = random.choice(events)
                    cursor.execute("UPDATE stocks SET trend = ? WHERE name = ?", (trend_val, target_stock))
                    self.news_list.append(f"[{target_stock}] {content}")
            
            # 2. 전 종목 주가 계산 및 변동
            cursor.execute("SELECT name, price, trend, is_permanent FROM stocks")
            stocks = cursor.fetchall()
            
            for name, price, trend, is_perm in stocks:
                base_change = random.uniform(-0.06, 0.06) # 기본 변동폭
                trend_change = trend * 0.08
                
                new_price = int(price * (1 + base_change + trend_change))
                new_price = max(1, new_price)
                
                # 상장폐지 체크 (가치가 50원 이하가 되는 경우)
                if new_price <= 50:
                    if is_perm:
                        # 🔒 19개 핵심 학교 종목은 자동 긴급 구조 및 부활
                        new_price = 500
                        cursor.execute("UPDATE stocks SET price = ?, prev_price = ?, trend = 1.0 WHERE name = ?", (500, price, name))
                        self.news_list.append(f"🛡️ [{name}] 주가가 한계선에 도달하여 구조 기금이 투입되었습니다.")
                    else:
                        # 일반 잡주는 냉혹하게 상장폐지 처리
                        cursor.execute("DELETE FROM stocks WHERE name = ?", (name,))
                        cursor.execute("DELETE FROM portfolio WHERE stock_name = ?", (name,))
                        self.news_list.append(f"🚨 [상장폐지] 부실종목 [{name}]이(가) 시장에서 퇴출되었습니다.")
                        continue
                else:
                    # 추세 감소 처리 (시간이 지나면 뉴스의 약효가 떨어짐)
                    next_trend = trend
                    if trend > 0: next_trend = max(0.0, trend - 0.2)
                    elif trend < 0: next_trend = min(0.0, trend + 0.2)
                    
                    cursor.execute("UPDATE stocks SET price = ?, prev_price = ?, trend = ? WHERE name = ?", (new_price, price, next_trend, name))
            
            conn.commit()
            conn.close()

if __name__ == "__main__":
    app = App()
    app.mainloop()
