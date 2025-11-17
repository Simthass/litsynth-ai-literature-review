"""
Simplified observability for LitSynth
"""

import logging

def setup_logging():
    """Setup comprehensive logging for the agent system"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('litsynth.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('LitSynth')

def create_observability_plugin():
    """Create a simple observability setup"""
    logger = setup_logging()
    logger.info("Observability initialized")
    return None  # Return None since we're using basic logging

# Global logger instance
logger = setup_logging()