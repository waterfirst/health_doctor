# 🏥 OpenHealth 건강 도우미

AI 기반 개인 건강 관리 도우미 애플리케이션입니다. 로컬 LLM 모델(Ollama)을 사용하여 프라이버시를 보장하면서 건강 상담 서비스를 제공합니다.

## ✨ 주요 기능

### 🩺 AI 건강 상담
- **다중 LLM 모델 지원**: 각 모델의 특성에 맞는 전문 상담
- **증상 분석**: 사용자 증상을 분석하고 초기 진단 제안
- **응급상황 대응**: 응급 증상 감지 및 대응 가이드
- **맞춤형 조언**: 개인별 건강 관리 팁 제공

### 📊 건강 데이터 관리
- **생체 신호 추적**: 혈압, 심박수, 체온, 체중, 혈당 기록
- **증상 기록**: 다양한 증상과 심각도 추적
- **복용약 관리**: 복용 약물 및 일정 관리
- **데이터 시각화**: 건강 지표 추이 그래프

### 📈 건강 분석
- **추이 분석**: 시간별 건강 지표 변화 추적
- **건강 알림**: 이상 징후 자동 감지 및 알림
- **요약 보고서**: 주기적 건강 상태 요약

## 🚀 설치 및 실행

### 1. 사전 요구사항

#### Ollama 설치
```bash
# Windows/macOS/Linux
# https://ollama.ai 에서 다운로드 후 설치
```

#### Python 환경
```bash
# Python 3.8 이상 필요
python --version
```

### 2. 프로젝트 설정

```bash
# 프로젝트 클론
git clone https://github.com/waterfirst/health_doctor.git
cd health_doctor

# 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 3. Ollama 모델 다운로드

```bash
# 필수 모델들 다운로드 (용량에 따라 시간 소요)
ollama pull llama3.2:3b      # 2.0 GB - 일반 건강 상담
ollama pull qwen2.5:7b       # 4.7 GB - 증상 분석
ollama pull gemma2:9b        # 5.4 GB - 예방 의학
ollama pull deepseek-r1:1.5b # 1.1 GB - 빠른 응답

# 모델 확인
ollama list
```

### 4. 의존성 설치

```bash
pip install -r requirements.txt
```

### 5. 애플리케이션 실행

```bash
# 자동 설치 및 실행
python setup.py

# 또는 메인 애플리케이션 직접 실행
python main.py

# 또는 Streamlit 직접 실행
streamlit run app/ui/streamlit_app.py
```

### 6. 웹 브라우저에서 접속

```
http://localhost:8501
```

## 🤖 지원 모델별 특화 기능

| 모델 | 크기 | 특화 분야 | 주요 용도 |
|------|------|-----------|-----------|
| **llama3.2:3b** | 2.0 GB | 일반 건강 상담 | 기본 의료 정보, 생활습관 조언 |
| **qwen2.5:7b** | 4.7 GB | 증상 분석 | 상세한 증상 분석, 원인 추론 |
| **gemma2:9b** | 5.4 GB | 예방 의학 | 건강 예방, 생활습관 개선 |
| **deepseek-r1:1.5b** | 1.1 GB | 빠른 응답 | 응급 상황, 간단한 질문 |

## 📱 사용 방법

### 1. 건강 상담
1. 사이드바에서 "🩺 건강 상담" 선택
2. 질문 유형 선택 (일반/증상분석/응급/예방)
3. 증상이나 질문 입력
4. 추가 정보 입력 (나이, 성별, 기존 질환 등)
5. "AI 상담 받기" 클릭

### 2. 건강 데이터 입력
1. "📊 건강 데이터" 메뉴 선택
2. 탭별로 데이터 입력:
   - **생체 신호**: 혈압, 심박수, 체온, 체중 등
   - **증상 기록**: 증상 선택 및 심각도 입력
   - **복용약**: 약물명, 용량, 복용 빈도

### 3. 건강 추이 확인
1. "📈 건강 추이" 메뉴 선택
2. 분석 기간 선택 (7일/14일/30일/90일)
3. 건강 지표 요약 및 차트 확인
4. 건강 알림 확인

## ⚠️ 중요 안내사항

### 의료 면책 조항
- 이 애플리케이션은 **의료 조언을 대체하지 않습니다**
- 심각한 증상이나 응급상황 시 반드시 의료진에게 상담하세요
- AI 답변은 참고용으로만 사용하시기 바랍니다

### 데이터 프라이버시
- 모든 데이터는 **로컬에 저장**됩니다
- 외부 서버로 전송되지 않습니다
- Ollama를 통한 로컬 AI 처리로 프라이버시 보장

## 🛠️ 문제 해결

### Ollama 연결 문제
```bash
# Ollama 서비스 상태 확인
ollama list

# Ollama 서비스 재시작
# Windows: 작업 관리자에서 Ollama 프로세스 종료 후 재시작
# macOS/Linux: 터미널에서 ollama serve
```

### 메모리 부족 문제
- 작은 모델부터 시작: `deepseek-r1:1.5b` 또는 `llama3.2:3b`
- 시스템 RAM 8GB 이상 권장
- 다른 애플리케이션 종료 후 실행

### 포트 충돌 문제
```bash
# 다른 포트로 실행
streamlit run app/ui/streamlit_app.py --server.port 8502
```

## 🔧 개발자 정보

### 기술 스택
- **Backend**: Python, Ollama
- **Frontend**: Streamlit
- **Data**: Pandas, JSON
- **Visualization**: Plotly
- **AI Models**: Llama, Qwen, Gemma, DeepSeek

### 프로젝트 구조
```
health_doctor/
├── app/
│   ├── models/
│   │   └── ollama_client.py
│   ├── services/
│   │   └── health_tracker.py
│   └── ui/
│       └── streamlit_app.py
├── data/
│   └── health_records.json
├── main.py
├── setup.py
├── requirements.txt
└── README.md
```

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**⚡ 빠른 시작:**
```bash
git clone https://github.com/waterfirst/health_doctor.git
cd health_doctor
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.2:3b
python setup.py
```

🌐 **웹 접속**: http://localhost:8501