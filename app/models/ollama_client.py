"""
클라우드용 Ollama 클라이언트 - HTTP API 사용
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import os

@dataclass
class ModelInfo:
    """모델 정보 클래스"""
    name: str
    size: str
    specialty: str
    description: str

class CloudOllamaClient:
    """클라우드 환경용 Ollama 클라이언트 (HTTP API 사용)"""
    
    def __init__(self):
        # 환경변수에서 Ollama 서버 URL 가져오기 (기본값: 로컬)
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.available_models = self._get_available_models()
        self.model_specs = self._define_model_specialties()
        
    def _get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 조회 (HTTP API)"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            else:
                return []
        except Exception as e:
            print(f"모델 목록 조회 실패: {e}")
            return []
    
    def _define_model_specialties(self) -> Dict[str, ModelInfo]:
        """각 모델의 특화 분야 정의"""
        return {
            'llama3.2:3b': ModelInfo(
                name='llama3.2:3b',
                size='2.0 GB',
                specialty='general_health',
                description='일반적인 건강 상담 및 기본 의료 정보 제공'
            ),
            'qwen2.5:7b': ModelInfo(
                name='qwen2.5:7b',
                size='4.7 GB',
                specialty='symptom_analysis',
                description='증상 분석 및 상세한 의료 정보 제공'
            ),
            'gemma2:9b': ModelInfo(
                name='gemma2:9b',
                size='5.4 GB',
                specialty='preventive_care',
                description='예방 의학 및 생활습관 개선 조언'
            ),
            'deepseek-r1:1.5b': ModelInfo(
                name='deepseek-r1:1.5b',
                size='1.1 GB',
                specialty='quick_response',
                description='빠른 응급 상황 대응 및 간단한 건강 질문'
            )
        }
    
    def get_model_by_specialty(self, specialty: str) -> Optional[str]:
        """특화 분야에 따른 최적 모델 선택"""
        for model_name, info in self.model_specs.items():
            if info.specialty == specialty and model_name in self.available_models:
                return model_name
        return None
    
    def create_health_prompt(self, user_input: str, context: str = "", 
                           prompt_type: str = "general") -> str:
        """건강 상담용 프롬프트 생성"""
        
        base_prompt = """당신은 전문적인 건강 상담 AI입니다. 다음 지침을 따라주세요:

1. 의료 전문가가 아니므로 확정적인 진단은 하지 마세요
2. 심각한 증상의 경우 반드시 의료진 상담을 권하세요
3. 근거 있는 일반적인 건강 정보만 제공하세요
4. 친근하고 이해하기 쉬운 언어를 사용하세요
5. 응급상황 시 즉시 응급실 방문을 권하세요

"""
        
        prompt_templates = {
            "general": base_prompt + f"""
사용자 질문: {user_input}
{f"추가 컨텍스트: {context}" if context else ""}

친절하고 도움이 되는 건강 조언을 제공해주세요.
""",
            
            "symptom_analysis": base_prompt + f"""
사용자가 다음 증상을 호소하고 있습니다:
증상: {user_input}
{f"추가 정보: {context}" if context else ""}

1. 가능한 원인들을 나열해주세요 (일반적인 것부터 심각한 것까지)
2. 자가 관리 방법을 제안해주세요
3. 언제 의료진을 만나야 하는지 알려주세요
4. 응급상황의 징후가 있다면 명확히 지적해주세요
""",
            
            "emergency": base_prompt + f"""
응급상황 가능성이 있는 증상입니다:
증상: {user_input}

