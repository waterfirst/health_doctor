"""
OpenAI API 클라이언트 - 클라우드 배포용
"""

import openai
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

@dataclass
class ModelInfo:
    """모델 정보 클래스"""
    name: str
    size: str
    specialty: str
    description: str

class OpenAIHealthClient:
    """OpenAI API를 사용한 건강 상담 클라이언트"""
    
    def __init__(self):
        # 환경변수에서 API 키 가져오기
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.available = True
        else:
            self.available = False
            
        self.model_specs = self._define_model_specialties()
        
    def _define_model_specialties(self) -> Dict[str, ModelInfo]:
        """OpenAI 모델의 특화 분야 정의"""
        return {
            'gpt-4': ModelInfo(
                name='gpt-4',
                size='Large',
                specialty='general_health',
                description='고급 건강 상담 및 복합적 의료 정보 분석'
            ),
            'gpt-3.5-turbo': ModelInfo(
                name='gpt-3.5-turbo',
                size='Medium',
                specialty='symptom_analysis',
                description='빠른 증상 분석 및 일반적인 건강 조언'
            )
        }
    
    def get_model_by_specialty(self, specialty: str) -> str:
        """특화 분야에 맞는 최적 모델 선택"""
        specialty_map = {
            'general_health': 'gpt-4',
            'symptom_analysis': 'gpt-3.5-turbo',
            'preventive_care': 'gpt-4',
            'quick_response': 'gpt-3.5-turbo'
        }
        return specialty_map.get(specialty, 'gpt-3.5-turbo')
    
    def create_health_prompt(self, user_input: str, context: str = "", 
                           prompt_type: str = "general") -> str:
        """건강 상담용 프롬프트 생성"""
        
        base_prompt = """당신은 전문적인 건강 상담 AI입니다. 다음 지침을 따라주세요:

1. 의료 전문가가 아니므로 확정적인 진단은 하지 마세요
2. 심각한 증상의 경우 반드시 의료진 상담을 권하세요
3. 근거 있는 일반적인 건강 정보만 제공하세요
4. 친근하고 이해하기 쉬운 한국어를 사용하세요
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
        """건강 조언 요청 (OpenAI API 사용)"""
        
        if not self.available:
            return self._get_fallback_response(user_input, specialty)
        
        # 특화 분야에 맞는 모델 선택
        model_name = self.get_model_by_specialty(specialty)
        
        # 프롬프트 타입 결정
        prompt_type = self._determine_prompt_type(user_input)
        prompt = self.create_health_prompt(user_input, context, prompt_type)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 친절하고 신중한 건강 상담 AI입니다. 의료 조언을 대체하지 않으며, 항상 전문의 상담을 권장합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "model_used": model_name,
                "specialty": specialty,
                "prompt_type": prompt_type,
                "response": response.choices[0].message.content,
                "error": None
            }
            
        except Exception as e:
            print(f"OpenAI API 요청 실패: {e}")
            return self._get_fallback_response(user_input, specialty)
    
    def _get_fallback_response(self, user_input: str, specialty: str) -> Dict[str, Any]:
        """API를 사용할 수 없을 때의 대체 응답"""
        
        fallback_responses = {
            "두통": "두통의 일반적인 원인으로는 스트레스, 수면 부족, 탈수, 긴장성 두통 등이 있습니다. 충분한 휴식과 수분 섭취를 권하며, 지속되거나 심한 경우 의료진 상담을 받으세요.",
            "발열": "발열은 몸의 자연스러운 방어 반응입니다. 충분한 휴식과 수분 섭취가 중요하며, 38.5도 이상의 고열이나 다른 심각한 증상이 동반되면 즉시 의료진에게 상담받으세요.",
            "기침": "기침의 원인은 감기, 알레르기, 건조한 공기 등 다양합니다. 충분한 수분 섭취와 가습기 사용이 도움될 수 있으며, 2주 이상 지속되면 의료진 상담을 권합니다.",
            "복통": "복통의 원인은 매우 다양합니다. 가벼운 소화불량일 수도 있지만, 심한 통증이나 발열, 구토가 동반되면 즉시 응급실을 방문하세요."
        }
        
        response = "현재 AI 모델에 연결할 수 없어 기본 응답을 제공합니다. 정확한 건강 상담은 의료 전문가에게 받으시기 바랍니다."
        
        for keyword, fallback in fallback_responses.items():
            if keyword in user_input:
                response = fallback
                break
        
        return {
            "model_used": "fallback_system",
            "specialty": specialty,
            "prompt_type": "fallback",
            "response": response + "\n\n⚠️ 참고: AI 모델이 연결되지 않아 기본 응답을 제공합니다. 정확한 의료 상담은 전문의에게 받으시기 바랍니다.",
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
            "available_models": ["gpt-4", "gpt-3.5-turbo"] if self.available else [],
            "model_specialties": {
                name: {
                    "specialty": info.specialty,
                    "description": info.description,
                    "available": self.available
                }
                for name, info in self.model_specs.items()
            },
            "server_status": "connected" if self.available else "disconnected",
            "api_available": self.available
        }

# OpenAI 클라이언트 인스턴스
openai_health_client = OpenAIHealthClient()