import time
import logging
import psycopg2.extras
from app.database import get_db
from app.agents.content.script_generator import ScriptGeneratorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoWorker:
    def __init__(self):
        self.script_gen = ScriptGeneratorAgent()
        self.running = True
    
    def run(self):
        logger.info("Video Worker started")
        
        while self.running:
            try:
                job = self._get_next_job()
                
                if job:
                    logger.info(f"Processing job {job['id']}: {job['topic']}")
                    self._process_job(job)
                else:
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(10)
    
    def _get_next_job(self):
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM generation_queue
            WHERE status = 'queued'
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
        """)
        
        job = cursor.fetchone()
        
        if job:
            cursor.execute("""
                UPDATE generation_queue
                SET status = 'processing', started_at = NOW()
                WHERE id = %s
            """, (job['id'],))
            db.commit()
        
        cursor.close()
        return dict(job) if job else None
    
    def _process_job(self, job: dict):
        try:
            script_result = self.script_gen.execute(
                topic=job['topic'],
                brand_id=job['brand_id']
            )
            
            if not script_result['success']:
                raise Exception(f"Script failed: {script_result['error']}")
            
            video_id = self._create_video(job, script_result['data'])
            self._complete_job(job['id'], video_id)
            
            logger.info(f"Job {job['id']} completed - Video {video_id}")
            
        except Exception as e:
            logger.error(f"Job {job['id']} failed: {e}")
            self._fail_job(job['id'], str(e))
    
    def _create_video(self, job: dict, script: dict) -> int:
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            INSERT INTO videos (brand_id, title, platform, status, topic, script)
            VALUES (%s, %s, %s, 'completed', %s, %s)
            RETURNING id
        """, (job['brand_id'], job['topic'][:100], job['platform'],
              job['topic'], script['full_script']))
        
        video_id = cursor.fetchone()['id']
        db.commit()
        cursor.close()
        return video_id
    
    def _complete_job(self, job_id: int, video_id: int):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE generation_queue
            SET status = 'completed', completed_at = NOW(), video_id = %s
            WHERE id = %s
        """, (video_id, job_id))
        db.commit()
        cursor.close()
    
    def _fail_job(self, job_id: int, error: str):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE generation_queue
            SET status = 'failed', error_message = %s
            WHERE id = %s
        """, (error, job_id))
        db.commit()
        cursor.close()

if __name__ == '__main__':
    worker = VideoWorker()
    worker.run()
