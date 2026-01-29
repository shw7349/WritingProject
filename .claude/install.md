# 블로그 SEO HTML 생성기 - 설치 및 실행 가이드

## 요구 사항

- Python 3.7 이상
- macOS / Windows / Linux

---

## 1. 패키지 설치

터미널에서 프로젝트 폴더로 이동 후 실행:

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install anthropic duckduckgo-search
```

---

## 2. API 키 설정

프로젝트 루트의 `.env` 파일을 열어 API 키를 입력합니다.

```
ANTHROPIC_API_KEY=sk-ant-api03-여기에_실제_키_입력
```

> API 키 발급: https://console.anthropic.com/

---

## 3. 실행 방법

### 방법 1: GUI 앱 실행 (권장)

**macOS:**
- `블로그생성기.app` 더블클릭
- 또는 `블로그생성기.command` 더블클릭

**터미널:**
```bash
python3 blog_generator_gui.py
```

### 방법 2: CLI 실행

```bash
# 기본 사용
python3 blog_generator.py "키워드"

# 옵션 사용
python3 blog_generator.py "서울 맛집" --audience "20-30대" --tone "캐주얼하게"

# 웹 검색 없이 생성
python3 blog_generator.py "재테크 방법" --no-search
```

---

## CLI 옵션

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

---

## GUI 기능

1. **키워드 입력**: 메인 키워드와 옵션 설정
2. **웹 검색 토글**: 최신 정보 반영 여부 선택
3. **생성 버튼**: 블로그 글 생성 (1~2분 소요)
4. **복사**: 클립보드에 복사
5. **새로 생성**: 같은 키워드로 다시 생성
6. **저장 (TXT)**: 텍스트 파일로 저장
7. **저장 (HTML)**: 스타일 포함 HTML로 저장

---

## 파일 구조

```
writingProject/
├── .env                    # API 키 설정 (git 제외)
├── .env.example            # 설정 예시 파일
├── .gitignore              # git 제외 목록
├── requirements.txt        # 패키지 목록
├── blog_generator.py       # CLI 버전
├── blog_generator_gui.py   # GUI 버전
├── 블로그생성기.app/        # macOS 앱
├── 블로그생성기.command     # macOS 실행 스크립트
├── output/                 # 생성된 파일 저장 폴더
└── .claude/
    ├── blog_seo_html_prompt.md  # 프롬프트 템플릿
    └── install.md               # 이 파일
```

---

## 문제 해결

### "API 키가 설정되지 않았습니다"
→ `.env` 파일에 `ANTHROPIC_API_KEY` 값이 올바르게 입력되었는지 확인

### "anthropic 패키지가 없습니다"
→ `pip install anthropic` 실행

### "duckduckgo-search 패키지가 없습니다"
→ `pip install duckduckgo-search` 실행 (웹 검색 기능에 필요)

### macOS 앱 실행 시 "확인되지 않은 개발자" 경고
→ 시스템 설정 > 개인 정보 보호 및 보안 > "확인 없이 열기" 클릭
→ 또는 앱을 우클릭 > 열기 선택

---

## 출력 예시

생성된 파일은 `output/` 폴더에 저장됩니다:
- `키워드_20260129_143052.html` (HTML 형식)
- `키워드_20260129_143052.txt` (텍스트 형식)
