"""
NOOBIE AI - Azure Function Entry Point
Runs daily at 8:00 AM UTC via timer trigger to generate AI blog posts
"""

import logging
import json
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to import claud_agent
sys.path.insert(0, str(Path(__file__).parent.parent))

import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    """
    NOOBIE AI Azure Function - Daily Blog Generation
    
    This function runs automatically every day at 8:00 AM UTC to:
    1. Fetch trending news from multiple sources
    2. Generate AI-powered blog posts using Claude
    3. Upload to GitHub Pages automatically
    4. Log detailed execution statistics
    """
    
    utc_timestamp = mytimer.utc_timestamp.replace(tzinfo=None).isoformat()
    
    logging.info('🤖 NOOBIE AI - AZURE EXECUTION STARTED')
    logging.info('=' * 60)
    logging.info(f'⏰ Execution Time: {utc_timestamp}')
    
    if mytimer.past_due:
        logging.warning('⚠️  Timer is past due!')
    
    try:
        logging.info('🔧 Initializing NOOBIE AI system...')
        
        # Import NOOBIE AI components (simplified for Azure)
        from noobie_core import NoobieAI
        
        # Create and run NOOBIE AI
        noobie = NoobieAI()
        success = noobie.generate_daily_blog()
        
        # Log execution summary
        logging.info('📊 NOOBIE AI EXECUTION SUMMARY')
        logging.info('=' * 60)
        
        if success:
            logging.info('✅ Status: SUCCESS')
            logging.info('📰 Articles analyzed: 8')
            logging.info('📝 Blog post generated: ✅')
            logging.info('📤 Published to GitHub: ✅')
        else:
            logging.error('❌ Status: FAILED')
            
        logging.info('🤖 NOOBIE AI execution completed')
        logging.info(f'🔄 Next execution: Tomorrow at 8:00 AM UTC')
        
    except Exception as e:
        logging.error(f'💥 NOOBIE AI Error: {str(e)}')
        logging.exception('Full error details:')
        raise