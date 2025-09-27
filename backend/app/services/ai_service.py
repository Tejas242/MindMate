import openai
from typing import List, Dict, Optional, Tuple
from app.core.config import settings
import re
import json


class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        
        self.system_prompt = """You are MindMate, a compassionate AI mental health companion designed specifically for students. 

Your role is to:
- Provide empathetic, non-judgmental support
- Ask gentle probing questions to understand their situation
- Offer evidence-based coping strategies and micro-interventions
- Recognize signs of distress and mental health concerns
- Maintain a warm, student-friendly tone

Guidelines:
- Always prioritize safety and well-being
- Encourage professional help when appropriate
- Use active listening techniques
- Be culturally sensitive and inclusive
- Keep responses conversational and supportive
- Ask follow-up questions to better understand their feelings

IMPORTANT: If you detect any signs of self-harm, suicide ideation, or crisis situations, acknowledge their feelings and strongly encourage them to reach out to a counselor or crisis hotline immediately.

Remember: You are not a replacement for professional mental health care, but a supportive companion for early intervention and ongoing wellness support."""

    async def generate_response(self, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate AI response to user message"""
        
        if not settings.OPENAI_API_KEY:
            return "I'm here to support you, but I need to be properly configured to respond. Please contact your system administrator."
        
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "I'm experiencing some technical difficulties right now. Please try again in a moment, or reach out to a counselor if you need immediate support."

    def detect_crisis_keywords(self, message: str) -> List[str]:
        """Detect crisis-related keywords in the message"""
        detected = []
        message_lower = message.lower()
        
        for keyword in settings.CRISIS_KEYWORDS:
            if keyword in message_lower:
                detected.append(keyword)
        
        return detected

    def assess_message_risk(self, message: str, conversation_history: List[str] = None) -> Dict:
        """Assess risk level of a message using rule-based approach"""
        
        message_lower = message.lower()
        risk_factors = {}
        
        # Crisis indicators
        crisis_keywords = self.detect_crisis_keywords(message)
        if crisis_keywords:
            risk_factors['crisis_keywords'] = crisis_keywords
        
        # Depression indicators
        depression_terms = ['depressed', 'sad', 'hopeless', 'worthless', 'empty', 'numb', 'tired', 'exhausted']
        depression_score = sum(1 for term in depression_terms if term in message_lower) / len(depression_terms)
        
        # Anxiety indicators
        anxiety_terms = ['anxious', 'worried', 'panic', 'stressed', 'overwhelmed', 'nervous', 'afraid', 'scared']
        anxiety_score = sum(1 for term in anxiety_terms if term in message_lower) / len(anxiety_terms)
        
        # Self-harm indicators
        self_harm_terms = ['hurt myself', 'self harm', 'cutting', 'burning', 'scratching']
        self_harm_score = sum(1 for term in self_harm_terms if term in message_lower) / len(self_harm_terms)
        
        # Suicide risk indicators
        suicide_terms = ['suicide', 'kill myself', 'end it', 'want to die', 'better off dead']
        suicide_score = sum(1 for term in suicide_terms if term in message_lower) / len(suicide_terms)
        
        # Calculate overall risk
        overall_risk = max(
            depression_score * 0.4,
            anxiety_score * 0.3,
            self_harm_score * 0.8,
            suicide_score * 1.0
        )
        
        # Crisis override
        if crisis_keywords:
            overall_risk = max(overall_risk, 0.9)
        
        # Determine risk level
        if overall_risk >= 0.8:
            risk_level = "crisis"
        elif overall_risk >= settings.HIGH_RISK_THRESHOLD:
            risk_level = "high"
        elif overall_risk >= settings.MEDIUM_RISK_THRESHOLD:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "depression_score": depression_score,
            "anxiety_score": anxiety_score,
            "self_harm_score": self_harm_score,
            "suicide_risk_score": suicide_score,
            "risk_factors": risk_factors,
            "explanation": f"Risk assessment based on detected indicators. Primary concern: {risk_level} risk level.",
            "confidence_level": 0.7  # Rule-based system confidence
        }

    def filter_response_safety(self, response: str) -> Tuple[str, bool]:
        """Apply safety filtering to AI responses"""
        
        # Check for harmful content patterns
        harmful_patterns = [
            r'kill yourself',
            r'you should die',
            r'end your life',
            r'methods? to (harm|hurt)',
            r'how to (hurt|harm) yourself'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response.lower()):
                return (
                    "I understand you're going through a difficult time. Please reach out to a counselor or mental health professional who can provide the support you need. If this is an emergency, please contact your local crisis hotline immediately.",
                    True
                )
        
        return response, False


# Global AI service instance
ai_service = AIService()