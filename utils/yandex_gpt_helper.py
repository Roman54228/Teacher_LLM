import os
import json
import requests
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import config

def get_ai_explanation(question, options, correct_answer):
    """
    Get AI explanation for a question using YandexGPT
    """
    try:
        YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
        YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "b1gd0b1ls413o390fmqk")
        
        if not YANDEX_API_KEY:
            return "YandexGPT API key not found. Please set the YANDEX_API_KEY environment variable."
        
        prompt_text = f"""Объясни этот вопрос простыми словами, как будто рассказываешь другу:

Вопрос: {question}
Варианты: {', '.join(options)}
Правильный ответ: {correct_answer}

НЕ используй формальную структуру с пронумерованными пунктами! 
НЕ начинай с "Чёткое определение" или "Ключевые принципы".

Просто объясни понятно и интересно. Можешь привести пример из реальной практики или проекта. 
Пиши естественно, как опытный программист, который делится знаниями."""

        payload = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты опытный программист-наставник. Говори простым языком, избегай официальности. НЕ используй пронумерованные списки. Рассказывай как друг, который объясняет сложные вещи понятно и интересно."
                },
                {
                    "role": "user",
                    "text": prompt_text
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {YANDEX_API_KEY}"
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'alternatives' in result['result']:
                return result['result']['alternatives'][0]['message']['text']
            else:
                return "Ошибка: неожиданный формат ответа от YandexGPT."
        else:
            return f"Ошибка API YandexGPT: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"Ошибка при получении объяснения ИИ: {str(e)}"

def get_personalized_recommendations(user_progress, weak_areas):
    """
    Get personalized study recommendations based on user performance using YandexGPT
    """
    try:
        YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
        YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "b1gd0b1ls413o390fmqk")
        
        if not YANDEX_API_KEY:
            return "YandexGPT API key not found. Please set the YANDEX_API_KEY environment variable."
        
        prompt_text = f"""На основе следующих данных о производительности пользователя предоставьте персонализированные рекомендации по обучению:

Прогресс пользователя: {user_progress}
Слабые области: {weak_areas}

Пожалуйста, предоставьте:
1. Конкретные темы для изучения
2. Рекомендуемые учебные ресурсы
3. Стратегии практики
4. График улучшений

Сформулируйте ответ как практические рекомендации для подготовки к собеседованию."""

        payload = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": "1500"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты карьерный коуч, специализирующийся на подготовке к техническим собеседованиям. Предоставляй практические, действенные советы."
                },
                {
                    "role": "user",
                    "text": prompt_text
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {YANDEX_API_KEY}"
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'alternatives' in result['result']:
                return result['result']['alternatives'][0]['message']['text']
            else:
                return "Ошибка: неожиданный формат ответа от YandexGPT."
        else:
            return f"Ошибка API YandexGPT: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"Ошибка при получении рекомендаций: {str(e)}"

def explain_concept(concept, context="general"):
    """
    Get detailed explanation of a technical concept using YandexGPT
    """
    try:
        YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
        YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "b1gd0b1ls413o390fmqk")
        
        if not YANDEX_API_KEY:
            return "YandexGPT API key not found. Please set the YANDEX_API_KEY environment variable."
        
        prompt_text = f"""Пожалуйста, объясните концепцию: {concept}

Контекст: {context}

Предоставьте:
1. Четкое определение
2. Ключевые принципы
3. Практические примеры
4. Общие вопросы собеседования по этой теме
5. Как это связано с другими концепциями

Сделайте объяснение подходящим для подготовки к техническому собеседованию."""

        payload = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты технический эксперт, который объясняет сложные концепции доступным способом для подготовки к собеседованию."
                },
                {
                    "role": "user",
                    "text": prompt_text
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {YANDEX_API_KEY}"
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'alternatives' in result['result']:
                return result['result']['alternatives'][0]['message']['text']
            else:
                return "Ошибка: неожиданный формат ответа от YandexGPT."
        else:
            return f"Ошибка API YandexGPT: {response.status_code} - {response.text}"
        
    except Exception as e:
        return f"Ошибка при объяснении концепции: {str(e)}"


class YandexGPTHelper:
    """
    Helper class for YandexGPT API integration
    """
    
    def __init__(self):
        self.api_key = os.environ.get("YANDEX_API_KEY")
        self.folder_id = os.environ.get("YANDEX_FOLDER_ID", "b1gd0b1ls413o390fmqk")
        
        if not self.api_key:
            raise Exception("YANDEX_API_KEY not found in environment variables")
    
    def get_explanation(self, message, context=None):
        """
        Get explanation for a question or concept
        """
        try:
            if context:
                prompt = f"Контекст: {context}\n\nВопрос: {message}\n\nДай подробное объяснение простыми словами."
            else:
                prompt = message
                
            return self._make_request(prompt)
            
        except Exception as e:
            return f"Ошибка при получении объяснения: {str(e)}"
    
    def get_recommendations(self, user_progress, weak_areas):
        """
        Get personalized recommendations
        """
        return get_personalized_recommendations(user_progress, weak_areas)
    
    def _make_request(self, prompt):
        """
        Make request to YandexGPT API
        """
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты помощник для изучения программирования. Объясняй понятно и дружелюбно."
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result and 'alternatives' in result['result']:
                return result['result']['alternatives'][0]['message']['text']
            else:
                return "Ошибка: неожиданный формат ответа от YandexGPT."
        else:
            return f"Ошибка API YandexGPT: {response.status_code} - {response.text}"