즉시 다음 사항을 확인하고 적절한 조치를 안내해주세요:
1. 즉시 응급실에 가야 하는지 판단
2. 응급처치 방법 (있다면)
3. 119 신고가 필요한지 여부
4. 병원 이동 시 주의사항
"""
        }
        
        return prompt_templates.get(prompt_type, prompt_templates["general"])
    
    async def get_health_advice(self, user_input: str, 
                               specialty: str = "general_health",
                               context: str = "") -> Dict[str, Any]:
        """건강 조언 요청 (HTTP API 사용)"""
        
        # Ollama 서버가 사용 불가능한 경우 더미 응답 반환
        if not self.available_models:
            return self._get_fallback_response(user_input, specialty)
        
        # 특화 분야에 맞는 모델 선택
        model_name = self.get_model_by_specialty(specialty)
        if not model_name:
            model_name = self.available_models[0] if self.available_models else None
            
        if not model_name:
            return self._get_fallback_response(user_input, specialty)
        
        # 프롬프트 타입 결정
        prompt_type = self._determine_prompt_type(user_input)
        prompt = self.create_health_prompt(user_input, context, prompt_type)
        
        try:
            # HTTP API로 요청
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "model_used": model_name,
                    "specialty": specialty,
                    "prompt_type": prompt_type,
                    "response": result['message']['content'],
                    "error": None
                }
            else:
                return self._get_fallback_response(user_input, specialty)
                
        except Exception as e:
            print(f"모델 응답 생성 실패: {e}")
            return self._get_fallback_response(user_input, specialty)
    
    def _get_fallback_response(self, user_input: str, specialty: str) -> Dict[str, Any]:
        """Ollama 서버를 사용할 수 없을 때의 대체 응답"""
        
        # 키워드 기반 기본 응답
        fallback_responses = {
            "두통": "두통의 일반적인 원인으로는 스트레스, 수면 부족, 탈수, 긴장성 두통 등이 있습니다. 충분한 휴식과 수분 섭취를 권하며, 지속되거나 심한 경우 의료진 상담을 받으세요.",
            "발열": "발열은 몸의 자연스러운 방어 반응입니다. 충분한 휴식과 수분 섭취가 중요하며, 38.5도 이상의 고열이나 다른 심각한 증상이 동반되면 즉시 의료진에게 상담받으세요.",
            "기침": "기침의 원인은 감기, 알레르기, 건조한 공기 등 다양합니다. 충분한 수분 섭취와 가습기 사용이 도움될 수 있으며, 2주 이상 지속되면 의료진 상담을 권합니다.",
            "복통": "복통의 원인은 매우 다양합니다. 가벼운 소화불량일 수도 있지만, 심한 통증이나 발열, 구토가 동반되면 즉시 응급실을 방문하세요."
        }
        
        # 키워드 매칭으로 응답 선택
        response = "죄송합니다. 현재 AI 모델 서버에 연결할 수 없습니다. 일반적인 건강 관리 수칙을 따르시고, 증상이 지속되거나 악화되면 반드시 의료진에게 상담받으시기 바랍니다."
        
        for keyword, fallback in fallback_responses.items():
            if keyword in user_input:
                response = fallback
                break
        
        return {
            "model_used": "fallback_system",
            "specialty": specialty,
            "prompt_type": "fallback",
            "response": response + "\n\n⚠️ 참고: 현재 로컬 AI 모델이 연결되지 않아 기본 응답을 제공합니다. 정확한 의료 상담은 전문의에게 받으시기 바랍니다.",
            "error": None
        }
    
    def _determine_prompt_type(self, user_input: str) -> str:
        """사용자 입력을 분석하여 프롬프트 타입 결정"""
        emergency_keywords = [
            '가슴통증', '호흡곤란', '의식잃음', '심한복통', '고열', 
            '출혈', '외상', '골절', '화상', '중독', '알레르기반응'
        ]
        
        symptom_keywords = [
            '아프', '통증', '열', '기침', '두통', '복통', '설사', 
            '구토', '어지러', '피로', '불면', '발진'
        ]
        
        user_lower = user_input.lower()
        
        if any(keyword in user_lower for keyword in emergency_keywords):
            return "emergency"
        elif any(keyword in user_lower for keyword in symptom_keywords):
            return "symptom_analysis"
        else:
            return "general"
    
    def get_model_status(self) -> Dict[str, Any]:
        """모델 상태 정보 반환"""
        return {
            "available_models": self.available_models,
            "model_specialties": {
                name: {
                    "specialty": info.specialty,
                    "description": info.description,
                    "available": name in self.available_models
                }
                for name, info in self.model_specs.items()
            },
            "server_status": "connected" if self.available_models else "disconnected",
            "fallback_mode": len(self.available_models) == 0
        }

# 전역 클라이언트 인스턴스
health_client = CloudOllamaClient()