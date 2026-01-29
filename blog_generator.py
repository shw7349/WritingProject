#!/usr/bin/env python3
"""
블로그 SEO HTML 생성기
- 키워드 입력 → 웹 검색 → Claude API로 블로그 글 생성
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import anthropic
except ImportError:
    anthropic = None


def load_env_file() -> dict:
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


def load_prompt_template() -> str:
    """프롬프트 템플릿 파일 로드"""
    template_path = Path(__file__).parent / ".claude" / "blog_seo_html_prompt.md"
    if not template_path.exists():
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {template_path}")
    return template_path.read_text(encoding="utf-8")


def search_keyword(keyword, max_results=10):
    """DuckDuckGo로 키워드 검색"""
    if DDGS is None:
        print("⚠️  duckduckgo-search 패키지가 없어 검색을 건너뜁니다.")
        print("   설치: pip install duckduckgo-search")
        return []

    print(f"🔍 '{keyword}' 검색 중...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(keyword, region="kr-kr", max_results=max_results))
        print(f"   {len(results)}개 결과 수집 완료")
        return results
    except Exception as e:
        print(f"⚠️  검색 실패: {e}")
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


def build_prompt(
    template: str,
    keyword: str,
    search_context: str,
    audience: str = "일반 독자",
    goal: str = "정보 제공",
    tone: str = "친절하고 명확하게",
    brand: str = "",
    location: str = "",
    avoid_terms: str = "",
) -> str:
    """프롬프트 템플릿에 변수 치환"""
    # 템플릿 변수 치환
    prompt = template.replace("{{keyword}}", keyword)
    prompt = prompt.replace("{{audience}}", audience)
    prompt = prompt.replace("{{goal}}", goal)
    prompt = prompt.replace("{{tone}}", tone)
    prompt = prompt.replace("{{brand}}", brand if brand else "생략")
    prompt = prompt.replace("{{location}}", location if location else "생략")
    prompt = prompt.replace("{{avoid_terms}}", avoid_terms if avoid_terms else "생략")

    # 검색 컨텍스트 추가
    if search_context:
        prompt = f"{prompt}\n\n---\n\n{search_context}\n\n위 검색 결과를 참고하여 최신 정보와 트렌드를 반영한 글을 작성하세요."

    return prompt


def generate_blog_with_claude(prompt: str, keyword: str) -> str:
    """Claude API로 블로그 글 생성"""
    if anthropic is None:
        raise ImportError(
            "anthropic 패키지가 설치되지 않았습니다.\n"
            "설치: pip install anthropic"
        )

    api_key = get_api_key()
    if not api_key:
        env_path = Path(__file__).parent / ".env"
        raise ValueError(
            f"API 키가 설정되지 않았습니다.\n"
            f".env 파일을 열어 ANTHROPIC_API_KEY를 설정하세요.\n"
            f"파일 위치: {env_path}"
        )

    print(f"✍️  '{keyword}' 블로그 글 생성 중...")

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = message.content[0].text
    print("   생성 완료!")
    return content


def save_output(html_content: str, keyword: str, output_dir: str = "output") -> Path:
    """생성된 HTML을 파일로 저장"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 파일명 생성 (키워드 + 타임스탬프)
    safe_keyword = "".join(c if c.isalnum() or c in "-_" else "_" for c in keyword)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_keyword}_{timestamp}.html"

    filepath = output_path / filename

    # 완전한 HTML 문서로 래핑
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
{html_content}
</body>
</html>"""

    filepath.write_text(full_html, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="키워드 기반 SEO 블로그 글 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python blog_generator.py "갤럭시 S24 리뷰"
  python blog_generator.py "서울 맛집" --audience "20-30대" --tone "캐주얼하게"
  python blog_generator.py "재테크 방법" --goal "가이드 제공" --no-search
        """
    )

    parser.add_argument("keyword", help="블로그 글의 메인 키워드")
    parser.add_argument("--audience", default="일반 독자", help="타겟 독자 (기본: 일반 독자)")
    parser.add_argument("--goal", default="정보 제공", help="글 목적 (기본: 정보 제공)")
    parser.add_argument("--tone", default="친절하고 명확하게", help="톤/말투 (기본: 친절하고 명확하게)")
    parser.add_argument("--brand", default="", help="브랜드/서비스명 (선택)")
    parser.add_argument("--location", default="", help="지역 (선택)")
    parser.add_argument("--avoid", default="", help="금지어/회피표현 (선택)")
    parser.add_argument("--output", "-o", default="output", help="출력 디렉토리 (기본: output)")
    parser.add_argument("--no-search", action="store_true", help="웹 검색 건너뛰기")
    parser.add_argument("--search-count", type=int, default=10, help="검색 결과 수 (기본: 10)")

    args = parser.parse_args()

    print("=" * 50)
    print("🚀 블로그 SEO HTML 생성기")
    print("=" * 50)
    print(f"📌 키워드: {args.keyword}")
    print(f"👥 타겟 독자: {args.audience}")
    print(f"🎯 목적: {args.goal}")
    print(f"💬 톤: {args.tone}")
    print()

    # 1. 프롬프트 템플릿 로드
    try:
        template = load_prompt_template()
    except FileNotFoundError as e:
        print(f"❌ 오류: {e}")
        sys.exit(1)

    # 2. 웹 검색
    search_context = ""
    if not args.no_search:
        results = search_keyword(args.keyword, args.search_count)
        search_context = format_search_context(results)

    # 3. 프롬프트 생성
    prompt = build_prompt(
        template=template,
        keyword=args.keyword,
        search_context=search_context,
        audience=args.audience,
        goal=args.goal,
        tone=args.tone,
        brand=args.brand,
        location=args.location,
        avoid_terms=args.avoid,
    )

    # 4. Claude API로 생성
    try:
        html_content = generate_blog_with_claude(prompt, args.keyword)
    except (ImportError, ValueError) as e:
        print(f"❌ 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        sys.exit(1)

    # 5. 파일 저장
    output_file = save_output(html_content, args.keyword, args.output)

    print()
    print("=" * 50)
    print(f"✅ 완료! 파일 저장됨: {output_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()
