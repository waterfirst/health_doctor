"""
OpenHealth 메인 실행 파일
"""

import subprocess
import sys
from pathlib import Path

def main():
    """메인 함수"""
    print("🏥 OpenHealth 건강 도우미를 시작합니다...")
    
    # Streamlit 앱 실행
    app_file = Path("app/ui/streamlit_app.py")
    
    if not app_file.exists():
        print("❌ Streamlit 앱 파일을 찾을 수 없습니다.")
        print("setup.py를 먼저 실행해주세요.")
        return
    
    try:
        print("🌐 브라우저에서 http://localhost:8501 로 접속하세요")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_file),
            "--server.address", "localhost",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 OpenHealth를 종료합니다.")
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

if __name__ == "__main__":
    main()