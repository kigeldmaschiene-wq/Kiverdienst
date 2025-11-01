from .base_agent import BaseAgent
from ..utils.ollama_client import OllamaClient
from typing import Dict, Any, List

class CommentTriggerAgent(BaseAgent):
    """Auto-reply to comments with engagement triggers"""
    
    def __init__(self):
        super().__init__("CommentTrigger")
        self.ollama = OllamaClient()
    
    async def _execute(self, task_data: Dict[str, Any]) -> Any:
        video_id = task_data.get("video_id")
        comments = task_data.get("comments", [])
        brand_id = task_data.get("brand_id")
        
        self.logger.info(f"Processing {len(comments)} comments for video {video_id}")
        
        # Analyze and respond to comments
        responses = []
        for comment in comments:
            response = await self._process_comment(comment, brand_id)
            if response:
                responses.append(response)
        
        return {
            "video_id": video_id,
            "comments_processed": len(comments),
            "responses_generated": len(responses),
            "responses": responses
        }
    
    async def _process_comment(self, comment: Dict, brand_id: int) -> Dict:
        """Process single comment and generate response"""
        comment_text = comment.get("text", "")
        commenter = comment.get("username", "")
        
        # Detect comment type
        comment_type = self._detect_comment_type(comment_text)
        
        # Check if should respond
        if not self._should_respond(comment_type):
            return None
        
        # Generate appropriate response
        response_text = await self._generate_response(comment_text, comment_type, brand_id)
        
        return {
            "comment_id": comment.get("id"),
            "commenter": commenter,
            "original_comment": comment_text,
            "response": response_text,
            "comment_type": comment_type,
            "priority": self._get_priority(comment_type)
        }
    
    def _detect_comment_type(self, text: str) -> str:
        """Detect type of comment"""
        text_lower = text.lower()
        
        # Question
        if "?" in text or any(q in text_lower for q in ["wie", "was", "wo", "wann", "warum"]):
            return "question"
        
        # Negative
        if any(neg in text_lower for neg in ["schlecht", "fake", "scam", "betrug", "nicht gut"]):
            return "negative"
        
        # Positive
        if any(pos in text_lower for pos in ["danke", "super", "toll", "genial", "hilft", "??", "??"]):
            return "positive"
        
        # Interest/engagement
        if any(eng in text_lower for eng in ["link", "wo", "wie", "mehr", "info", "lernen"]):
            return "interest"
        
        return "general"
    
    def _should_respond(self, comment_type: str) -> bool:
        """Determine if comment should get response"""
        # Always respond to questions, interest, and negative comments
        respond_to = ["question", "interest", "negative", "positive"]
        return comment_type in respond_to
    
    async def _generate_response(self, comment: str, comment_type: str, brand_id: int) -> str:
        """Generate appropriate response"""
        # Template-based responses for quick replies
        templates = {
            "question": [
                "Gute Frage! Check den Link in meiner Bio f?r mehr Infos! ??",
                "Hab ich im Detail in meinem neuesten Video erkl?rt - schau mal rein! ??",
                "Folge mir f?r mehr zu diesem Thema! ??"
            ],
            "interest": [
                "Alle Infos findest du im Link in meiner Bio! ??",
                "Schreib mir eine DM - ich helfe dir gerne! ??",
                "Bleib dran - n?chstes Video kommt bald! ??"
            ],
            "positive": [
                "Danke dir! ?? Folge f?r mehr Content!",
                "Freut mich dass es hilft! ?? Mehr kommt bald!",
                "Du bist der Beste! ?? Teile das Video gerne!"
            ],
            "negative": [
                "Sorry dass du so f?hlst! Schreib mir eine DM und wir kl?ren das! ??",
                "Ich verstehe deine Bedenken. Lass uns dar?ber reden! ??",
                "Danke f?r dein Feedback! Wie kann ich es besser machen?"
            ],
            "general": [
                "Danke f?r deinen Kommentar! ??",
                "Folge f?r mehr Content! ??",
                "Schau dir auch meine anderen Videos an! ??"
            ]
        }
        
        import random
        template_responses = templates.get(comment_type, templates["general"])
        
        # For important comments, use AI to generate personalized response
        if comment_type in ["question", "negative"]:
            try:
                prompt = f"""Generate a short, friendly German reply to this comment: "{comment}"
                Keep it under 50 characters, include emoji, be helpful."""
                
                ai_response = await self.ollama.generate(prompt, use_large=False, temperature=0.7)
                return ai_response.strip()[:200]  # Limit length
            except:
                pass
        
        # Fallback to template
        return random.choice(template_responses)
    
    def _get_priority(self, comment_type: str) -> str:
        """Get response priority"""
        if comment_type in ["negative", "question"]:
            return "high"
        elif comment_type == "interest":
            return "medium"
        else:
            return "low"
