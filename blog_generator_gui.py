#!/usr/bin/env python3
"""
블로그 SEO HTML 생성기 - GUI 버전
아이콘 클릭으로 실행, 키워드 입력 후 블로그 글 생성
"""

import os
import sys
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def load_env_file() -> dict:
    """프로젝트 루트의 .env 파일에서 환경 변수 로드"""
    env_path = Path(__file__).parent / ".env"
    env_vars = {}

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 주석이나 빈 줄 무시
                if not line or line.startswith("#"):
                    continue
                # KEY=VALUE 형식 파싱
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # 따옴표 제거
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    env_vars[key] = value

    return env_vars


def get_api_key():
    """API 키를 .env 파일 또는 환경 변수에서 가져오기"""
    # 1. .env 파일에서 먼저 확인
    env_vars = load_env_file()
    api_key = env_vars.get("ANTHROPIC_API_KEY", "")

    # 플레이스홀더 값인지 확인
    if api_key and api_key != "여기에_API_키를_입력하세요":
        return api_key

    # 2. 시스템 환경 변수에서 확인
    return os.environ.get("ANTHROPIC_API_KEY")


class BlogGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 블로그 SEO 생성기")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)

        # 생성된 컨텐츠 저장
        self.generated_content = ""
        self.is_generating = False

        self.setup_ui()
        self.check_dependencies()

    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === 입력 섹션 ===
        input_frame = ttk.LabelFrame(main_frame, text="🎯 입력 설정", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 키워드 입력
        keyword_frame = ttk.Frame(input_frame)
        keyword_frame.pack(fill=tk.X, pady=5)
        ttk.Label(keyword_frame, text="메인 키워드:", width=12).pack(side=tk.LEFT)
        self.keyword_entry = ttk.Entry(keyword_frame, font=("", 12))
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.keyword_entry.bind("<Return>", lambda e: self.generate_blog())

        # 옵션 프레임 (2열)
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill=tk.X, pady=5)

        # 왼쪽 열
        left_col = ttk.Frame(options_frame)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 타겟 독자
        audience_frame = ttk.Frame(left_col)
        audience_frame.pack(fill=tk.X, pady=2)
        ttk.Label(audience_frame, text="타겟 독자:", width=12).pack(side=tk.LEFT)
        self.audience_entry = ttk.Entry(audience_frame)
        self.audience_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.audience_entry.insert(0, "일반 독자")

        # 글 목적
        goal_frame = ttk.Frame(left_col)
        goal_frame.pack(fill=tk.X, pady=2)
        ttk.Label(goal_frame, text="글 목적:", width=12).pack(side=tk.LEFT)
        self.goal_entry = ttk.Entry(goal_frame)
        self.goal_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.goal_entry.insert(0, "정보 제공")

        # 오른쪽 열
        right_col = ttk.Frame(options_frame)
        right_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 톤/말투
        tone_frame = ttk.Frame(right_col)
        tone_frame.pack(fill=tk.X, pady=2)
        ttk.Label(tone_frame, text="톤/말투:", width=12).pack(side=tk.LEFT)
        self.tone_entry = ttk.Entry(tone_frame)
        self.tone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.tone_entry.insert(0, "친절하고 명확하게")

        # 웹 검색 체크박스
        search_frame = ttk.Frame(right_col)
        search_frame.pack(fill=tk.X, pady=2)
        self.search_var = tk.BooleanVar(value=True)
        self.search_check = ttk.Checkbutton(
            search_frame,
            text="웹 검색으로 최신 정보 반영",
            variable=self.search_var
        )
        self.search_check.pack(side=tk.LEFT, padx=(80, 0))

        # === 버튼 섹션 ===
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.generate_btn = ttk.Button(
            button_frame,
            text="✨ 블로그 글 생성",
            command=self.generate_blog,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.regenerate_btn = ttk.Button(
            button_frame,
            text="🔄 새로 생성",
            command=self.generate_blog,
            state=tk.DISABLED
        )
        self.regenerate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_btn = ttk.Button(
            button_frame,
            text="📋 복사",
            command=self.copy_content,
            state=tk.DISABLED
        )
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(
            button_frame,
            text="💾 저장 (TXT)",
            command=self.save_content,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_html_btn = ttk.Button(
            button_frame,
            text="🌐 저장 (HTML)",
            command=self.save_html,
            state=tk.DISABLED
        )
        self.save_html_btn.pack(side=tk.LEFT)

        # === 상태 표시 ===
        self.status_var = tk.StringVar(value="키워드를 입력하고 '블로그 글 생성' 버튼을 클릭하세요.")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="gray")
        self.status_label.pack(fill=tk.X, pady=5)

        # 프로그레스 바
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # === 출력 섹션 ===
        output_frame = ttk.LabelFrame(main_frame, text="📄 생성된 블로그 글", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Menlo", 11),
            padx=10,
            pady=10
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # 글자 수 표시
        self.char_count_var = tk.StringVar(value="글자 수: 0")
        char_count_label = ttk.Label(main_frame, textvariable=self.char_count_var)
        char_count_label.pack(anchor=tk.E)

    def check_dependencies(self):
        """의존성 패키지 확인"""
        missing = []
        if not ANTHROPIC_AVAILABLE:
            missing.append("anthropic")
        if not SEARCH_AVAILABLE:
            missing.append("duckduckgo-search")

        if missing:
            msg = f"다음 패키지가 필요합니다:\n\npip install {' '.join(missing)}"
            messagebox.showwarning("패키지 필요", msg)

        # API 키 확인 (.env 파일 또는 환경 변수)
        api_key = get_api_key()
        if not api_key:
            self.status_var.set("⚠️ API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

    def load_prompt_template(self) -> str:
        """프롬프트 템플릿 로드"""
        template_path = Path(__file__).parent / ".claude" / "blog_seo_html_prompt.md"
        if not template_path.exists():
            raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {template_path}")
        return template_path.read_text(encoding="utf-8")

    def search_keyword(self, keyword: str) -> str:
        """웹 검색"""
        if not SEARCH_AVAILABLE or not self.search_var.get():
            return ""

        self.update_status(f"🔍 '{keyword}' 검색 중...")

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(keyword, region="kr-kr", max_results=10))

            if not results:
                return ""

            context_parts = ["## 검색 결과 참고 자료\n"]
            for i, r in enumerate(results, 1):
                title = r.get("title", "제목 없음")
                body = r.get("body", "")[:300]
                context_parts.append(f"### {i}. {title}\n{body}\n")

            return "\n".join(context_parts)
        except Exception as e:
            self.update_status(f"⚠️ 검색 실패: {e}")
            return ""

    def build_prompt(self, template: str, keyword: str, search_context: str) -> str:
        """프롬프트 생성"""
        prompt = template.replace("{{keyword}}", keyword)
        prompt = prompt.replace("{{audience}}", self.audience_entry.get() or "일반 독자")
        prompt = prompt.replace("{{goal}}", self.goal_entry.get() or "정보 제공")
        prompt = prompt.replace("{{tone}}", self.tone_entry.get() or "친절하고 명확하게")
        prompt = prompt.replace("{{brand}}", "생략")
        prompt = prompt.replace("{{location}}", "생략")
        prompt = prompt.replace("{{avoid_terms}}", "생략")

        if search_context:
            prompt = f"{prompt}\n\n---\n\n{search_context}\n\n위 검색 결과를 참고하여 최신 정보와 트렌드를 반영한 글을 작성하세요."

        return prompt

    def generate_blog(self):
        """블로그 글 생성 (스레드에서 실행)"""
        keyword = self.keyword_entry.get().strip()

        if not keyword:
            messagebox.showwarning("입력 필요", "키워드를 입력해주세요.")
            self.keyword_entry.focus()
            return

        if not ANTHROPIC_AVAILABLE:
            messagebox.showerror("오류", "anthropic 패키지가 설치되지 않았습니다.\n\npip install anthropic")
            return

        api_key = get_api_key()
        if not api_key:
            messagebox.showerror(
                "API 키 필요",
                "API 키가 설정되지 않았습니다.\n\n"
                ".env 파일을 열어 ANTHROPIC_API_KEY를 설정하세요.\n"
                f"파일 위치: {Path(__file__).parent / '.env'}"
            )
            return

        if self.is_generating:
            return

        self.is_generating = True
        self.generate_btn.config(state=tk.DISABLED)
        self.regenerate_btn.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.save_html_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.output_text.delete(1.0, tk.END)

        # 백그라운드 스레드에서 생성
        thread = threading.Thread(target=self._generate_thread, args=(keyword,))
        thread.daemon = True
        thread.start()

    def _generate_thread(self, keyword: str):
        """생성 작업 (별도 스레드)"""
        try:
            # 1. 템플릿 로드
            self.update_status("📄 프롬프트 템플릿 로드 중...")
            template = self.load_prompt_template()

            # 2. 웹 검색
            search_context = self.search_keyword(keyword)

            # 3. 프롬프트 생성
            self.update_status("✍️ 블로그 글 생성 중... (1~2분 소요)")
            prompt = self.build_prompt(template, keyword, search_context)

            # 4. Claude API 호출
            api_key = get_api_key()
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = message.content[0].text
            self.generated_content = content

            # UI 업데이트 (메인 스레드에서)
            self.root.after(0, lambda: self._on_generation_complete(content, keyword))

        except FileNotFoundError as e:
            self.root.after(0, lambda: self._on_generation_error(str(e)))
        except Exception as e:
            self.root.after(0, lambda: self._on_generation_error(f"생성 실패: {e}"))

    def _on_generation_complete(self, content: str, keyword: str):
        """생성 완료 콜백"""
        self.progress.stop()
        self.is_generating = False

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, content)

        char_count = len(content)
        self.char_count_var.set(f"글자 수: {char_count:,}")

        self.update_status(f"✅ '{keyword}' 블로그 글 생성 완료!")

        self.generate_btn.config(state=tk.NORMAL)
        self.regenerate_btn.config(state=tk.NORMAL)
        self.copy_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.save_html_btn.config(state=tk.NORMAL)

    def _on_generation_error(self, error_msg: str):
        """생성 오류 콜백"""
        self.progress.stop()
        self.is_generating = False
        self.generate_btn.config(state=tk.NORMAL)
        self.update_status(f"❌ {error_msg}")
        messagebox.showerror("오류", error_msg)

    def update_status(self, message: str):
        """상태 메시지 업데이트"""
        self.root.after(0, lambda: self.status_var.set(message))

    def copy_content(self):
        """클립보드에 복사"""
        content = self.output_text.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("📋 클립보드에 복사되었습니다!")

    def save_content(self):
        """TXT 파일로 저장"""
        content = self.output_text.get(1.0, tk.END).strip()
        if not content:
            return

        keyword = self.keyword_entry.get().strip()
        safe_keyword = "".join(c if c.isalnum() or c in "-_" else "_" for c in keyword)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{safe_keyword}_{timestamp}.txt"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
            initialfile=default_name
        )

        if filepath:
            Path(filepath).write_text(content, encoding="utf-8")
            self.update_status(f"💾 저장 완료: {filepath}")

    def save_html(self):
        """HTML 파일로 저장"""
        content = self.output_text.get(1.0, tk.END).strip()
        if not content:
            return

        keyword = self.keyword_entry.get().strip()
        safe_keyword = "".join(c if c.isalnum() or c in "-_" else "_" for c in keyword)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{safe_keyword}_{timestamp}.html"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML 파일", "*.html"), ("모든 파일", "*.*")],
            initialfile=default_name
        )

        if filepath:
            full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keyword} - 블로그</title>
    <style>
        body {{
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 40px; }}
        h3 {{ color: #34495e; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        ul, ol {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
        p {{ margin: 16px 0; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
            Path(filepath).write_text(full_html, encoding="utf-8")
            self.update_status(f"🌐 HTML 저장 완료: {filepath}")


def main():
    root = tk.Tk()

    # macOS에서 창을 앞으로 가져오기
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))

    # macOS에서 앱 활성화
    try:
        import subprocess
        subprocess.run(['osascript', '-e', 'tell application "Python" to activate'],
                      capture_output=True, timeout=2)
    except Exception:
        pass

    app = BlogGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
