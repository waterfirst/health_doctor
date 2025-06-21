"""
Ollama 클라이언트 - 다중 LLM 모델 관리
"""

import ollama
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
import asyncio

@dataclass
class ModelInfo:
    """모델 정보 클래스"""
    name: str
    size: str
    specialty: str  # 각 모델의 특화 분야
    description: str

class OllamaHealthClient:
    """건강 상담을 위한 Ollama 클라이언트"""
    
    def __init__(self):
        self.client = ollama.Client()
        self.available_models = self._get_available_models()
        self.model_specs = self._define_model_specialties()
        
    def _get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 조회"""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            logger.error(f"모델 목록 조회 실패: {e}")
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
        """건강 조언 요청"""
        
        # 특화 분야에 맞는 모델 선택
        model_name = self.get_model_by_specialty(specialty)
        if not model_name:
            model_name = self.available_models[0] if self.available_models else None
            
        if not model_name:
            return {
                "error": "사용 가능한 모델이 없습니다",
                "model_used": None,
                "response": None
            }
        
        # 프롬프트 타입 결정
        prompt_type = self._determine_prompt_type(user_input)
        prompt = self.create_health_prompt(user_input, context, prompt_type)
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            return {
                "model_used": model_name,
                "specialty": specialty,
                "prompt_type": prompt_type,
                "response": response['message']['content'],
                "error": None
            }
            
        except Exception as e:
            logger.error(f"모델 응답 생성 실패: {e}")
            return {
                "error": f"모델 응답 실패: {str(e)}",
                "model_used": model_name,
                "response": None
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
            }
        }

# 전역 클라이언트 인스턴스
health_client = OllamaHealthClient()