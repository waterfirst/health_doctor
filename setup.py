"""
OpenHealth 자동 설치 및 설정 스크립트
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class OpenHealthSetup:
    """OpenHealth 설치 및 설정"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.app_dir = self.project_dir / "app"
        self.data_dir = self.project_dir / "data"
    
    def create_directory_structure(self):
        """디렉토리 구조 생성"""
        print("📁 프로젝트 디렉토리 구조를 생성합니다...")
        
        directories = [
            self.app_dir,
            self.app_dir / "models",
            self.app_dir / "services", 
            self.app_dir / "utils",
            self.app_dir / "ui",
            self.data_dir
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"   ✅ {directory}")
        
        # __init__.py 파일 생성
        init_files = [
            self.app_dir / "__init__.py",
            self.app_dir / "models" / "__init__.py",
            self.app_dir / "services" / "__init__.py",
            self.app_dir / "utils" / "__init__.py",
            self.app_dir / "ui" / "__init__.py"
        ]
        
        for init_file in init_files:
            if not init_file.exists():
                init_file.write_text("")
                print(f"   ✅ {init_file}")
    
    def install_dependencies(self):
        """의존성 패키지 설치"""
        print("📦 필요한 패키지를 설치합니다...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("   ✅ 패키지 설치 완료")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 패키지 설치 실패: {e}")
            return False
    
    def check_ollama(self):
        """Ollama 상태 확인"""
        print("🤖 Ollama 상태를 확인합니다...")
        
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                print("   ✅ Ollama 서비스가 실행 중입니다.")
                
                # 모델 확인
                lines = result.stdout.strip().split('\n')[1:]
                models = [line.split()[0] for line in lines if line.strip()]
                
                if models:
                    print("   📋 사용 가능한 모델:")
                    for model in models:
                        print(f"      • {model}")
                else:
                    print("   ⚠️  다운로드된 모델이 없습니다.")
                    print("   💡 권장 모델 다운로드:")
                    print("      ollama pull llama3.2:3b")
                return True
            else:
                print("   ❌ Ollama 서비스에 접근할 수 없습니다.")
                return False
                
        except FileNotFoundError:
            print("   ❌ Ollama가 설치되지 않았습니다.")
            print("   💡 https://ollama.ai 에서 설치해주세요.")
            return False
        except Exception as e:
            print(f"   ❌ Ollama 상태 확인 실패: {e}")
            return False
    
    def run_setup(self):
        """전체 설치 프로세스 실행"""
        print("=" * 60)
        print("🏥 OpenHealth 건강 도우미 설치를 시작합니다")
        print("=" * 60)
        print()
        
        try:
            # 1. 디렉토리 구조 생성
            self.create_directory_structure()
            print()
            
            # 2. 의존성 설치
            if not self.install_dependencies():
                print("❌ 설치 과정에서 오류가 발생했습니다.")
                return False
            print()
            
            # 3. Ollama 상태 확인
            self.check_ollama()
            print()
            
            # 4. 설치 완료
            print("=" * 60)
            print("✅ OpenHealth 설치가 완료되었습니다!")
            print("=" * 60)
            print()
            print("🚀 애플리케이션 실행 방법:")
            print("   python main.py")
            print()
            print("🌐 웹 브라우저 접속:")
            print("   http://localhost:8501")
            print()
            print("📚 추가 설정:")
            print("   • Ollama 모델 다운로드: ollama pull llama3.2:3b")
            print("   • 문서 확인: README.md")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ 설치 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    setup = OpenHealthSetup()
    success = setup.run_setup()
    
    if success:
        print("🎉 설치가 성공적으로 완료되었습니다!")
        
        # 바로 실행할지 묻기
        try:
            answer = input("\n지금 바로 OpenHealth를 실행하시겠습니까? (y/n): ").lower()
            if answer in ['y', 'yes', '예']:
                print("\n🚀 OpenHealth를 시작합니다...")
                subprocess.run([sys.executable, "main.py"])
        except KeyboardInterrupt:
            print("\n👋 설치가 완료되었습니다. 언제든 'python main.py'로 실행하세요!")
    else:
        print("❌ 설치에 실패했습니다. 오류를 확인하고 다시 시도해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()