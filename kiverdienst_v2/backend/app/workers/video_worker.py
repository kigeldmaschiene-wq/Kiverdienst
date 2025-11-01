"""
Video Generation Background Worker
Processes generation queue in background
"""
import time
import logging
import asyncio
from app.database import get_pool
from app.agents.content.script_generator import ScriptGeneratorAgent
from app.agents.video.video_renderer import VideoRendererAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoWorker:
    """
    Background worker for video generation
    
    Process:
    1. Get next job from queue (FIFO with priority)
    2. Generate script
    3. Generate voice-over (TODO: Azure TTS)
    4. Select clips (TODO: Clip Selector Agent)
    5. Render video
    6. Mark job complete
    """
    
    def __init__(self):
        self.script_gen = ScriptGeneratorAgent()
        self.renderer = VideoRendererAgent()
        self.running = True
    
    async def run(self):
        """Main worker loop"""
        logger.info("?? Video Worker started")
        logger.info("Server: 135.181.129.240")
        logger.info("Polling interval: 5 seconds")
        
        while self.running:
            try:
                # Get next job from queue
                job = await self._get_next_job()
                
                if job:
                    logger.info(f"?? Processing job {job['id']}: {job['topic']}")
                    await self._process_job(job)
                else:
                    # No jobs, sleep
                    await asyncio.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("??  Worker stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"? Worker error: {e}")
                await asyncio.sleep(10)
    
    async def _get_next_job(self):
        """Get next job from generation_queue"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            job = await conn.fetchrow("""
                SELECT * FROM generation_queue
                WHERE status = 'queued'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """)
            
            if job:
                # Mark as processing
                await conn.execute("""
                    UPDATE generation_queue
                    SET status = 'processing', started_at = NOW()
                    WHERE id = $1
                """, job['id'])
            
            return dict(job) if job else None
    
    async def _process_job(self, job: dict):
        """Process a generation job"""
        try:
            # 1. Generate script
            logger.info(f"  ?? Generating script...")
            script_result = await self.script_gen.execute(
                topic=job['topic'],
                brand_id=job['brand_id'],
                context={'platform': job['platform']}
            )
            
            if not script_result['success']:
                raise Exception(f"Script generation failed: {script_result['error']}")
            
            script = script_result['data']
            logger.info(f"  ? Script generated (quality: {script.get('quality_score', 0)}/100)")
            
            # 2. Create video entry
            video_id = await self._create_video(job, script)
            logger.info(f"  ?? Video entry created: {video_id}")
            
            # 3. Mark job complete (skip video rendering for now)
            await self._complete_job(job['id'], video_id)
            
            logger.info(f"? Job {job['id']} completed successfully ? Video {video_id}")
            
        except Exception as e:
            logger.error(f"? Job {job['id']} failed: {e}")
            await self._fail_job(job['id'], str(e))
    
    async def _create_video(self, job: dict, script: dict) -> int:
        """Create video entry in database"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO videos 
                (brand_id, character_id, title, platform, status, 
                 topic, script, hook, cta, quality_score, generation_started_at)
                VALUES ($1, $2, $3, $4, 'generating', $5, $6, $7, $8, $9, NOW())
                RETURNING id
            """,
                job['brand_id'],
                job.get('character_id'),
                job['topic'][:100],
                job['platform'],
                job['topic'],
                script['full_script'],
                script['hook'],
                script['cta'],
                script.get('quality_score', 0)
            )
            
            return result['id']
    
    async def _complete_job(self, job_id: int, video_id: int):
        """Mark job as completed"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE generation_queue
                SET status = 'completed', completed_at = NOW(), video_id = $1
                WHERE id = $2
            """, video_id, job_id)
            
            # Also update video status
            await conn.execute("""
                UPDATE videos
                SET status = 'completed', generation_completed_at = NOW()
                WHERE id = $1
            """, video_id)
    
    async def _fail_job(self, job_id: int, error: str):
        """Handle job failure with retry logic"""
        pool = await get_pool()
        
        async with pool.acquire() as conn:
            # Get current retry count
            job = await conn.fetchrow(
                "SELECT retry_count, max_retries FROM generation_queue WHERE id = $1",
                job_id
            )
            
            if job and job['retry_count'] < job['max_retries']:
                # Retry
                logger.info(f"  ?? Retry {job['retry_count'] + 1}/{job['max_retries']}")
                await conn.execute("""
                    UPDATE generation_queue
                    SET status = 'queued', 
                        retry_count = retry_count + 1, 
                        error_message = $1
                    WHERE id = $2
                """, error, job_id)
            else:
                # Max retries reached - permanent failure
                logger.error(f"  ? Max retries reached - permanent failure")
                await conn.execute("""
                    UPDATE generation_queue
                    SET status = 'failed', error_message = $1
                    WHERE id = $2
                """, error, job_id)

async def main():
    worker = VideoWorker()
    await worker.run()

if __name__ == '__main__':
    asyncio.run(main())
