import os
import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def generate_report(self, idea: str, abstract: str, research_data: List[Dict[str, Any]]) -> str:
        if not self.model:
            return "AI Service unavailable: No API Key provided."

        # Prepare context from research data
        context = "Reference Papers:\n"
        for i, paper in enumerate(research_data, 1):
            context += f"{i}. {paper['title']} - {paper['abstract'][:300]}...\n"

        prompt = f"""
        You are an academic research assistant. Analyze the following research idea based on the provided existing literature.
        
        User Idea: {idea}
        User Abstract: {abstract}
        
        {context}
        
        Generate a structured 'AI Research Analysis Report' with the following sections:
        1. Overview of Existing Work
        2. Key Techniques and Technologies
        3. Current Limitations
        4. Research Gaps
        5. Suggested Improvements
        6. Future Research Scope
        7. Key References
        
        Format output as Markdown.
        """

        try:
            # Gemini calls are synchronous by default in the python client, 
            # but usually fast. For true async, we'd run in executor, 
            # but for MVP this is fine or we can use the async method if available in newer versions.
            # safe approach:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating report: {e}"

    async def chat(self, history: List[Dict[str, str]], context: str) -> str:
        if not self.model:
            return "AI Service unavailable."
            
        # Convert history to Gemini format if possible, or just append to prompt for simplicity
        # Gemini format: role='user'|'model'
        # History is [{'role': 'user'|'ai', 'content': '...'}]
        
        gemini_history = []
        # Add system context as first message from user (hacky but works for context) or strict system instruction
        # Gemini 1.5 supports system instructions in model init, but we want dynamic context.
        # We will prepend context to the latest message or history.
        
        for msg in history[-10:]: # limit context
            role = 'user' if msg['role'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [msg['content']]})

        try:
            chat = self.model.start_chat(history=gemini_history)
            
            # Add context to the latest prompt
            latest_prompt = f"Context: {context}\n\nAnswer the user based on this context if relevant."
            
            response = chat.send_message(latest_prompt)
            return response.text
        except Exception as e:
            return f"Error in chat: {e}"

ai_service = AIService()
