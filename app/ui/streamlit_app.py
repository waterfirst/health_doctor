"""
OpenHealth 건강 도우미 Streamlit 앱
"""

import streamlit as st
import asyncio
import json
from datetime import datetime, date
import plotly.graph_objects as go
from typing import Dict, Any
import sys
from pathlib import Path

# 상위 디렉토리를 Python 경로에 추가
app_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(app_dir))

try:
    from app.models.ollama_client import health_client
    from app.services.health_tracker import health_tracker, VitalSigns
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("프로젝트 구조를 확인하고 setup.py를 실행해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="OpenHealth 건강 도우미",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-good {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """세션 상태 초기화"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "default_user"
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "건강 상담"

def sidebar_navigation():
    """사이드바 네비게이션"""
    st.sidebar.title("🏥 OpenHealth")
    st.sidebar.markdown("---")
    
    # 사용자 정보
    st.sidebar.subheader("👤 사용자 정보")
    user_id = st.sidebar.text_input("사용자 ID", value=st.session_state.user_id)
    st.session_state.user_id = user_id
    
    st.sidebar.markdown("---")
    
    # 메뉴
    pages = [
        "🩺 건강 상담",
        "📊 건강 데이터",
        "📈 건강 추이",
        "💊 복용약 관리",
        "⚙️ 시스템 상태"
    ]
    
    selected_page = st.sidebar.selectbox("메뉴 선택", pages)
    st.session_state.current_page = selected_page.split(" ", 1)[1]
    
    return st.session_state.current_page

def health_consultation_page():
    """건강 상담 페이지"""
    st.markdown('<h1 class="main-header">🩺 AI 건강 상담</h1>', unsafe_allow_html=True)
    
    # 모델 상태 확인
    model_status = health_client.get_model_status()
    
    if not model_status["available_models"]:
        st.error("사용 가능한 Ollama 모델이 없습니다. 모델을 다운로드해주세요.")
        st.code("ollama pull llama3.2:3b")
        return
    
    # 모델 선택
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 건강 질문하기")
        
        # 질문 카테고리 선택
        question_type = st.selectbox(
            "질문 유형을 선택하세요:",
            ["일반 건강 상담", "증상 분석", "응급 상황", "예방 관리"]
        )
        
        # 사용자 입력
        user_question = st.text_area(
            "증상이나 건강 관련 질문을 입력하세요:",
            placeholder="예: 머리가 아프고 열이 나는데 어떻게 해야 할까요?",
            height=100
        )
        
        # 추가 정보
        additional_info = st.text_input(
            "추가 정보 (나이, 성별, 기존 질환 등):",
            placeholder="예: 30세 여성, 고혈압 있음"
        )
        
        if st.button("💡 AI 상담 받기", type="primary"):
            if user_question:
                with st.spinner("AI가 답변을 생성 중입니다..."):
                    # 특화 분야 매핑
                    specialty_map = {
                        "일반 건강 상담": "general_health",
                        "증상 분석": "symptom_analysis", 
                        "응급 상황": "quick_response",
                        "예방 관리": "preventive_care"
                    }
                    
                    specialty = specialty_map.get(question_type, "general_health")
                    
                    # 비동기 함수를 동기로 실행
                    result = asyncio.run(health_client.get_health_advice(
                        user_question, specialty, additional_info
                    ))
                    
                    if result.get("error"):
                        st.error(f"오류 발생: {result['error']}")
                    else:
                        # 응답 표시
                        st.success("✅ AI 답변:")
                        st.markdown(result["response"])
                        
                        # 메타 정보
                        st.info(f"사용된 모델: {result['model_used']} | 특화분야: {result['specialty']}")
                        
                        # 채팅 기록에 추가
                        st.session_state.chat_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "question": user_question,
                            "answer": result["response"],
                            "model": result["model_used"]
                        })
            else:
                st.warning("질문을 입력해주세요.")
    
    with col2:
        st.subheader("🤖 사용 가능한 모델")
        
        for model_name, spec in model_status["model_specialties"].items():
            status_icon = "✅" if spec["available"] else "❌"
            st.markdown(f"""
            **{status_icon} {model_name}**
            - 특화: {spec['specialty']}
            - 설명: {spec['description']}
            """)
    
    # 최근 상담 기록
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📋 최근 상담 기록")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
            with st.expander(f"상담 {len(st.session_state.chat_history)-i}: {chat['question'][:50]}..."):
                st.write(f"**질문:** {chat['question']}")
                st.write(f"**답변:** {chat['answer']}")
                st.caption(f"모델: {chat['model']} | 시간: {chat['timestamp']}")

