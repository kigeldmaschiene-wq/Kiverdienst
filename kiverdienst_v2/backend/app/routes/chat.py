# -*- coding: utf-8 -*-
"""Mastermind Chat API Routes - MISSING ROUTE #4"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.database import get_pool

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    role: str
    message: str
    timestamp: str

@router.post("/chat")
async def mastermind_chat(msg: ChatMessage):
    """Chat with Mastermind AI"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Save user message
        await conn.execute("""
            INSERT INTO chat_history (role, message)
            VALUES ('user', $1)
        """, msg.message)
        
        # Generate AI response (placeholder - in production would call Ollama)
        ai_response = f"Ich habe deine Nachricht verstanden: '{msg.message}'. "
        
        # Context-aware responses
        if "performance" in msg.message.lower() or "analyse" in msg.message.lower():
            stats = await conn.fetchrow("""
                SELECT COUNT(*) as brands, 
                       (SELECT COUNT(*) FROM videos) as videos,
                       (SELECT COALESCE(SUM(views), 0) FROM videos) as views
                FROM brands
            """)
            ai_response = f"?? Performance-Analyse:\n\n"
            ai_response += f"? {stats['brands']} aktive Marken\n"
            ai_response += f"? {stats['videos']} generierte Videos\n"
            ai_response += f"? {stats['views']:,} Gesamt-Views\n\n"
            ai_response += "Die Performance entwickelt sich gut. Empfehlung: Fokus auf Top-performing Nischen."
        
        elif "ideen" in msg.message.lower() or "themen" in msg.message.lower():
            ai_response = "?? Content-Ideen f?r deine Marken:\n\n"
            ai_response += "1. Top 5 KI-Tools f?r Content Creator\n"
            ai_response += "2. Passive Income Strategien 2025\n"
            ai_response += "3. 30-Tage Fitness Challenge\n"
            ai_response += "4. Hidden Travel Gems in Europa\n"
            ai_response += "5. TikTok Algorithm Hacks\n"
        
        elif "strategie" in msg.message.lower():
            ai_response = "?? Content-Strategie Empfehlungen:\n\n"
            ai_response += "? Posting-Frequenz: 2-3x t?glich zu Peak-Zeiten\n"
            ai_response += "? Best Times: 12:00, 18:00, 21:00 Uhr\n"
            ai_response += "? Fokus auf Trending Topics\n"
            ai_response += "? Cross-Posting auf allen Plattformen\n"
        
        else:
            ai_response += "Wie kann ich dir bei deinem Content-Business helfen? Ich kann dir mit Performance-Analysen, Content-Ideen, Strategien und mehr helfen."
        
        # Save AI response
        await conn.execute("""
            INSERT INTO chat_history (role, message)
            VALUES ('assistant', $1)
        """, ai_response)
        
        return {
            "role": "assistant",
            "message": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/suggestions")
async def get_suggestions():
    """Get AI suggestions"""
    return [
        "Analysiere die Performance meiner Top 5 Videos",
        "Generiere 10 neue Content-Ideen f?r TechSnap",
        "Erstelle einen optimalen Posting-Plan f?r diese Woche",
        "Welche Nische hat das gr??te Potenzial?",
        "Wie kann ich meine Engagement-Rate verbessern?"
    ]

@router.get("/history")
async def get_chat_history(limit: int = 50):
    """Get chat history"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM chat_history 
            ORDER BY timestamp DESC 
            LIMIT $1
        """, limit)
        return [dict(row) for row in reversed(rows)]
