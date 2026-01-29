# 블로그 SEO HTML 생성기

키워드를 입력하면 **웹 검색 + Claude AI**를 활용하여 SEO 최적화된 블로그 글을 자동으로 생성하는 프로그램입니다.

## 주요 기능

- **키워드 기반 자동 생성**: 키워드 입력만으로 약 3,000자 분량의 블로그 글 생성
- **웹 검색 연동**: DuckDuckGo 검색으로 최신 정보 반영
- **SEO 최적화**: H1/H2 구조, FAQ, 표, 리스트 등 SEO 친화적인 HTML 구조
- **다양한 실행 방식**: CLI, GUI(tkinter), 웹(Streamlit) 지원

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/shw7349/WritingProject.git
cd WritingProject
```

### 2. 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

**필수 패키지:**
- `anthropic` - Claude API 클라이언트
- `duckduckgo-search` - 웹 검색
- `streamlit` - 웹 UI

### 4. API 키 설정

`.env.example`을 `.env`로 복사하고 API 키를 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```
ANTHROPIC_API_KEY=sk-ant-api03-여기에_실제_키_입력
```

> API 키 발급: https://console.anthropic.com/

## 실행 방법

### 웹 UI (권장)

```bash
streamlit run blog_generator_web.py
```

브라우저에서 `http://localhost:8501` 자동 오픈

### macOS 앱 실행

- `블로그생성기.command` 더블클릭
- 또는 `블로그생성기.app` 더블클릭

### CLI

```bash
# 기본 사용
python blog_generator.py "갤럭시 S24 리뷰"

# 옵션 사용
python blog_generator.py "서울 맛집" --audience "20-30대" --tone "캐주얼하게"

# 웹 검색 없이
python blog_generator.py "재테크 방법" --no-search
```

#### CLI 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `keyword` | 메인 키워드 (필수) | - |
| `--audience` | 타겟 독자 | 일반 독자 |
| `--goal` | 글 목적 | 정보 제공 |
| `--tone` | 톤/말투 | 친절하고 명확하게 |
| `--brand` | 브랜드명 | - |
| `--location` | 지역 | - |
| `--avoid` | 금지어 | - |
| `--no-search` | 웹 검색 건너뛰기 | False |
| `-o, --output` | 출력 폴더 | output |

## 프로젝트 구조

```
WritingProject/
├── .env                         # API 키 설정 (git 제외)
├── .env.example                 # 설정 예시 파일
├── .gitignore
├── README.md
├── requirements.txt
│
├── blog_generator.py            # CLI 버전
├── blog_generator_gui.py        # GUI 버전 (tkinter)
├── blog_generator_web.py        # 웹 버전 (Streamlit)
│
├── 블로그생성기.app/             # macOS 앱 번들
├── 블로그생성기.command          # macOS 실행 스크립트
│
├── output/                      # 생성된 파일 저장 폴더
│
└── .claude/
    ├── blog_seo_html_prompt.md  # 프롬프트 템플릿
    └── install.md               # 상세 설치 가이드
```

## 프롬프트 구조

`.claude/blog_seo_html_prompt.md`에 정의된 프롬프트 템플릿:

### 입력 변수
| 변수 | 설명 |
|------|------|
| `{{keyword}}` | 메인 키워드 |
| `{{audience}}` | 타겟 독자 |
| `{{goal}}` | 글 목적 |
| `{{tone}}` | 톤/말투 |
| `{{brand}}` | 브랜드명 (선택) |
| `{{location}}` | 지역 (선택) |

### 출력 형식
- 순수 HTML만 출력 (`<article>` 태그로 감싸기)
- `<h1>` 1개 (메인 키워드 포함)
- `<h2>` 최소 5개 (본문 섹션)
- 리스트 최소 2개 (`<ul>` 또는 `<ol>`)
- 표 1개 (`<table>`)
- FAQ 섹션 3~5문항

### SEO 규칙
- 메인 키워드: 전체 글에서 6~10회 자연스럽게 포함
- 연관 키워드 최소 8개 이상 삽입
- E-E-A-T 스타일 (근거 없는 확정 표현 금지)

## 개발 환경

| 항목 | 버전/정보 |
|------|-----------|
| Python | 3.7+ |
| AI 모델 | Claude Sonnet 4 |
| 웹 프레임워크 | Streamlit |
| 검색 엔진 | DuckDuckGo |

## 문제 해결

### "API 키가 설정되지 않았습니다"
→ `.env` 파일에 `ANTHROPIC_API_KEY` 값이 올바르게 입력되었는지 확인

### "anthropic 패키지가 없습니다"
```bash
pip install anthropic
```

### "duckduckgo-search 패키지가 없습니다"
```bash
pip install duckduckgo-search
```

### macOS 앱 실행 시 "확인되지 않은 개발자" 경고
→ 시스템 설정 > 개인 정보 보호 및 보안 > "확인 없이 열기" 클릭

## 라이선스

MIT License
