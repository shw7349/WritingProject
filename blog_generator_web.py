#!/usr/bin/env python3
"""
블로그 SEO HTML 생성기 - 웹 UI 버전 (Streamlit)
"""

import os
from pathlib import Path
from datetime import datetime

import streamlit as st

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


def load_env_file():
    """프로젝트 루트의 .env 파일에서 환경 변수 로드"""
    env_path = Path(__file__).parent / ".env"
    env_vars = {}

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    env_vars[key] = value

    return env_vars


def get_api_key():
    """API 키를 .env 파일 또는 환경 변수에서 가져오기"""
    env_vars = load_env_file()
    api_key = env_vars.get("ANTHROPIC_API_KEY", "")

    if api_key and api_key != "여기에_API_키를_입력하세요":
        return api_key

    return os.environ.get("ANTHROPIC_API_KEY")


def load_prompt_template():
    """프롬프트 템플릿 로드"""
    template_path = Path(__file__).parent / ".claude" / "blog_seo_html_prompt.md"
    if not template_path.exists():
        return None
    return template_path.read_text(encoding="utf-8")


def search_keyword(keyword, max_results=10):
    """웹 검색"""
    if not SEARCH_AVAILABLE:
        return []

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(keyword, region="kr-kr", max_results=max_results))
        return results
    except Exception:
        return []


def format_search_context(results):
    """검색 결과를 컨텍스트 문자열로 변환"""
    if not results:
        return ""

    context_parts = ["## 검색 결과 참고 자료\n"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "제목 없음")
        body = r.get("body", "")[:300]
        context_parts.append(f"### {i}. {title}\n{body}\n")

    return "\n".join(context_parts)


def build_prompt(template, keyword, search_context, audience, goal, tone):
    """프롬프트 생성"""
    prompt = template.replace("{{keyword}}", keyword)
    prompt = prompt.replace("{{audience}}", audience)
    prompt = prompt.replace("{{goal}}", goal)
    prompt = prompt.replace("{{tone}}", tone)
    prompt = prompt.replace("{{brand}}", "생략")
    prompt = prompt.replace("{{location}}", "생략")
    prompt = prompt.replace("{{avoid_terms}}", "생략")

    if search_context:
        prompt = f"{prompt}\n\n---\n\n{search_context}\n\n위 검색 결과를 참고하여 최신 정보와 트렌드를 반영한 글을 작성하세요."

    return prompt


def generate_blog(prompt, api_key):
    """Claude API로 블로그 글 생성"""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def main():
    st.set_page_config(
        page_title="블로그 SEO 생성기",
        page_icon="✍️",
        layout="wide"
    )

    st.title("✍️ 블로그 SEO HTML 생성기")
    st.markdown("키워드를 입력하면 SEO 최적화된 블로그 글을 자동으로 생성합니다.")

    # API 키 확인
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ API 키가 설정되지 않았습니다. `.env` 파일에 `ANTHROPIC_API_KEY`를 설정하세요.")
        st.stop()

    # 프롬프트 템플릿 확인
    template = load_prompt_template()
    if not template:
        st.error("⚠️ 프롬프트 템플릿 파일을 찾을 수 없습니다.")
        st.stop()

    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")

        audience = st.text_input("타겟 독자", value="일반 독자")
        goal = st.text_input("글 목적", value="정보 제공")
        tone = st.text_input("톤/말투", value="친절하고 명확하게")

        use_search = st.checkbox("웹 검색으로 최신 정보 반영", value=True)

        if not SEARCH_AVAILABLE:
            st.warning("duckduckgo-search 패키지가 없어 웹 검색이 비활성화됩니다.")

        st.markdown("---")
        st.markdown("**사용법**")
        st.markdown("1. 키워드 입력")
        st.markdown("2. '생성' 버튼 클릭")
        st.markdown("3. 결과 복사 또는 저장")

    # 메인 영역
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 키워드 입력")
        keyword = st.text_input("메인 키워드", placeholder="예: 갤럭시 S24 리뷰")

        generate_btn = st.button("✨ 블로그 글 생성", type="primary", use_container_width=True)

    # 생성 로직
    if generate_btn:
        if not keyword:
            st.warning("키워드를 입력해주세요.")
        else:
            with col2:
                st.subheader("📄 생성 결과")

                with st.spinner("블로그 글 생성 중... (1~2분 소요)"):
                    # 웹 검색
                    search_context = ""
                    if use_search and SEARCH_AVAILABLE:
                        with st.status("🔍 웹 검색 중..."):
                            results = search_keyword(keyword)
                            search_context = format_search_context(results)
                            st.write(f"{len(results)}개 결과 수집")

                    # 프롬프트 생성
                    prompt = build_prompt(template, keyword, search_context, audience, goal, tone)

                    # 생성
                    try:
                        content = generate_blog(prompt, api_key)

                        # 세션에 저장
                        st.session_state['generated_content'] = content
                        st.session_state['keyword'] = keyword

                    except Exception as e:
                        st.error(f"생성 실패: {e}")

    # 결과 표시
    if 'generated_content' in st.session_state:
        with col2:
            if 'generated_content' not in dir():
                st.subheader("📄 생성 결과")

            content = st.session_state['generated_content']
            keyword = st.session_state.get('keyword', 'blog')

            # 글자 수 표시
            st.caption(f"글자 수: {len(content):,}자")

            # 탭으로 HTML/미리보기 전환
            tab1, tab2 = st.tabs(["📝 HTML 코드", "👁️ 미리보기"])

            with tab1:
                st.code(content, language="html")

            with tab2:
                st.components.v1.html(f"""
                <div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.8; padding: 20px;">
                {content}
                </div>
                """, height=600, scrolling=True)

            # 버튼들
            col_btn1, col_btn2, col_btn3 = st.columns(3)

            with col_btn1:
                st.download_button(
                    "📋 TXT 다운로드",
                    content,
                    file_name=f"{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col_btn2:
                full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keyword} - 블로그</title>
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; line-height: 1.8; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 40px; }}
        h3 {{ color: #34495e; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
                st.download_button(
                    "🌐 HTML 다운로드",
                    full_html,
                    file_name=f"{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )

            with col_btn3:
                if st.button("🔄 새로 생성", use_container_width=True):
                    del st.session_state['generated_content']
                    st.rerun()


if __name__ == "__main__":
    main()
