# Streamlit Cloud 배포용 메인 파일
import sys
from pathlib import Path

# 앱 디렉토리를 Python 경로에 추가
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# 메인 Streamlit 앱 실행
from app.ui.streamlit_app import main

if __name__ == "__main__":
    main()