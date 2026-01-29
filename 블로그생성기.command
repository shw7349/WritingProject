#!/bin/bash
# 블로그 SEO 생성기 실행 스크립트 (웹 버전)

# 프로젝트 폴더로 이동
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

echo "========================================"
echo "  블로그 SEO 생성기 (웹 버전)"
echo "========================================"
echo ""

# venv의 Python/Streamlit 직접 사용
STREAMLIT="$PROJECT_DIR/venv/bin/streamlit"

if [ ! -f "$STREAMLIT" ]; then
    echo "❌ Streamlit을 찾을 수 없습니다."
    echo "터미널에서 다음 명령을 실행하세요:"
    echo ""
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo "  pip install streamlit"
    echo ""
    echo "아무 키나 누르면 종료됩니다..."
    read -n 1
    exit 1
fi

echo "브라우저에서 자동으로 열립니다..."
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# Streamlit 실행
$STREAMLIT run blog_generator_web.py --server.headless=false