def health_data_page():
    """건강 데이터 입력 페이지"""
    st.markdown('<h1 class="main-header">📊 건강 데이터 관리</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["생체 신호", "증상 기록", "복용약"])
    
    with tab1:
        st.subheader("🩺 생체 신호 입력")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**혈압 측정**")
            systolic = st.number_input("수축기 혈압 (mmHg)", min_value=60, max_value=250, value=120)
            diastolic = st.number_input("이완기 혈압 (mmHg)", min_value=40, max_value=150, value=80)
            
            st.write("**심박수**")
            heart_rate = st.number_input("심박수 (bpm)", min_value=40, max_value=200, value=70)
            
        with col2:
            st.write("**체온 및 체중**")
            temperature = st.number_input("체온 (°C)", min_value=35.0, max_value=42.0, value=36.5, step=0.1)
            weight = st.number_input("체중 (kg)", min_value=20.0, max_value=200.0, value=70.0, step=0.1)
            
            st.write("**혈당**")
            blood_sugar = st.number_input("혈당 (mg/dL)", min_value=50, max_value=500, value=100)
        
        notes = st.text_area("메모", placeholder="측정 상황, 컨디션 등")
        
        if st.button("생체 신호 저장", type="primary"):
            vital_signs = VitalSigns(
                blood_pressure_systolic=systolic,
                blood_pressure_diastolic=diastolic,
                heart_rate=heart_rate,
                body_temperature=temperature,
                weight=weight,
                blood_sugar=blood_sugar
            )
            
            if health_tracker.add_vital_signs(st.session_state.user_id, vital_signs, notes):
                st.success("✅ 생체 신호가 저장되었습니다!")
            else:
                st.error("❌ 저장에 실패했습니다.")
    
    with tab2:
        st.subheader("🤒 증상 기록")
        
        # 일반적인 증상 체크박스
        st.write("**일반적인 증상 (해당되는 것을 선택하세요)**")
        symptoms_options = [
            "두통", "발열", "기침", "인후통", "콧물", "코막힘",
            "복통", "설사", "변비", "구토", "어지러움", "피로감",
            "근육통", "관절통", "발진", "가려움", "불면증", "식욕부진"
        ]
        
        selected_symptoms = []
        cols = st.columns(3)
        for i, symptom in enumerate(symptoms_options):
            with cols[i % 3]:
                if st.checkbox(symptom):
                    selected_symptoms.append(symptom)
        
        # 추가 증상
        custom_symptoms = st.text_input("기타 증상", placeholder="위에 없는 증상을 입력하세요")
        if custom_symptoms:
            selected_symptoms.extend([s.strip() for s in custom_symptoms.split(",")])
        
        # 증상 심각도
        severity = st.slider("증상의 심각도 (1: 매우 가벼움, 10: 매우 심각함)", 1, 10, 5)
        
        # 지속 기간
        duration = st.text_input("증상 지속 기간", placeholder="예: 2일째, 오늘 아침부터")
        
        if st.button("증상 기록 저장", type="primary"):
            if selected_symptoms:
                if health_tracker.add_symptom_record(
                    st.session_state.user_id, selected_symptoms, severity, duration
                ):
                    st.success("✅ 증상이 기록되었습니다!")
                else:
                    st.error("❌ 저장에 실패했습니다.")
            else:
                st.warning("증상을 선택해주세요.")
    
    with tab3:
        st.subheader("💊 복용약 기록")
        
        col1, col2 = st.columns(2)
        
        with col1:
            medication_name = st.text_input("약물명", placeholder="예: 타이레놀, 아스피린")
            dosage = st.text_input("용량", placeholder="예: 500mg, 1정")
            
        with col2:
            frequency = st.selectbox("복용 빈도", [
                "하루 1회", "하루 2회", "하루 3회", 
                "필요시", "일주일에 1회", "기타"
            ])
            
            if frequency == "기타":
                frequency = st.text_input("복용 빈도 상세")
        
        med_notes = st.text_area("복용 메모", placeholder="복용 시간, 식전/식후, 부작용 등")
        
        if st.button("복용약 기록 저장", type="primary"):
            if medication_name and dosage:
                if health_tracker.add_medication_record(
                    st.session_state.user_id, medication_name, dosage, frequency, med_notes
                ):
                    st.success("✅ 복용약이 기록되었습니다!")
                else:
                    st.error("❌ 저장에 실패했습니다.")
            else:
                st.warning("약물명과 용량을 입력해주세요.")

def health_trends_page():
    """건강 추이 분석 페이지"""
    st.markdown('<h1 class="main-header">📈 건강 추이 분석</h1>', unsafe_allow_html=True)
    
    # 기간 선택
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analysis_period = st.selectbox("분석 기간", [7, 14, 30, 90])
        
    # 건강 요약 생성
    summary = health_tracker.generate_health_summary(st.session_state.user_id, analysis_period)
    
    if summary["total_records"] == 0:
        st.info("📝 기록된 건강 데이터가 없습니다. 먼저 건강 데이터를 입력해주세요.")
        return
    
    # 건강 알림
    if summary["alerts"]:
        st.markdown("### 🚨 건강 알림")
        for alert in summary["alerts"]:
            if "⚠️" in alert:
                st.markdown(f'<div class="status-danger">{alert}</div>', unsafe_allow_html=True)
            elif "ℹ️" in alert:
                st.markdown(f'<div class="status-warning">{alert}</div>', unsafe_allow_html=True)
    
    # 메트릭 카드들
    st.markdown("### 📊 건강 지표 요약")
    
    col1, col2, col3 = st.columns(3)
    
    # 생체 신호 요약
    if summary["vital_signs"]:
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("총 기록 수", summary["total_records"])
            
            if "blood_pressure" in summary["vital_signs"]:
                bp = summary["vital_signs"]["blood_pressure"]
                st.metric(
                    "평균 혈압", 
                    f"{bp['avg_systolic']:.0f}/{bp['avg_diastolic']:.0f}",
                    f"최근: {bp['latest_systolic']}/{bp['latest_diastolic']}"
                )
            
            if "heart_rate" in summary["vital_signs"]:
                hr = summary["vital_signs"]["heart_rate"]
                st.metric("평균 심박수", f"{hr['avg']:.0f} bpm", f"최근: {hr['latest']} bpm")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 증상 요약
    if summary["symptoms"]:
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🤒 증상 현황")
            
            symptoms = summary["symptoms"]
            st.metric("증상 보고 횟수", symptoms["total_reports"])
            st.metric("평균 심각도", f"{symptoms['avg_severity']:.1f}/10")
            
            if symptoms["most_common"]:
                st.write("**주요 증상:**")
                for symptom, count in list(symptoms["most_common"].items())[:3]:
                    st.write(f"• {symptom}: {count}회")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 복용약 요약
    if summary["medications"]:
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("💊 복용약 현황")
            
            meds = summary["medications"]
            st.metric("총 복용 횟수", meds["total_doses"])
            st.metric("복용 약물 종류", meds["unique_medications"])
            
            if meds["medications_taken"]:
                st.write("**복용 약물:**")
                for med, count in list(meds["medications_taken"].items())[:3]:
                    st.write(f"• {med}: {count}회")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 차트 표시
    st.markdown("### 📈 생체 신호 추이")
    
    chart = health_tracker.create_vital_signs_chart(st.session_state.user_id, analysis_period)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("표시할 생체 신호 데이터가 없습니다.")

def system_status_page():
    """시스템 상태 페이지"""
    st.markdown('<h1 class="main-header">⚙️ 시스템 상태</h1>', unsafe_allow_html=True)
    
    # Ollama 모델 상태
    model_status = health_client.get_model_status()
    
    st.subheader("🤖 Ollama 모델 상태")
    
    if model_status["available_models"]:
        for model_name, spec in model_status["model_specialties"].items():
            status = "🟢 사용 가능" if spec["available"] else "🔴 사용 불가"
            
            with st.expander(f"{status} {model_name}"):
                st.write(f"**특화 분야:** {spec['specialty']}")
                st.write(f"**설명:** {spec['description']}")
                
                if spec["available"]:
                    # 간단한 테스트 버튼
                    if st.button(f"{model_name} 테스트", key=f"test_{model_name}"):
                        with st.spinner("모델 테스트 중..."):
                            result = asyncio.run(health_client.get_health_advice(
                                "안녕하세요, 잘 작동하나요?", 
                                spec['specialty']
                            ))
                            
                            if result.get("error"):
                                st.error(f"테스트 실패: {result['error']}")
                            else:
                                st.success("✅ 모델이 정상 작동합니다!")
                                st.write(result["response"][:200] + "...")
    else:
        st.error("사용 가능한 모델이 없습니다.")
        st.markdown("""
        **모델 설치 방법:**
        ```bash
        ollama pull llama3.2:3b
        ollama pull qwen2.5:7b  
        ollama pull gemma2:9b
        ollama pull deepseek-r1:1.5b
        ```
        """)
    
    # 데이터 상태
    st.subheader("📊 데이터 상태")
    
    user_records = health_tracker.get_user_records(st.session_state.user_id, days=365)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vital_records = [r for r in user_records if r.record_type == "vital_signs"]
        st.metric("생체 신호 기록", len(vital_records))
    
    with col2:
        symptom_records = [r for r in user_records if r.record_type == "symptoms"]
        st.metric("증상 기록", len(symptom_records))
    
    with col3:
        med_records = [r for r in user_records if r.record_type == "medication"]
        st.metric("복용약 기록", len(med_records))
    
    # 데이터 내보내기/가져오기
    st.subheader("💾 데이터 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 데이터 내보내기"):
            # JSON 형태로 데이터 내보내기
            export_data = {
                "user_id": st.session_state.user_id,
                "export_date": datetime.now().isoformat(),
                "records": [
                    {
                        "timestamp": r.timestamp,
                        "record_type": r.record_type,
                        "data": r.data,
                        "notes": r.notes
                    }
                    for r in user_records
                ]
            }
            
            st.download_button(
                label="💾 JSON 파일 다운로드",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"health_data_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 데이터 가져오기", type=['json'])
        if uploaded_file:
            try:
                import_data = json.load(uploaded_file)
                st.success(f"✅ {len(import_data.get('records', []))}개의 기록을 가져올 준비가 되었습니다.")
                
                if st.button("데이터 가져오기 실행"):
                    # 실제 구현에서는 데이터 검증 및 중복 처리 필요
                    st.info("데이터 가져오기 기능은 추후 구현 예정입니다.")
            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")

def main():
    """메인 애플리케이션"""
    initialize_session_state()
    
    # 네비게이션
    current_page = sidebar_navigation()
    
    # 페이지 라우팅
    if current_page == "건강 상담":
        health_consultation_page()
    elif current_page == "건강 데이터":
        health_data_page()
    elif current_page == "건강 추이":
        health_trends_page()
    elif current_page == "복용약 관리":
        health_data_page()  # 탭으로 구현됨
    elif current_page == "시스템 상태":
        system_status_page()
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🏥 OpenHealth v1.0 | Powered by Ollama & Streamlit<br>
        ⚠️ 이 도구는 의료 조언을 대체하지 않습니다. 심각한 증상이 있으면 의료진에게 상담하세요.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()