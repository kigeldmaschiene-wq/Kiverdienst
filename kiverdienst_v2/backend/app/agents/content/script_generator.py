"""
Script Generator Agent
Uses Llama 3.1 8B for fast script generation
Optimized for TikTok/Instagram viral content
"""
import json
from typing import Dict
from app.agents.base_agent import BaseAgent
from app.agents.utils.ollama_client import OllamaClient
from app.database import get_pool

class ScriptGeneratorAgent(BaseAgent):
    """
    Generates video scripts optimized for TikTok/Instagram
    
    Structure: Hook ? Problem ? Story/Solution ? CTA
    All scripts scored 0-100 for quality
    """
    
    def __init__(self):
        super().__init__(
            name="ScriptGenerator",
            description="Video script generation using Llama 8B"
        )
        self.ollama = OllamaClient(model="llama3.1:8b")
    
    async def execute(self, topic: str, brand_id: int, context: Dict = None) -> Dict:
        """
        Generate video script
        
        Args:
            topic: Video topic
            brand_id: Brand ID
            context: Additional context (platform, duration, etc.)
        
        Returns:
            Dict with success status and script data
        """
        context = context or {}
        
        with self.measure_time() as timer:
            try:
                # Get brand info
                brand = await self._get_brand(brand_id)
                if not brand:
                    raise ValueError(f"Brand {brand_id} not found")
                
                # Build prompt
                prompt = self._build_prompt(topic, brand, context)
                
                # Generate with Ollama
                response = self.ollama.generate(prompt, temperature=0.8)
                
                # Parse JSON
                script_data = self._extract_json(response)
                
                # Validate
                if not self._validate_script(script_data):
                    raise ValueError("Invalid script format - missing required fields")
                
                # Calculate quality scores
                scores = self._calculate_scores(script_data)
                script_data.update(scores)
                
                # Save to database
                script_id = await self._save_script(script_data, brand_id)
                script_data['id'] = script_id
                
                # Log success
                await self.log_action(
                    action="generate_script",
                    status="success",
                    message=f"Script generated for topic: {topic}",
                    details={"script_id": script_id, "scores": scores},
                    duration_ms=timer.duration_ms,
                    brand_id=brand_id
                )
                
                return {'success': True, 'data': script_data}
                
            except Exception as e:
                self.logger.error(f"Script generation failed: {e}")
                
                await self.log_action(
                    action="generate_script",
                    status="failed",
                    message=str(e),
                    details={"topic": topic},
                    duration_ms=timer.duration_ms,
                    brand_id=brand_id
                )
                
                return {'success': False, 'error': str(e)}
    
    def _build_prompt(self, topic: str, brand: Dict, context: Dict) -> str:
        """Build optimized prompt for script generation"""
        
        platform = context.get('platform', 'tiktok')
        target_duration = context.get('duration', 60)
        word_count_target = int(target_duration * 2.3)  # ~2.3 words per second
        
        return f"""
You are a viral TikTok/Instagram content scriptwriter.

Brand: {brand.get('name', '')}
Niche: {brand.get('niche', '')}
Tone: Engaging and authentic
Target Audience: 18-35 years old

Topic: {topic}
Platform: {platform}
Target Duration: {target_duration} seconds (~{word_count_target} words)

Task: Write a highly engaging script following this EXACT structure:

1. HOOK (1-3 seconds, 3-7 words):
   - Shocking statement OR intriguing question
   - Create curiosity gap
   - Promise value/result
   Examples: "This makes $500/day", "Stop wasting time on..."

2. PROBLEM (3-5 seconds, 7-12 words):
   - Address audience pain point
   - Create FOMO or frustration
   Example: "You're losing money because you don't know this..."

3. STORY/SOLUTION (40-50 seconds, 90-115 words):
   - Visual demonstration (describe what to show)
   - Step-by-step OR before/after
   - Include specific numbers/results
   - Keep sentences short (5-8 words max)
   - Fast-paced, energetic

4. CTA (5-7 seconds, 10-15 words):
   - Clear action ("Comment X", "Link in bio")
   - Create urgency or offer value
   Example: "Comment TOOL for the full guide"

Output as JSON:
{{
    "hook": "...",
    "problem": "...",
    "story": "...",
    "cta": "...",
    "full_script": "...",
    "visual_notes": ["Scene 1: Show X", "Scene 2: Demo Y"],
    "topic": "{topic}",
    "estimated_duration": {target_duration}
}}

CRITICAL RULES:
- NEVER exceed {target_duration + 10} seconds
- Hook MUST be <7 words
- Use active voice, present tense
- Include 1-2 numbers/stats in story
- No fluff, every word counts
- CTA must be crystal clear
"""
    
    def _extract_json(self, response: str) -> Dict:
        """Extract JSON from Ollama response"""
        try:
            return json.loads(response)
        except:
            pass
        
        # Look for JSON between ```json and ```
        if "```json" in response:
            try:
                start = response.index("```json") + 7
                end = response.index("```", start)
                return json.loads(response[start:end].strip())
            except:
                pass
        
        # Try to find JSON object
        if "{" in response and "}" in response:
            try:
                start = response.index("{")
                end = response.rindex("}") + 1
                return json.loads(response[start:end])
            except:
                pass
        
        raise ValueError("Could not extract JSON from response")
    
    def _validate_script(self, script: Dict) -> bool:
        """Validate script has required fields"""
        required = ['hook', 'problem', 'story', 'cta', 'full_script']
        return all(field in script and script[field] for field in required)
    
    def _calculate_scores(self, script: Dict) -> Dict:
        """
        Calculate quality scores for script
        Returns: {hook_strength, cta_clarity, quality_score}
        """
        scores = {
            'hook_strength': 0,
            'cta_clarity': 0,
            'quality_score': 0
        }
        
        # Hook strength (0-100)
        hook = script['hook']
        hook_words = len(hook.split())
        
        if hook_words <= 7:
            scores['hook_strength'] += 30
        if hook_words <= 5:
            scores['hook_strength'] += 20
        
        # Power words
        power_words = ['shocking', 'secret', 'never', 'mistake', 'truth', 'revealed', 'stop', 'this']
        if any(word in hook.lower() for word in power_words):
            scores['hook_strength'] += 20
        
        # Numbers in hook
        if any(char.isdigit() for char in hook):
            scores['hook_strength'] += 15
        
        # Question mark
        if '?' in hook:
            scores['hook_strength'] += 15
        
        # CTA clarity (0-100)
        cta = script['cta']
        action_words = ['comment', 'click', 'link', 'follow', 'subscribe', 'check', 'save', 'share']
        
        if any(word in cta.lower() for word in action_words):
            scores['cta_clarity'] += 40
        
        if 'bio' in cta.lower() or 'comment' in cta.lower():
            scores['cta_clarity'] += 30
        
        if len(cta.split()) <= 15:
            scores['cta_clarity'] += 30
        
        # Overall quality (0-100)
        word_count = len(script['full_script'].split())
        
        # Target: 120-180 words for 60 second video
        if 100 <= word_count <= 200:
            scores['quality_score'] += 30
        
        # Has visual notes
        if 'visual_notes' in script and len(script.get('visual_notes', [])) >= 3:
            scores['quality_score'] += 20
        
        # Story has numbers/stats
        if any(char.isdigit() for char in script['story']):
            scores['quality_score'] += 25
        
        # Not too long
        if word_count <= 250:
            scores['quality_score'] += 25
        
        return scores
    
    async def _save_script(self, script: Dict, brand_id: int) -> int:
        """Save script to database"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO video_scripts 
                (brand_id, hook, problem, story, cta, full_script, 
                 word_count, estimated_duration, topic, 
                 quality_score, hook_strength, cta_clarity)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
            """,
                brand_id,
                script['hook'],
                script.get('problem', ''),
                script['story'],
                script['cta'],
                script['full_script'],
                len(script['full_script'].split()),
                script.get('estimated_duration', 60),
                script.get('topic', ''),
                script.get('quality_score', 0),
                script.get('hook_strength', 0),
                script.get('cta_clarity', 0)
            )
            
            return result['id']
    
    async def _get_brand(self, brand_id: int) -> Dict:
        """Get brand details"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
            return dict(brand) if brand else {}
