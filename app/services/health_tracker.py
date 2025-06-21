"""
건강 데이터 추적 및 관리 서비스
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from loguru import logger

@dataclass
class HealthRecord:
    """건강 기록 데이터 클래스"""
    timestamp: str
    user_id: str
    record_type: str  # 'vital_signs', 'symptoms', 'medication', 'exercise', 'nutrition'
    data: Dict[str, Any]
    notes: Optional[str] = None

@dataclass
class VitalSigns:
    """생체 신호 데이터"""
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    body_temperature: Optional[float] = None
    blood_sugar: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None

class HealthDataTracker:
    """건강 데이터 추적 관리자"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.records_file = self.data_dir / "health_records.json"
        self.records = self._load_records()
    
    def _load_records(self) -> List[HealthRecord]:
        """저장된 기록 로드"""
        if self.records_file.exists():
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [HealthRecord(**record) for record in data]
            except Exception as e:
                logger.error(f"기록 로드 실패: {e}")
                return []
        return []
    
    def _save_records(self):
        """기록 저장"""
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(record) for record in self.records], 
                         f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"기록 저장 실패: {e}")
    
    def add_vital_signs(self, user_id: str, vital_signs: VitalSigns, 
                       notes: str = None) -> bool:
        """생체 신호 기록 추가"""
        try:
            record = HealthRecord(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                record_type="vital_signs",
                data=asdict(vital_signs),
                notes=notes
            )
            self.records.append(record)
            self._save_records()
            return True
        except Exception as e:
            logger.error(f"생체 신호 기록 실패: {e}")
            return False
    
    def add_symptom_record(self, user_id: str, symptoms: List[str], 
                          severity: int, notes: str = None) -> bool:
        """증상 기록 추가"""
        try:
            record = HealthRecord(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                record_type="symptoms",
                data={
                    "symptoms": symptoms,
                    "severity": severity,  # 1-10 척도
                    "duration": notes
                },
                notes=notes
            )
            self.records.append(record)
            self._save_records()
            return True
        except Exception as e:
            logger.error(f"증상 기록 실패: {e}")
            return False
    
    def add_medication_record(self, user_id: str, medication_name: str, 
                            dosage: str, frequency: str, notes: str = None) -> bool:
        """복용약 기록 추가"""
        try:
            record = HealthRecord(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                record_type="medication",
                data={
                    "medication_name": medication_name,
                    "dosage": dosage,
                    "frequency": frequency,
                    "taken": True
                },
                notes=notes
            )
            self.records.append(record)
            self._save_records()
            return True
        except Exception as e:
            logger.error(f"복용약 기록 실패: {e}")
            return False
    
    def get_user_records(self, user_id: str, 
                        record_type: Optional[str] = None,
                        days: int = 30) -> List[HealthRecord]:
        """사용자별 기록 조회"""
        start_date = datetime.now() - timedelta(days=days)
        
        filtered_records = []
        for record in self.records:
            if record.user_id != user_id:
                continue
            
            record_time = datetime.fromisoformat(record.timestamp)
            if record_time < start_date:
                continue
                
            if record_type and record.record_type != record_type:
                continue
                
            filtered_records.append(record)
        
        return sorted(filtered_records, key=lambda x: x.timestamp, reverse=True)
    
    def generate_health_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """건강 요약 보고서 생성"""
        records = self.get_user_records(user_id, days=days)
        
        summary = {
            "period": f"최근 {days}일",
            "total_records": len(records),
            "vital_signs": {},
            "symptoms": {},
            "medications": {},
            "trends": {},
            "alerts": []
        }
        
        # 생체 신호 요약
        vital_records = [r for r in records if r.record_type == "vital_signs"]
        if vital_records:
            summary["vital_signs"] = self._summarize_vital_signs(vital_records)
        
        # 증상 요약
        symptom_records = [r for r in records if r.record_type == "symptoms"]
        if symptom_records:
            summary["symptoms"] = self._summarize_symptoms(symptom_records)
        
        # 복용약 요약
        med_records = [r for r in records if r.record_type == "medication"]
        if med_records:
            summary["medications"] = self._summarize_medications(med_records)
        
        # 건강 알림 생성
        summary["alerts"] = self._generate_health_alerts(summary)
        
        return summary
    
    def _summarize_vital_signs(self, records: List[HealthRecord]) -> Dict[str, Any]:
        """생체 신호 요약"""
        df_data = []
        for record in records:
            data = record.data.copy()
            data['timestamp'] = record.timestamp
            df_data.append(data)
        
        if not df_data:
            return {}
        
        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        summary = {}
        
        # 혈압
        if 'blood_pressure_systolic' in df.columns:
            bp_data = df.dropna(subset=['blood_pressure_systolic', 'blood_pressure_diastolic'])
            if not bp_data.empty:
                summary['blood_pressure'] = {
                    'avg_systolic': round(bp_data['blood_pressure_systolic'].mean(), 1),
                    'avg_diastolic': round(bp_data['blood_pressure_diastolic'].mean(), 1),
                    'latest_systolic': int(bp_data.iloc[-1]['blood_pressure_systolic']),
                    'latest_diastolic': int(bp_data.iloc[-1]['blood_pressure_diastolic']),
                    'readings_count': len(bp_data)
                }
        
        # 심박수
        if 'heart_rate' in df.columns:
            hr_data = df.dropna(subset=['heart_rate'])
            if not hr_data.empty:
                summary['heart_rate'] = {
                    'avg': round(hr_data['heart_rate'].mean(), 1),
                    'min': int(hr_data['heart_rate'].min()),
                    'max': int(hr_data['heart_rate'].max()),
                    'latest': int(hr_data.iloc[-1]['heart_rate'])
                }
        
        # 체중
        if 'weight' in df.columns:
            weight_data = df.dropna(subset=['weight'])
            if not weight_data.empty:
                summary['weight'] = {
                    'current': float(weight_data.iloc[-1]['weight']),
                    'change': float(weight_data.iloc[-1]['weight'] - weight_data.iloc[0]['weight']) if len(weight_data) > 1 else 0,
                    'readings_count': len(weight_data)
                }
        
        return summary
    
    def _summarize_symptoms(self, records: List[HealthRecord]) -> Dict[str, Any]:
        """증상 요약"""
        all_symptoms = []
        severity_scores = []
        
        for record in records:
            data = record.data
            all_symptoms.extend(data.get('symptoms', []))
            severity_scores.append(data.get('severity', 0))
        
        from collections import Counter
        symptom_counts = Counter(all_symptoms)
        
        return {
            'most_common': dict(symptom_counts.most_common(5)),
            'avg_severity': round(sum(severity_scores) / len(severity_scores), 1) if severity_scores else 0,
            'total_reports': len(records),
            'unique_symptoms': len(symptom_counts)
        }
    
    def _summarize_medications(self, records: List[HealthRecord]) -> Dict[str, Any]:
        """복용약 요약"""
        medications = []
        for record in records:
            medications.append(record.data.get('medication_name', ''))
        
        from collections import Counter
        med_counts = Counter(medications)
        
        return {
            'medications_taken': dict(med_counts),
            'total_doses': len(records),
            'unique_medications': len(med_counts)
        }
    
    def _generate_health_alerts(self, summary: Dict[str, Any]) -> List[str]:
        """건강 알림 생성"""
        alerts = []
        
        # 혈압 체크
        if 'blood_pressure' in summary.get('vital_signs', {}):
            bp = summary['vital_signs']['blood_pressure']
            if bp['latest_systolic'] > 140 or bp['latest_diastolic'] > 90:
                alerts.append("⚠️ 최근 혈압이 높습니다. 의료진 상담을 권합니다.")
            elif bp['latest_systolic'] < 90 or bp['latest_diastolic'] < 60:
                alerts.append("⚠️ 최근 혈압이 낮습니다. 주의가 필요합니다.")
        
        # 심박수 체크
        if 'heart_rate' in summary.get('vital_signs', {}):
            hr = summary['vital_signs']['heart_rate']
            if hr['latest'] > 100:
                alerts.append("⚠️ 심박수가 빠릅니다. 휴식을 취하세요.")
            elif hr['latest'] < 60:
                alerts.append("ℹ️ 심박수가 낮습니다. 운동선수가 아니라면 확인이 필요합니다.")
        
        # 증상 체크
        if 'symptoms' in summary and summary['symptoms'].get('avg_severity', 0) > 7:
            alerts.append("⚠️ 심각한 증상이 지속되고 있습니다. 의료진 상담을 권합니다.")
        
        return alerts
    
    def create_vital_signs_chart(self, user_id: str, days: int = 7) -> Optional[go.Figure]:
        """생체 신호 차트 생성"""
        records = self.get_user_records(user_id, "vital_signs", days)
        
        if not records:
            return None
        
        # 데이터 준비
        timestamps = []
        systolic = []
        diastolic = []
        heart_rates = []
        
        for record in reversed(records):  # 시간순 정렬
            data = record.data
            timestamps.append(datetime.fromisoformat(record.timestamp))
            
            systolic.append(data.get('blood_pressure_systolic'))
            diastolic.append(data.get('blood_pressure_diastolic'))
            heart_rates.append(data.get('heart_rate'))
        
        # 차트 생성
        fig = go.Figure()
        
        # 혈압 그래프
        if any(systolic):
            fig.add_trace(go.Scatter(
                x=timestamps, y=systolic,
                name='수축기 혈압',
                line=dict(color='red')
            ))
        
        if any(diastolic):
            fig.add_trace(go.Scatter(
                x=timestamps, y=diastolic,
                name='이완기 혈압',
                line=dict(color='blue')
            ))
        
        # 심박수는 보조 y축 사용
        if any(heart_rates):
            fig.add_trace(go.Scatter(
                x=timestamps, y=heart_rates,
                name='심박수',
                line=dict(color='green'),
                yaxis='y2'
            ))
        
        # 레이아웃 설정
        fig.update_layout(
            title=f'생체 신호 추이 (최근 {days}일)',
            xaxis_title='날짜',
            yaxis_title='혈압 (mmHg)',
            yaxis2=dict(
                title='심박수 (bpm)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        return fig

# 전역 트래커 인스턴스
health_tracker = HealthDataTracker()