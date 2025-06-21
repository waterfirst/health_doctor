# 🚀 OpenHealth 빠른 시작 가이드

## ⚡ 5분 만에 시작하기

### 1단계: Ollama 설치 (2분)
```bash
# Windows/macOS/Linux에서 https://ollama.ai 접속하여 다운로드
# 설치 후 터미널에서 확인
ollama --version
```

### 2단계: 모델 다운로드 (3분)
```bash
# 가장 빠른 모델부터 시작 (필수)
ollama pull deepseek-r1:1.5b    # 1.1GB - 30초

# 권장 모델 (선택사항)
ollama pull llama3.2:3b         # 2.0GB - 1분
ollama pull qwen2.5:7b          # 4.7GB - 2분  
ollama pull gemma2:9b           # 5.4GB - 3분
```

### 3단계: OpenHealth 설치 및 실행 (1분)
```bash
# 프로젝트 클론
git clone https://github.com/waterfirst/health_doctor.git
cd health_doctor

# 가상환경 생성 (선택사항)
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 자동 설치 실행
python setup.py

# 애플리케이션 시작
python main.py
```

### 4단계: 웹 브라우저 접속
```
http://localhost:8501
```

## 🎯 첫 사용법

### 건강 상담 체험하기
1. **🩺 건강 상담** 메뉴 클릭
2. 질문 입력: "두통이 있는데 어떻게 해야 할까요?"
3. **AI 상담 받기** 버튼 클릭
4. AI 답변 확인

### 건강 데이터 입력하기  
1. **📊 건강 데이터** 메뉴 클릭
2. 혈압, 심박수 등 입력
3. **데이터 저장** 버튼 클릭
4. 기록 확인

## 🔧 문제 해결

### Ollama 연결 안 됨
```bash
# Ollama 서비스 확인
ollama list

# 재시작이 필요한 경우
# Windows: 작업관리자에서 Ollama 종료 후 재시작
# macOS/Linux: ollama serve
```

### 포트 충돌
```bash
# 다른 포트로 실행
streamlit run app/ui/streamlit_app.py --server.port 8502
```

### 메모리 부족
- 가장 작은 모델부터: `deepseek-r1:1.5b` (1.1GB)
- RAM 8GB 이상 권장
- 다른 프로그램 종료 후 재시도

## 📱 주요 기능 미리보기

### 🤖 AI 모델별 특화 기능
- **deepseek-r1:1.5b**: 빠른 응급 대응
- **llama3.2:3b**: 일반 건강 상담  
- **qwen2.5:7b**: 상세한 증상 분석
- **gemma2:9b**: 예방 의학 조언

### 📊 건강 추적 기능
- 혈압, 심박수, 체온, 체중 기록
- 증상 심각도 추적 (1-10 점수)
- 복용약 관리 및 일정
- 시각적 차트 및 트렌드 분석

### ⚠️ 안전 기능
- 응급상황 자동 감지
- 의료진 상담 권고 알림
- 개인정보 로컬 저장 (외부 전송 없음)

## 🎯 사용 팁

### 효과적인 질문 방법
```
❌ 나쁜 예: "아파요"
✅ 좋은 예: "2일 전부터 오른쪽 머리가 욱신욱신 아프고, 특히 아침에 심합니다. 30세 여성이고 평소 두통은 거의 없었습니다."
```

### 정확한 데이터 입력
- **정기적으로**: 매일 같은 시간에 측정
- **일관성 있게**: 같은 조건에서 측정  
- **상세하게**: 메모란에 상황 기록

### 개인정보 보호
- 모든 데이터는 로컬 컴퓨터에만 저장
- 네트워크로 전송되지 않음
- 언제든 데이터 삭제/내보내기 가능

## 📈 고급 사용법

### 여러 사용자 관리
- 사이드바에서 사용자 ID 변경
- 가족 구성원별 데이터 분리 관리

### 데이터 백업
- **시스템 상태** 메뉴에서 데이터 내보내기
- JSON 파일로 백업 가능

### 커스터마이징
- `app/models/ollama_client.py`에서 프롬프트 수정
- `app/ui/streamlit_app.py`에서 UI 커스터마이징

## ⚡ 성능 최적화

### 시스템 요구사항
- **최소**: RAM 4GB, HDD 여유공간 5GB
- **권장**: RAM 8GB+, SSD 10GB+
- **최적**: RAM 16GB+, SSD 20GB+

### 모델 선택 가이드
| 시스템 | 권장 모델 | 용도 |
|--------|-----------|------|
| 저사양 | deepseek-r1:1.5b | 빠른 기본 상담 |
| 중간 | llama3.2:3b | 일반적인 모든 기능 |
| 고사양 | 모든 모델 | 최고 품질 상담 |

## 🆘 지원

### 문제 신고
- GitHub Issues: https://github.com/waterfirst/health_doctor/issues

### 업데이트
```bash
# 최신 버전 확인
git pull origin main
python setup.py  # 재설치
```

---

**🎉 이제 AI 건강 도우미를 마음껏 활용해보세요!**

*⚠️ 주의: 이 도구는 의료 조언을 대체하지 않습니다. 심각한 증상이 있으면 반드시 의료진에게 상담받으세요.*